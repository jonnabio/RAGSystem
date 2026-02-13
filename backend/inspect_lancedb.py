import lancedb
import pandas as pd
from src.config import settings
import os

def inspect_db():
    output_file = "lancedb_inspection.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Current working directory: {os.getcwd()}\n")
        db = lancedb.connect(settings.VECTOR_DB_PATH)
        f.write(f"Tables: {db.table_names()}\n")

        for name in db.table_names():
            table = db.open_table(name)
            f.write(f"\nTable: {name}\n")
            f.write(f"Schema: {table.schema}\n")
            try:
                df = table.to_pandas()
                f.write(f"Columns in pandas: {df.columns.tolist()}\n")
                if len(df) > 0:
                    f.write("First row Sample:\n")
                    row = df.iloc[0].to_dict()
                    for k, v in row.items():
                        if k != 'vector':
                            f.write(f"  {k}: {v}\n")
            except Exception as e:
                f.write(f"Error reading table: {e}\n")
    print(f"Inspection written to {output_file}")

if __name__ == "__main__":
    inspect_db()
