import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()

u = os.getenv('DB_USER','root')
p = urllib.parse.quote_plus(os.getenv('DB_PASSWORD',''))
h = os.getenv('DB_HOST','localhost')
port = os.getenv('DB_PORT','3306')
db = os.getenv('DB_NAME','research_platform')

engine = create_engine(f'mysql+pymysql://{u}:{p}@{h}:{port}/{db}')
inspector = inspect(engine)

output = []
for t in sorted(inspector.get_table_names()):
    output.append(f"=== TABLE: {t} ===")
    for c in inspector.get_columns(t):
        output.append(f"  {c['name']}: {c['type']} (nullable={c['nullable']})")
    output.append(f"  Foreign keys: {inspector.get_foreign_keys(t)}\n")

with open("schema_dump.txt", "w") as f:
    f.write("\n".join(output))

print("Dump completed.")
