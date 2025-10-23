# XSELLER.AI Dashboard & Automation (v2.2)

This repository contains the Streamlit operations console, automation pipelines, and service layer for XSELLER.AI. It powers the multi-provider social posting workflow (GetLate, Buffer, Publer), AI news generation pipeline, analytics views, and health monitoring.

## Project Structure

```
xseller-ai/
├─ app/
│  ├─ __init__.py
│  ├─ streamlit_app.py
│  ├─ assets/
│  │  ├─ dashboard_theme.json
│  │  └─ xseller_logo.svg
│  ├─ config/
│  │  └─ channels.json
│  ├─ data/
│  │  ├─ ai_shorts_db.json
│  │  ├─ ai_shorts_queue.json
│  │  ├─ analytics_summary.json
│  │  ├─ hooks_lab.csv
│  │  └─ publish_queue.json
│  ├─ pages/
│  │  ├─ 01_AI_News_Shorts.py
│  │  ├─ 02_Text_Posts.py
│  │  ├─ 03_Social_Posts.py
│  │  ├─ 04_Analytics.py
│  │  ├─ 05_Learning.py
│  │  ├─ 06_Hook_Lab.py
│  │  └─ 07_Settings_Health.py
│  └─ services/
│     ├─ __init__.py
│     ├─ ai_news_service.py
│     ├─ analytics_service.py
│     ├─ buffer_client.py
│     ├─ getlate_client.py
│     ├─ healthcheck.py
│     ├─ publish_service.py
│     └─ publer_client.py
├─ pipelines/
│  ├─ ai-news-shorts.yml
│  └─ run_ai_news.py
├─ xseller_ai/  # legacy automation helpers (RSS fetch, ranking, summarisation)
├─ outputs/
│  └─ … dated video & social assets
└─ requirements.txt
```

## Getting Started

1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Populate environment variables (locally via `.env`, and via GitHub/Streamlit secrets for deployment):
   ```bash
   POST_PROVIDER=getlate  # or buffer / publer
   GETLATE_API_KEY=...
   BUFFER_ACCESS_TOKEN=...
   BUFFER_PROFILE_ID=...
   PUBLER_API_KEY=...
   PUBLER_WORKSPACE_ID=...
   OPENAI_API_KEY=...
   ELEVENLABS_API_KEY=...
   ```
3. Run the automation pipeline locally (optional):
   ```bash
   python pipelines/run_ai_news.py
   ```
   This refreshes `app/data/ai_shorts_queue.json` and writes assets under `outputs/YYYY-MM-DD/`.
4. Launch the dashboard:
   ```bash
   streamlit run app/streamlit_app.py
   ```

## Streamlit Pages

- **Home** (`streamlit_app.py`): high-level KPI cards, signals, and charts.
- **01 – AI News Shorts**: queue review, preview, and exports.
- **02 – Text Posts**: ready-to-post copy and image prompts per platform.
- **03 – Social Posts**: multi-provider publish queue with GetLate / Buffer / Publer switching.
- **04 – Analytics**: retention, shares, follower conversion, daily posts, platform views.
- **05 – Learning**: human-in-the-loop feedback log for hook experiments.
- **06 – Hook Lab**: CSV grid of hooks, retention, and CTR performance.
- **07 – Settings / Health**: environment guidance and provider status checks.

## Automation Pipelines

- `pipelines/run_ai_news.py` ingests RSS feeds, ranks stories, summaries with LLM (fallback supported), generates social copy, placeholder media, and updates `app/data/*`.
- `pipelines/ai-news-shorts.yml` mirrors the same steps for orchestration platforms.

## Multi-Provider Publishing

`app/services/publish_service.py` queues posts and dispatches them via:
- `app/services/getlate_client.py`
- `app/services/buffer_client.py`
- `app/services/publer_client.py`

The active provider defaults to `POST_PROVIDER` or the last provider used in the UI. Failed posts remain in the queue and can be rerouted instantly.

## Analytics & Health

- `app/services/analytics_service.py` reads/writes aggregated metrics (`app/data/analytics_summary.json`).
- `app/services/healthcheck.py` verifies credential presence (GetLate, Buffer, Publer) and DNS resolution, persisting the latest run at `logs/health_last.json`.

## Deployment

- Pushes to `main` trigger the GitHub Actions `deploy.yml` workflow (placeholder) and Streamlit Cloud auto-redeploys if configured.
- Point `app.xseller.ai` to the Streamlit app URL via CNAME (already provisioned).

## Useful Commands

```bash
# Run dashboard locally
streamlit run app/streamlit_app.py

# Execute automation pipeline
python pipelines/run_ai_news.py

# Refresh health status
python app/services/healthcheck.py
```

## Contributing

- Commit with conventional messages (e.g., `feat:`, `fix:`).
- Keep `app/data/` JSON/CSV files lightweight or mock when secrets are unavailable.
- Use `st.warning`/`st.info` to surface missing provider credentials in the UI.
