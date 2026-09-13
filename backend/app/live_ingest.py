"""Explicit live-model ingestion calls (evidence enhance, JD target detection).

Never a fallback: every call requires live readiness, counts against a small
per-session ingestion budget, and failures return errors the caller must handle
with the static path or manual input. Upload/run endpoints must not become
unmetered model endpoints (docs/03).
"""
import time
from .providers import GeminiProvider, ProviderError

INGESTION_ATTEMPT_CAP = 8  # model attempts per session across all ingestion calls
INGESTION_DEADLINE_SECONDS = 150


def gemini_ingest(store, session, config, task, schema, payload):
    """Run one budgeted Gemini ingestion call; records attempts on the session."""
    used = session.get('ingestion_model_attempts', 0) or 0
    if used >= INGESTION_ATTEMPT_CAP:
        raise ProviderError('ingestion_budget_exhausted')
    run = {'model_attempts': 0, 'mock_calls': 0, '_deadline': time.monotonic() + INGESTION_DEADLINE_SECONDS, 'mode': 'gemini'}
    provider = GeminiProvider(run, lambda: None, lambda *a, **k: None, config)
    try:
        return provider.call(task, schema, payload)
    finally:
        try:
            provider.close()
        finally:
            session['ingestion_model_attempts'] = used + run['model_attempts']
            store.update(session['id'], session)
