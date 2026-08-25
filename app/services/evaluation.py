"""Evaluation Service — Langfuse observability, tracing, and scoring."""
import os
import time
from typing import Any
from dotenv import load_dotenv

load_dotenv()

_langfuse = None


def get_langfuse():
    """Lazy-load Langfuse client (singleton)."""
    global _langfuse
    if _langfuse is None:
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if not public_key or not secret_key or public_key.startswith("pk-lf-your"):
            print("[Langfuse] ⚠ API keys not configured — tracing disabled")
            return None

        try:
            from langfuse import Langfuse
            _langfuse = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host,
            )
            print(f"[Langfuse] Connected to {host}")
        except Exception as e:
            print(f"[Langfuse] Connection failed: {e}")
            return None

    return _langfuse


class TraceContext:
    """Context manager for a single agent run trace in Langfuse."""

    def __init__(self, name: str, input_data: dict, metadata: dict = None):
        self.name = name
        self.input_data = input_data
        self.metadata = metadata or {}
        self.trace = None
        self.trace_id = None
        self._start_time = None

    def __enter__(self):
        self._start_time = time.time()
        lf = get_langfuse()
        if lf:
            try:
                self.trace = lf.trace(
                    name=self.name,
                    input=self.input_data,
                    metadata=self.metadata,
                )
                self.trace_id = self.trace.id
                print(f"[Langfuse] Trace started: {self.trace_id}")
            except Exception as e:
                print(f"[Langfuse] Trace start failed: {e}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self._start_time) * 1000)
        if self.trace:
            try:
                status = "ERROR" if exc_type else "SUCCESS"
                self.trace.update(
                    output={"status": status},
                    metadata={**self.metadata, "duration_ms": duration_ms},
                )
                lf = get_langfuse()
                if lf:
                    lf.flush()
            except Exception as e:
                print(f"[Langfuse] Trace update failed: {e}")

    def score_response(self, response: dict):
        """Auto-score the response based on confidence and completeness."""
        if not self.trace:
            return

        confidence = response.get("confidence_score", 0.0)
        has_fix = bool(response.get("fix", "").strip())
        has_concepts = len(response.get("related_concepts", [])) > 0
        has_solutions = len(response.get("practice_problems", [])) > 0

        completeness = sum([has_fix, has_concepts, has_solutions]) / 3.0
        overall_score = (confidence * 0.7) + (completeness * 0.3)

        try:
            self.trace.score(
                name="confidence",
                value=confidence,
                comment=f"Model self-reported confidence: {confidence:.2f}",
            )
            self.trace.score(
                name="completeness",
                value=completeness,
                comment=f"Response completeness: fix={has_fix}, concepts={has_concepts}, problems={has_solutions}",
            )
            self.trace.score(name="overall_quality", value=overall_score)
            print(f"[Langfuse] Scored — overall: {overall_score:.2f}")
        except Exception as e:
            print(f"[Langfuse] Score failed: {e}")

    def log_span(self, name: str, input_data: Any, output_data: Any):
        """Log a sub-span for individual pipeline steps."""
        if not self.trace:
            return
        try:
            self.trace.span(name=name, input=input_data, output=output_data)
        except Exception:
            pass
