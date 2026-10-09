
from sqlite3 import connect
from datetime import datetime

db = connect('complaint.db')
c = db.cursor()


def Deadline_Classification(priority_score, date_created, current_date):

    days_passed = (current_date.date() - date_created.date()).days

    if days_passed <= 0:
        new_priority = priority_score
    else:
        new_priority = priority_score + days_passed

    if new_priority > 8:
        new_priority = 8

    return new_priority


current_date = datetime.now()

# Update Tech Professionals
c.execute("SELECT id, priority, date FROM Tech_Professionals")
Tech_data = c.fetchall()

for complaint_id, priority, date in Tech_data:

    date_created = datetime.strptime(date, "%Y-%m-%d")

    new_priority = Deadline_Classification(
        priority, date_created, current_date
    )

    c.execute(
        "UPDATE Tech_Professionals SET priority = ? WHERE id = ?",
        (new_priority, complaint_id)
    )



# Update Admin
c.execute("SELECT id, priority, date FROM Admin")
Admin_data = c.fetchall()

for complaint_id, priority, date in Admin_data:

    date_created = datetime.strptime(date, "%Y-%m-%d")

    new_priority = Deadline_Classification(
        priority, date_created, current_date
    )

    c.execute(
        "UPDATE Admin SET priority = ? WHERE id = ?",
        (new_priority, complaint_id)
    )


db.commit()

# Sort Tech Professionals after updating
c.execute("""
    SELECT * FROM Tech_Professionals
    ORDER BY priority DESC
""")
Tech_sorted = c.fetchall()

# Sort Admin after updating
c.execute("""
    SELECT * FROM Admin
    ORDER BY priority DESC
""")
Admin_sorted = c.fetchall()





db.close()

