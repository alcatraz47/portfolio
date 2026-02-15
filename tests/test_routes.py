from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def _make_client(messages_path: Path) -> TestClient:
    app = create_app(
        content_file=Path("content/content.yaml"),
        messages_file=messages_path,
    )
    return TestClient(app)


def test_home_route_renders() -> None:
    messages_file = Path("data/test_messages_home.jsonl")
    with _make_client(messages_file) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Zakia Sultana" in response.text
    assert "Selected Work" in response.text

    if messages_file.exists():
        messages_file.unlink()


def test_work_detail_route_for_known_slug() -> None:
    messages_file = Path("data/test_messages_work.jsonl")
    with _make_client(messages_file) as client:
        response = client.get("/work/embassy-sweden-visa-operations")

    assert response.status_code == 200
    assert "Visa Operations Coordination" in response.text

    if messages_file.exists():
        messages_file.unlink()


def test_work_detail_route_unknown_slug() -> None:
    messages_file = Path("data/test_messages_unknown.jsonl")
    with _make_client(messages_file) as client:
        response = client.get("/work/non-existent-slug")

    assert response.status_code == 404

    if messages_file.exists():
        messages_file.unlink()


def test_contact_submission_redirects_and_persists_message(tmp_path: Path) -> None:
    messages_file = tmp_path / "messages.jsonl"

    with _make_client(messages_file) as client:
        response = client.post(
            "/contact",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Portfolio Inquiry",
                "message": "Hello Zakia, I would like to discuss collaboration opportunities.",
            },
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert "contact_status=success" in response.headers["location"]
    assert messages_file.exists()
    assert "test@example.com" in messages_file.read_text(encoding="utf-8")


def test_invalid_contact_submission_redirects_to_error(tmp_path: Path) -> None:
    messages_file = tmp_path / "messages.jsonl"

    with _make_client(messages_file) as client:
        response = client.post(
            "/contact",
            data={
                "name": "A",
                "email": "invalid",
                "message": "short",
            },
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert "contact_status=error" in response.headers["location"]
