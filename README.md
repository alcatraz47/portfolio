# Zakia Sultana Portfolio (FastAPI + Jinja2 + TailwindCSS)

Single-page portfolio with agency-style layout, server-rendered templates, editable YAML content, optional Instagram integration, and local contact message logging.

## Tech stack
- Backend: Python 3.11+, FastAPI
- Templating: Jinja2
- Styling: TailwindCSS (local build)
- Optional progressive enhancement: HTMX (contact form partial updates)
- Editable content source: `content/content.yaml`

## Project structure
```text
/app
  /static
    /css
    /files
    /js
    /photos
  /templates
    /partials
/content
  content.yaml
/data
  messages.jsonl
/scripts
/tests
```

## Local setup

### 1) Create and activate virtual environment

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows (Command Prompt):
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

### 2) Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3) Install frontend dependencies
```bash
npm install
```

### 4) Optional Instagram env config
```bash
cp .env.example .env
```
Then set `INSTAGRAM_ACCESS_TOKEN` only if you want server-side Graph API fetching.

### 5) Run Tailwind watcher and API server in separate terminals
Terminal A:
```bash
npm run dev:css
```

Terminal B:
```bash
uvicorn app.main:app --reload
```

Open: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Admin-less CMS workflow
1. Edit `content/content.yaml`.
2. Restart the FastAPI server.

No database or admin panel is required.

## Routes
- `/` - single-page portfolio
- `/work/{slug}` - work detail page
- `/download/cv` - serves local PDF from `app/static/files/zakia-sultana-cv.pdf`
- `/contact` - POST endpoint with server-side validation

## Contact form behavior
- Validates `name`, `email`, and `message`.
- Stores entries in `data/messages.jsonl`.
- Logs entries to server console in local dev mode.
- Does **not** send emails.

## Instagram modes (safe fallback built in)
1. Safe default mode (always available):
   - Uses local gallery files from `app/static/photos` and `content/content.yaml`.
2. Optional latest Instagram mode:
   - Mode A (recommended): server-side Graph API fetch using `INSTAGRAM_ACCESS_TOKEN` from `.env`.
   - Mode B (fallback): official embed snippets from `content/content.yaml` (`instagram.embeds`).

If Graph API fails or is not configured, the app automatically falls back to embed mode or local gallery mode without crashing.

## Privacy and security notes
- Public location display is restricted to `Germany & Norway`.
- No secrets are exposed in frontend code.
- Phone exists in YAML but is hidden by default (`site.show_phone: false`).

## Tests
```bash
pytest -q
```

## Replacing CV and photos
- Replace `app/static/files/zakia-sultana-cv.pdf` with the final CV file.
- Replace files in `app/static/photos/` and update paths/captions in `content/content.yaml`.
