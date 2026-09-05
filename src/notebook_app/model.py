from __future__ import annotations

import httpx


class ModelError(RuntimeError):
    pass


class OpenAIModel:
    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self._client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=120.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def reply(
        self,
        *,
        repo: str,
        path: str,
        page: str,
        user_text: str,
        instructions: str | None = None,
    ) -> str:
        system = (
            "You are collaborating with a human inside a Git-backed notebook. "
            "The notebook page is the foreground intellectual object; repository machinery is secondary. "
            "Respond in useful Markdown. Preserve mathematical notation. Do not invent repository changes "
            "you have not actually made, and do not propose context/handoff/status files merely for agent memory."
        )
        if instructions:
            system += f"\n\nRepository instructions:\n{instructions}"
        prompt = (
            f"Repository: {repo}\n"
            f"Current page: {path}\n\n"
            f"--- CURRENT PAGE ---\n{page}\n--- END PAGE ---\n\n"
            f"Human:\n{user_text}"
        )
        response = await self._client.post(
            "/responses",
            json={
                "model": self.model,
                "instructions": system,
                "input": prompt,
            },
        )
        if not response.is_success:
            raise ModelError(f"OpenAI {response.status_code}: {response.text}")
        data = response.json()
        text = data.get("output_text")
        if isinstance(text, str) and text.strip():
            return text.strip()
        pieces: list[str] = []
        for item in data.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    pieces.append(content["text"])
        if not pieces:
            raise ModelError("OpenAI response contained no output text")
        return "\n\n".join(pieces).strip()
