import lancedb
import pandas as pd
from src.config import settings

def inspect_db():
    db = lancedb.connect(settings.VECTOR_DB_PATH)
    print(f"Tables: {db.table_names()}")

    for name in db.table_names():
        table = db.open_table(name)
        print(f"\nTable: {name}")
        print(f"Schema: {table.schema}")
        try:
            df = table.to_pandas()
            print(f"Columns in pandas: {df.columns.tolist()}")
            if len(df) > 0:
                print("First row Sample:")
                print(df.iloc[0].to_dict())
        except Exception as e:
            print(f"Error reading table: {e}")

if __name__ == "__main__":
    inspect_db()
