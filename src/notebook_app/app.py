from __future__ import annotations

import asyncio
import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from markdown_it import MarkdownIt
from pydantic import BaseModel

from .codex import CodexError, CodexModel
from .domain import append_exchange, page_title
from .github import GitHubError, GitHubPage, GitHubRepo
from .model import ModelError, OpenAIModel

HERE = Path(__file__).parent
md = MarkdownIt("commonmark", {"html": False, "typographer": True})


class ContinueRequest(BaseModel):
    path: str
    message: str


class EditRequest(BaseModel):
    path: str
    source: str


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable {name}")
    return value


def build_model() -> tuple[CodexModel | OpenAIModel | None, str]:
    choice = os.getenv("NOTEBOOK_AI", "auto").strip().lower()
    if choice not in {"auto", "codex", "openai", "none"}:
        raise RuntimeError("NOTEBOOK_AI must be auto, codex, openai, or none")

    if choice in {"auto", "codex"} and shutil.which("codex"):
        cwd_value = os.getenv("NOTEBOOK_CODEX_CWD", "").strip()
        cwd = Path(cwd_value).expanduser().resolve() if cwd_value else None
        return CodexModel(cwd=cwd), "Codex · ChatGPT"
    if choice == "codex":
        raise RuntimeError("NOTEBOOK_AI=codex but the codex CLI is not on PATH")

    model_name = os.getenv("OPENAI_MODEL", "").strip()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if choice in {"auto", "openai"} and api_key and model_name:
        return OpenAIModel(api_key, model_name), f"OpenAI API · {model_name}"
    if choice == "openai":
        raise RuntimeError("NOTEBOOK_AI=openai requires OPENAI_API_KEY and OPENAI_MODEL")
    return None, "No AI backend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    repo = GitHubRepo(
        token=required_env("GITHUB_TOKEN"),
        repo=required_env("GITHUB_REPO"),
        branch=os.getenv("GITHUB_BRANCH", "main"),
    )
    model, model_label = build_model()
    app.state.repo = repo
    app.state.model = model
    app.state.model_label = model_label
    yield
    await repo.close()
    if model is not None:
        await model.close()


app = FastAPI(title="Notebook", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")


def repo_for(request: Request) -> GitHubRepo:
    return request.app.state.repo


def model_for(request: Request) -> CodexModel | OpenAIModel | None:
    return request.app.state.model


def page_payload(request: Request, item: GitHubPage) -> dict[str, object]:
    return {
        "repo": repo_for(request).repo,
        "path": item.path,
        "title": page_title(item.path, item.content),
        "source": item.content,
        "rendered": md.render(item.content),
        "aiEnabled": model_for(request) is not None,
        "aiBackend": request.app.state.model_label,
    }


@app.get("/")
async def shell() -> FileResponse:
    return FileResponse(HERE / "static" / "notebook.html")


@app.get("/api/notebook")
async def notebook_snapshot(request: Request):
    repo = repo_for(request)
    try:
        paths = await repo.markdown_paths()

        async def summary(path: str) -> dict[str, str]:
            try:
                item = await repo.get_page(path)
                title = page_title(path, item.content)
            except GitHubError:
                title = path.removesuffix(".md")
            return {"path": path, "title": title}

        pages = await asyncio.gather(*(summary(path) for path in paths[:80]))
    except GitHubError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    preferred = "notebook.md" if "notebook.md" in paths else (paths[0] if paths else None)
    return {
        "repo": repo.repo,
        "pages": pages,
        "defaultPath": preferred,
        "aiEnabled": model_for(request) is not None,
        "aiBackend": request.app.state.model_label,
    }


@app.get("/api/page")
async def api_page(request: Request, path: str = Query(...)):
    try:
        item = await repo_for(request).get_page(path)
    except GitHubError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return page_payload(request, item)


@app.post("/api/edit")
async def api_edit(request: Request, body: EditRequest):
    repo = repo_for(request)
    try:
        current = await repo.get_page(body.path)
        await repo.put_page(
            body.path,
            body.source,
            message=f"Notebook: edit {page_title(body.path, body.source)}",
            sha=current.sha,
        )
        updated = await repo.get_page(body.path)
    except GitHubError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return page_payload(request, updated)


@app.post("/api/continue")
async def api_continue(request: Request, body: ContinueRequest):
    model = model_for(request)
    if model is None:
        raise HTTPException(status_code=503, detail="No Notebook AI backend is configured")
    repo = repo_for(request)
    try:
        current = await repo.get_page(body.path)
        instructions = None
        if body.path != "AGENTS.md":
            try:
                instructions = (await repo.get_page("AGENTS.md")).content
            except GitHubError:
                pass
        answer = await model.reply(
            repo=repo.repo,
            path=body.path,
            page=current.content,
            user_text=body.message,
            instructions=instructions,
        )
        author = os.getenv("NOTEBOOK_AUTHOR", "You").strip() or "You"
        updated_source = append_exchange(current.content, author, body.message, answer)
        await repo.put_page(
            body.path,
            updated_source,
            message=f"Notebook: continue {page_title(body.path, current.content)}",
            sha=current.sha,
        )
        updated = await repo.get_page(body.path)
    except (GitHubError, ModelError, CodexError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    result = page_payload(request, updated)
    result["answer"] = answer
    return result


@app.get("/p/{path:path}")
async def legacy_page(path: str):
    return RedirectResponse(f"/?page={quote(path, safe='')}", status_code=307)
