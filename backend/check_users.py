import pymysql

conn = pymysql.connect(host='localhost', user='root', password='Madhu@123', database='research_platform')
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute('SELECT * FROM users')
users = cur.fetchall()
print(f'Total Users: {len(users)}')
for u in users:
    print(f"User {u['id']}: {u['full_name']} ({u['email']}) Role: {u['role']}")

cur.execute('SELECT * FROM Research_Profile')
profiles = cur.fetchall()
print(f'\nTotal Profiles: {len(profiles)}')
for p in profiles:
    print(f"Profile for User {p['user_id']}: Domain={p['research_domain']} | Tech={p['technology_area']} | Interests={p['research_interests']} | Keywords={p['keywords']}")

cur.execute('SELECT user_id, COUNT(*) as count FROM Publications GROUP BY user_id')
print(f'\nPublications count per user:', cur.fetchall())

cur.execute('SELECT user_id, COUNT(*) as count FROM Patents GROUP BY user_id')
print(f'Patents count per user:', cur.fetchall())

cur.execute('SELECT id, title, funder, amount_range, deadline, semantic_fit, match_badges FROM funding_opportunities LIMIT 10')
print(f'\nFunding opportunities count: {len(cur.fetchall())}')

conn.close()
