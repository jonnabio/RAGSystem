import json
import numpy as np

try:
    json.dumps({"val": np.nan})
except Exception as e:
    print(f"Broke as expected: {e}")
