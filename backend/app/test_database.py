from database import engine

try:
    with engine.connect() as connection:
        print("======================================")
        print("MYSQL CONNECTION SUCCESSFUL")
        print("======================================")

except Exception as e:
    print("======================================")
    print("MYSQL CONNECTION FAILED")
    print("======================================")
    print(e)