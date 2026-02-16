import json
import pandas as pd
from pathlib import Path
import numpy as np

class MockResult:
    def __init__(self, scores):
        self.scores = scores

def test_nan_serialization():
    results_path = Path("test_results_nan.json")
    # Simulation of NaN in scores (common in Ragas when a metric can't be computed)
    result = MockResult({
        "faithfulness": 0.85,
        "answer_relevancy": np.nan,
        "context_precision": 0.78
    })

    # Process scores to handle NaN (JSON doesn't support NaN)
    scores = {k: (v if not (isinstance(v, float) and np.isnan(v)) else 0.0) for k, v in result.scores.items()}

    summary = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "scores": scores,
        "sample_count": 5
    }

    print("Testing NaN handling and JSON serialization...")
    try:
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print("Success!")
        with open(results_path, "r", encoding="utf-8") as f:
            print(f.read())
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        if results_path.exists():
            results_path.unlink()

if __name__ == "__main__":
    test_nan_serialization()
