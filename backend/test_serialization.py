import json
import pandas as pd
from pathlib import Path

class MockResult:
    def __init__(self, scores):
        self.scores = scores

def test_serialization():
    results_path = Path("test_results.json")
    result = MockResult({
        "faithfulness": 0.85,
        "answer_relevancy": 0.92,
        "context_precision": 0.78
    })

    summary = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "scores": result.scores,
        "sample_count": 5
    }

    print("Testing JSON serialization...")
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
    test_serialization()
