import pymysql

conn = pymysql.connect(host='localhost', user='root', password='Madhu@123', database='research_platform')
cur = conn.cursor(pymysql.cursors.DictCursor)

with open("users_output.txt", "w") as f:
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    f.write(f"Total Users: {len(users)}\n")
    for u in users:
        f.write(f"User {u['id']}: {u['full_name']} ({u['email']}) Role: {u['role']}\n")

    cur.execute('SELECT * FROM Research_Profile')
    profiles = cur.fetchall()
    f.write(f"\nTotal Profiles: {len(profiles)}\n")
    for p in profiles:
        f.write(f"User {p['user_id']}: Domain='{p['research_domain']}' | Tech='{p['technology_area']}' | Interests='{p['research_interests']}' | Keywords='{p['keywords']}'\n")

    cur.execute('SELECT user_id, COUNT(*) as count FROM Publications GROUP BY user_id')
    f.write(f"\nPublications per user: {cur.fetchall()}\n")

    cur.execute('SELECT user_id, COUNT(*) as count FROM Patents GROUP BY user_id')
    f.write(f"Patents per user: {cur.fetchall()}\n")

conn.close()
