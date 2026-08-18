from database import engine, Base
from models import Publication


print("=" * 60)
print("CREATING MYSQL TABLE")
print("=" * 60)

try:

    Base.metadata.create_all(bind=engine)

    print("\nMySQL table created successfully!")
    print("Table name: publications")

except Exception as e:

    print("\nFailed to create MySQL table.")
    print("Error:", e)