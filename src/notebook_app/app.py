from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markdown_it import MarkdownIt

from .domain import append_exchange, page_title
from .github import GitHubError, GitHubRepo
from .model import ModelError, OpenAIModel

HERE = Path(__file__).parent
md = MarkdownIt("commonmark", {"html": False, "typographer": True})
templates = Jinja2Templates(directory=HERE / "templates")


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable {name}")
    return value


@asynccontextmanager
async def lifespan(app: FastAPI):
    repo = GitHubRepo(
        token=required_env("GITHUB_TOKEN"),
        repo=required_env("GITHUB_REPO"),
        branch=os.getenv("GITHUB_BRANCH", "main"),
    )
    model_name = os.getenv("OPENAI_MODEL", "").strip()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = OpenAIModel(api_key, model_name) if api_key and model_name else None
    app.state.repo = repo
    app.state.model = model
    yield
    await repo.close()
    if model is not None:
        await model.close()


app = FastAPI(title="Notebook", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")


def repo_for(request: Request) -> GitHubRepo:
    return request.app.state.repo


@app.get("/")
async def home(request: Request):
    try:
        paths = await repo_for(request).markdown_paths()
    except GitHubError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    pages = [{"path": p, "label": p.removesuffix(".md")} for p in paths]
    return templates.TemplateResponse(
        request,
        "home.html",
        {"pages": pages, "repo": repo_for(request).repo},
    )


@app.get("/p/{path:path}")
async def page(request: Request, path: str):
    try:
        item = await repo_for(request).get_page(path)
    except GitHubError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return templates.TemplateResponse(
        request,
        "page.html",
        {
            "repo": repo_for(request).repo,
            "path": path,
            "title": page_title(path, item.content),
            "source": item.content,
            "rendered": md.render(item.content),
            "model_enabled": request.app.state.model is not None,
        },
    )


@app.post("/p/{path:path}/edit")
async def edit_page(request: Request, path: str, source: str = Form(...)):
    repo = repo_for(request)
    try:
        current = await repo.get_page(path)
        await repo.put_page(
            path,
            source,
            message=f"Notebook: edit {page_title(path, source)}",
            sha=current.sha,
        )
    except GitHubError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return RedirectResponse(f"/p/{quote(path, safe='/')}", status_code=303)


@app.post("/p/{path:path}/ask")
async def ask_page(request: Request, path: str, message: str = Form(...)):
    model: OpenAIModel | None = request.app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY and OPENAI_MODEL are not configured")
    repo = repo_for(request)
    try:
        current = await repo.get_page(path)
        instructions = None
        if path != "AGENTS.md":
            try:
                instructions = (await repo.get_page("AGENTS.md")).content
            except GitHubError:
                pass
        answer = await model.reply(
            repo=repo.repo,
            path=path,
            page=current.content,
            user_text=message,
            instructions=instructions,
        )
        author = os.getenv("NOTEBOOK_AUTHOR", "You").strip() or "You"
        updated = append_exchange(current.content, author, message, answer)
        await repo.put_page(
            path,
            updated,
            message=f"Notebook: continue {page_title(path, current.content)}",
            sha=current.sha,
        )
    except (GitHubError, ModelError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return RedirectResponse(f"/p/{quote(path, safe='/')}", status_code=303)
