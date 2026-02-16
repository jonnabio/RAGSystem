import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.config import settings
import logging
import traceback

logger = logging.getLogger(__name__)

class EvaluationService:
    def __init__(self, data_dir: str = "data/evaluation"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.golden_dataset_path = self.data_dir / "golden_dataset.json"
        self.results_path = self.data_dir / "latest_results.json"

        # Initialize models for evaluation
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers={"HTTP-Referer": "https://rag-system.local", "X-Title": "RAG System Evaluation"}
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )

    async def evaluate_response(
        self,
        query: str,
        context: List[str],
        answer: str,
        ground_truth: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Evaluate a single RAG response using Ragas metrics.
        """
        data = {
            "question": [query],
            "contexts": [context],
            "answer": [answer],
        }

        if ground_truth:
            data["ground_truth"] = [ground_truth]

        dataset = Dataset.from_dict(data)

        # Define metrics to use
        metrics = [faithfulness, answer_relevancy]
        if ground_truth:
            metrics.append(context_precision)

        result = evaluate(
            dataset,
            metrics=metrics,
            llm=self.llm,
            embeddings=self.embeddings
        )

        return result.to_pandas().to_dict(orient="records")[0]

    async def run_batch_evaluation(self, chat_service: Any) -> Dict[str, Any]:
        """
        Run evaluation across the entire golden dataset.
        Requires a chat_service instance to generate answers for evaluation.
        """
        if not self.golden_dataset_path.exists():
            raise FileNotFoundError(f"Golden dataset not found at {self.golden_dataset_path}")

        with open(self.golden_dataset_path, "r", encoding="utf-8") as f:
            golden_data = json.load(f)

        eval_samples = []

        for item in golden_data.get("dataset", []):
            question = item["question"]
            ground_truth = item["ground_truth"]

            # Use chat_service to get current system response
            from src.features.chat.application.chat_service import ChatRequest
            request = ChatRequest(
                query=question,
                model=settings.DEFAULT_MODEL
            )

            try:
                response = await chat_service.chat(request)

                eval_samples.append({
                    "question": question,
                    "answer": response.answer,
                    "contexts": [s["text"] for s in response.sources],
                    "ground_truth": ground_truth
                })
            except Exception as e:
                logger.error(f"Error generating answer for evaluation: {e}")
                continue

        if not eval_samples:
            return {"status": "error", "message": "No samples generated for evaluation"}

        dataset = Dataset.from_dict({
            "question": [s["question"] for s in eval_samples],
            "answer": [s["answer"] for s in eval_samples],
            "contexts": [s["contexts"] for s in eval_samples],
            "ground_truth": [s["ground_truth"] for s in eval_samples]
        })

        try:
            result = evaluate(
                dataset,
                metrics=[faithfulness, answer_relevancy, context_precision],
                llm=self.llm,
                embeddings=self.embeddings
            )
        except Exception as e:
            logger.error(f"Ragas evaluation failed: {e}")
            logger.error(traceback.format_exc())
            raise e

        summary = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "scores": result.scores,
            "sample_count": len(eval_samples)
        }

        with open(self.results_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary
