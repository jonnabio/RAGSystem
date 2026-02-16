from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from src.features.rag.application.evaluation_service import EvaluationService
from src.features.rag.application.evaluation_service import EvaluationService
from src.features.chat.application.chat_service import ChatService
from src.api.dependencies import get_chat_service
import logging

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])
logger = logging.getLogger(__name__)

# Integration points for dependencies
def get_evaluation_service():
    return EvaluationService()

@router.post("/run")
async def run_evaluation(
    eval_service: EvaluationService = Depends(get_evaluation_service),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Trigger a batch evaluation across the golden dataset.
    """
    try:
        results = await eval_service.run_batch_evaluation(chat_service)
        return results
    except Exception as e:
        logger.error(f"Failed to run evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results")
async def get_latest_results(
    eval_service: EvaluationService = Depends(get_evaluation_service)
):
    """
    Retrieve the latest evaluation scores.
    """
    try:
        if not eval_service.results_path.exists():
            return {"status": "error", "message": "No evaluation results found. Run a benchmark first."}

        import json
        with open(eval_service.results_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to retrieve results: {e}")
        raise HTTPException(status_code=500, detail=str(e))
