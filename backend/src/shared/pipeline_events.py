"""Pipeline event tracking for step-by-step visualization.

Provides an in-memory event log that captures each stage of
document ingestion and chat query processing. The frontend
polls `/api/system/events` to render a live pipeline view.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel
import uuid
import threading


class PipelineStep(BaseModel):
    """A single step in a pipeline execution."""
    id: str
    stage: str          # e.g. "parsing", "chunking", "embedding", "storing"
    status: str         # "pending", "running", "completed", "error"
    message: str
    detail: Optional[Dict[str, Any]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None


class PipelineRun(BaseModel):
    """A full pipeline execution (ingestion or query)."""
    id: str
    pipeline_type: str  # "ingestion" or "query"
    label: str          # e.g. filename or query text
    status: str         # "running", "completed", "error"
    steps: List[PipelineStep] = []
    started_at: str
    completed_at: Optional[str] = None


class PipelineEventTracker:
    """Thread-safe tracker for pipeline runs.

    Keeps the last N runs in memory for the frontend to poll.
    """

    def __init__(self, max_runs: int = 20):
        self._runs: List[PipelineRun] = []
        self._max_runs = max_runs
        self._lock = threading.Lock()

    def start_run(self, pipeline_type: str, label: str) -> str:
        """Start a new pipeline run. Returns run_id."""
        run_id = str(uuid.uuid4())[:8]
        run = PipelineRun(
            id=run_id,
            pipeline_type=pipeline_type,
            label=label[:80],
            status="running",
            started_at=datetime.now(timezone.utc).isoformat()
        )
        with self._lock:
            self._runs.append(run)
            # Prune old runs
            if len(self._runs) > self._max_runs:
                self._runs = self._runs[-self._max_runs:]
        return run_id

    def add_step(
        self,
        run_id: str,
        stage: str,
        message: str,
        detail: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a step to a run. Returns step_id."""
        step_id = str(uuid.uuid4())[:8]
        step = PipelineStep(
            id=step_id,
            stage=stage,
            status="running",
            message=message,
            detail=detail,
            started_at=datetime.now(timezone.utc).isoformat()
        )
        with self._lock:
            run = self._find_run(run_id)
            if run:
                run.steps.append(step)
        return step_id

    def complete_step(
        self,
        run_id: str,
        step_id: str,
        detail: Optional[Dict[str, Any]] = None
    ):
        """Mark a step as completed."""
        with self._lock:
            run = self._find_run(run_id)
            if run:
                for step in run.steps:
                    if step.id == step_id:
                        step.status = "completed"
                        step.completed_at = datetime.now(timezone.utc).isoformat()
                        if step.started_at:
                            started = datetime.fromisoformat(step.started_at)
                            ended = datetime.fromisoformat(step.completed_at)
                            step.duration_ms = (ended - started).total_seconds() * 1000
                        if detail:
                            step.detail = {**(step.detail or {}), **detail}
                        break

    def fail_step(self, run_id: str, step_id: str, error: str):
        """Mark a step as failed."""
        with self._lock:
            run = self._find_run(run_id)
            if run:
                for step in run.steps:
                    if step.id == step_id:
                        step.status = "error"
                        step.message = f"{step.message} — Error: {error}"
                        step.completed_at = datetime.now(timezone.utc).isoformat()
                        break

    def complete_run(self, run_id: str):
        """Mark a run as completed."""
        with self._lock:
            run = self._find_run(run_id)
            if run:
                run.status = "completed"
                run.completed_at = datetime.now(timezone.utc).isoformat()

    def fail_run(self, run_id: str, error: str):
        """Mark a run as failed."""
        with self._lock:
            run = self._find_run(run_id)
            if run:
                run.status = "error"
                run.completed_at = datetime.now(timezone.utc).isoformat()

    def get_runs(self, limit: int = 10) -> List[PipelineRun]:
        """Get recent runs (newest first)."""
        with self._lock:
            return list(reversed(self._runs[-limit:]))

    def _find_run(self, run_id: str) -> Optional[PipelineRun]:
        for run in self._runs:
            if run.id == run_id:
                return run
        return None


# Global singleton
pipeline_tracker = PipelineEventTracker()
