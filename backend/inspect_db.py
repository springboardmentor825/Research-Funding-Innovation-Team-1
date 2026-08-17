import pymysql

conn = pymysql.connect(host='localhost', user='root', password='Madhu@123', database='research_platform')
cur = conn.cursor()

with open("db_schema_output.txt", "w") as f:
    for table in ['users', 'Research_Profile', 'Publications', 'Patents', 'funding_opportunities']:
        f.write(f"=== Table: {table} ===\n")
        cur.execute(f"DESCRIBE `{table}`")
        for c in cur.fetchall():
            f.write(f"  {c[0]:<25} {c[1]:<25} Null:{c[2]:<5} Key:{c[3]:<5} Default:{c[4]}\n")
        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        cnt = cur.fetchone()[0]
        f.write(f"Total Rows: {cnt}\n\n")

conn.close()
print("Done writing db_schema_output.txt")
