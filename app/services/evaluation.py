"""Evaluation Service — Langfuse observability (OpenTelemetry-based SDK v5): tracing and scoring.

Every pipeline run becomes one Langfuse trace:
    ekia_debug_agent (agent)
      ├─ graph_retrieval (retriever)
      ├─ parse_query (chain)   └─ llm.query_rewrite (generation)
      ├─ retrieve (retriever)
      ├─ reason (chain)        └─ llm.reasoning (generation)
      └─ validate (span)
plus trace-level scores: confidence, completeness, overall_quality.

Observability must never break a request, so every Langfuse call is wrapped and
degrades to a no-op when Langfuse is not configured or unreachable.
"""
import os
import time
from contextlib import contextmanager
from typing import Any, Optional

from dotenv import load_dotenv

load_dotenv()

_langfuse = None
_status = "not_initialized"
_last_attempt = 0.0
_RETRY_SECONDS = 60


def _keys_configured() -> bool:
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
    return bool(public_key and secret_key and not public_key.startswith("pk-lf-your"))


def get_langfuse():
    """Lazy-load and auth-check the Langfuse client (singleton, retried at most once a minute)."""
    global _langfuse, _status, _last_attempt

    if _langfuse is not None:
        return _langfuse
    if not _keys_configured():
        _status = "disabled"
        return None
    if time.time() - _last_attempt < _RETRY_SECONDS:
        return None
    _last_attempt = time.time()

    try:
        from langfuse import Langfuse

        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        client = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            base_url=host,
            environment=os.getenv("LANGFUSE_ENVIRONMENT", "development"),
        )
        if client.auth_check():
            _langfuse = client
            _status = "connected"
            print(f"[Langfuse] Connected to {host}")
        else:
            _status = "auth_failed"
            print("[Langfuse] ⚠ Auth check failed — tracing disabled")
    except Exception as e:
        _status = "unreachable"
        print(f"[Langfuse] ⚠ Could not connect: {e}")

    return _langfuse


def langfuse_status() -> str:
    """'connected' | 'disabled' | 'auth_failed' | 'unreachable' | 'not_initialized'."""
    get_langfuse()
    return _status


def flush():
    if _langfuse is not None:
        try:
            _langfuse.flush()
        except Exception as e:
            print(f"[Langfuse] Flush failed: {e}")


def dashboard_url() -> Optional[str]:
    """URL of this project's traces list in the Langfuse UI."""
    lf = get_langfuse()
    if lf is None:
        return os.getenv("LANGFUSE_HOST") or None
    try:
        sample = lf.get_trace_url(trace_id="0" * 32)
        return sample.rsplit("/traces/", 1)[0] + "/traces" if sample else None
    except Exception:
        return os.getenv("LANGFUSE_HOST") or None


def trace_url(trace_id: Optional[str]) -> Optional[str]:
    if _langfuse is None or not trace_id:
        return None
    try:
        return _langfuse.get_trace_url(trace_id=trace_id)
    except Exception:
        return None


class _Observation:
    """Null-safe wrapper around a Langfuse observation; every method swallows its own errors."""

    def __init__(self, obs=None):
        self._obs = obs

    @property
    def trace_id(self) -> Optional[str]:
        return getattr(self._obs, "trace_id", None) if self._obs else None

    def update(self, **kwargs):
        if self._obs:
            try:
                self._obs.update(**kwargs)
            except Exception as e:
                print(f"[Langfuse] update failed: {e}")

    def score_trace(self, name: str, value: float, comment: Optional[str] = None):
        if self._obs:
            try:
                self._obs.score_trace(name=name, value=value, comment=comment)
            except Exception as e:
                print(f"[Langfuse] score failed: {e}")


@contextmanager
def observation(name: str, as_type: str = "span", **kwargs: Any):
    """Open a Langfuse observation as the current OTel span (nests automatically).

    Yields an _Observation; when Langfuse is unavailable it is a no-op wrapper.
    """
    lf = get_langfuse()
    if lf is None:
        yield _Observation()
        return
    try:
        cm = lf.start_as_current_observation(name=name, as_type=as_type, **kwargs)
        obs = cm.__enter__()
    except Exception as e:
        print(f"[Langfuse] Could not start '{name}': {e}")
        yield _Observation()
        return

    try:
        yield _Observation(obs)
    except BaseException as exc:
        try:
            obs.update(level="ERROR", status_message=str(exc)[:500])
        except Exception:
            pass
        cm.__exit__(type(exc), exc, exc.__traceback__)
        raise
    else:
        cm.__exit__(None, None, None)


def score_response(root: _Observation, response: dict):
    """Auto-score a finished response on the trace: confidence, completeness, overall quality."""
    confidence = float(response.get("confidence_score", 0.0) or 0.0)
    has_fix = bool(str(response.get("fix", "")).strip())
    has_concepts = len(response.get("related_concepts", []) or []) > 0
    has_problems = len(response.get("practice_problems", []) or []) > 0

    completeness = sum([has_fix, has_concepts, has_problems]) / 3.0
    overall = (confidence * 0.7) + (completeness * 0.3)

    root.score_trace("confidence", confidence, f"Model self-reported confidence: {confidence:.2f}")
    root.score_trace(
        "completeness",
        completeness,
        f"fix={has_fix}, concepts={has_concepts}, problems={has_problems}",
    )
    root.score_trace("overall_quality", overall, "0.7 × confidence + 0.3 × completeness")
    print(f"[Langfuse] Scored — overall: {overall:.2f}")
    return overall
