from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator

from app.content import DEFAULT_CONTENT_PATH, PROJECT_ROOT, load_content
from app.instagram import resolve_instagram_feed


class ContactSubmission(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    subject: str = Field(default="", max_length=140)
    message: str = Field(min_length=10, max_length=2000)

    @field_validator("name", "subject", "message", mode="before")
    @classmethod
    def normalize_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value


def _resolve_cv_path(content_data: dict[str, Any]) -> Path:
    cv_uri = str(content_data.get("site", {}).get("cv_file", "/static/files/zakia-sultana-cv.pdf"))

    if cv_uri.startswith("/static/"):
        relative_path = cv_uri.removeprefix("/static/")
        return PROJECT_ROOT / "app" / "static" / relative_path

    return PROJECT_ROOT / cv_uri


def _save_message(path: Path, payload: ContactSubmission) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "name": payload.name,
        "email": str(payload.email),
        "subject": payload.subject,
        "message": payload.message,
    }

    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True) + "\n")

    print(f"[contact] {json.dumps(entry, ensure_ascii=True)}")


def create_app(
    *,
    content_file: Path | None = None,
    messages_file: Path | None = None,
) -> FastAPI:
    load_dotenv()

    app = FastAPI(title="Zakia Sultana Portfolio", version="1.0.0")

    templates = Jinja2Templates(directory=str(PROJECT_ROOT / "app" / "templates"))
    static_dir = PROJECT_ROOT / "app" / "static"

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.state.templates = templates
    app.state.content_file = content_file or DEFAULT_CONTENT_PATH
    app.state.messages_file = messages_file or (PROJECT_ROOT / "data" / "messages.jsonl")

    @app.on_event("startup")
    async def ensure_data_store() -> None:
        app.state.messages_file.parent.mkdir(parents=True, exist_ok=True)
        app.state.messages_file.touch(exist_ok=True)

    def _build_contact_feedback(status: str | None) -> dict[str, str] | None:
        if status == "success":
            return {
                "kind": "success",
                "message": "Message received. Thank you, I will respond soon.",
            }
        if status == "error":
            return {
                "kind": "error",
                "message": "Please provide valid name, email, and message (10+ characters).",
            }
        return None

    def _base_context(request: Request, **extra: Any) -> dict[str, Any]:
        content_data = load_content(app.state.content_file)
        context = {
            "request": request,
            "content": content_data,
            "instagram_feed": resolve_instagram_feed(content_data),
            "contact_feedback": _build_contact_feedback(
                request.query_params.get("contact_status")
            ),
        }
        context.update(extra)
        return context

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        return templates.TemplateResponse("index.html", _base_context(request))

    @app.get("/work/{slug}", response_class=HTMLResponse)
    async def work_detail(request: Request, slug: str):
        content_data = load_content(app.state.content_file)
        work_items = content_data.get("selected_work", [])

        selected_item = None
        for item in work_items:
            if item.get("slug") == slug:
                selected_item = item
                break

        if selected_item is None:
            raise HTTPException(status_code=404, detail="Work item not found")

        return templates.TemplateResponse(
            "work_detail.html",
            {
                "request": request,
                "content": content_data,
                "work_item": selected_item,
            },
        )

    @app.get("/download/cv")
    async def download_cv():
        content_data = load_content(app.state.content_file)
        cv_path = _resolve_cv_path(content_data)

        if not cv_path.exists():
            raise HTTPException(status_code=404, detail="CV file not found")

        return FileResponse(
            path=cv_path,
            media_type="application/pdf",
            filename="zakia-sultana-cv.pdf",
        )

    @app.post("/contact", response_model=None)
    async def submit_contact_form(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        subject: str = Form(""),
        message: str = Form(...),
    ):
        is_htmx = request.headers.get("HX-Request") == "true"

        try:
            payload = ContactSubmission(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
        except ValidationError:
            feedback = {
                "kind": "error",
                "message": "Please provide valid name, email, and message (10+ characters).",
            }
            if is_htmx:
                return templates.TemplateResponse(
                    "partials/contact_result.html",
                    {"request": request, "feedback": feedback},
                    status_code=400,
                )
            return RedirectResponse(url="/?contact_status=error#contact", status_code=303)

        _save_message(app.state.messages_file, payload)

        if is_htmx:
            return templates.TemplateResponse(
                "partials/contact_result.html",
                {
                    "request": request,
                    "feedback": {
                        "kind": "success",
                        "message": "Message received. Thank you, I will respond soon.",
                    },
                },
            )

        return RedirectResponse(url="/?contact_status=success#contact", status_code=303)

    return app


app = create_app()
