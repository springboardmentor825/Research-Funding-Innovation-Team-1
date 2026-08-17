import pymysql

conn = pymysql.connect(host='localhost', user='root', password='Madhu@123', database='research_platform')
cur = conn.cursor(pymysql.cursors.DictCursor)

with open("user16_and_funding_details.txt", "w") as f:
    f.write("=== USER 16 PUBLICATIONS ===\n")
    cur.execute('SELECT * FROM Publications WHERE user_id=16')
    pubs = cur.fetchall()
    for p in pubs:
        f.write(f"Pub {p['publication_id']}: '{p['title']}' | Journal: '{p['journal']}' | Year: {p['publication_year']}\n")

    f.write("\n=== USER 16 PATENTS ===\n")
    cur.execute('SELECT * FROM Patents WHERE user_id=16')
    pats = cur.fetchall()
    for pt in pats:
        f.write(f"Patent {pt['patent_id']}: '{pt['title']}' | Tech Domain: '{pt['technology_domain']}'\n")

    f.write("\n=== ALL FUNDING OPPORTUNITIES ===\n")
    cur.execute('SELECT * FROM funding_opportunities')
    fundings = cur.fetchall()
    for fo in fundings:
        f.write(f"ID {fo['id']}: '{fo['title']}' | Funder: '{fo['funder']}' | Amount: '{fo['amount_range']}' | Deadline: {fo['deadline']} | Fit: {fo['semantic_fit']} | Badges: '{fo['match_badges']}'\n")

conn.close()
print("Saved to user16_and_funding_details.txt")
