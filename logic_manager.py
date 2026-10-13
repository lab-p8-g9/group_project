from sqlite3 import connect
from datetime import datetime, timedelta



# Connect to database 'complain.db"
def Logic_Connect_Database():
    return connect("complaint.db")


def Logic_Assign_Complaints(db):

    c = db.cursor()

    c.execute("""
        SELECT a.ComplaintID, a.Category,
               a.PriorityScore, a.AssignedTo,
               e.Datetime
        FROM AI_Complaint_Analysis a
        JOIN Emails e
        ON a.ComplaintID = e.ComplaintID
    """)

    complaints = c.fetchall()

    for complaint_id, category, priority, assigned_to, date in complaints:

        if assigned_to == "Tech_Professionals":
            table_name = "Tech_Professionals"

        elif assigned_to == "Admin_Team":
            table_name = "Admin_Team"

        else:
            continue

        # Prevent duplicate assignments
        c.execute(
            f"SELECT 1 FROM {table_name} WHERE ComplaintID = ?",
            (complaint_id,)
        )

        if c.fetchone():
            continue

        # Insert complaint with its date
        c.execute(f"""
            INSERT INTO {table_name}
            (ComplaintID, Category, Datetime, PriorityScore)
            VALUES (?, ?, ?, ?)
        """, (complaint_id, category, date, priority))



# Calculate priority and deadline
def Logic_Deadline_Classification(priority_score, date_created, current_date):

    days_passed = (current_date.date() - date_created.date()).days

    if days_passed <= 0:
        new_priority = priority_score
    else:
        new_priority = priority_score + days_passed

    if new_priority > 8:
        new_priority = 8

    days_to_deadline = max(0, 8 - priority_score)

    deadline_date = date_created + timedelta(days=days_to_deadline)

    return new_priority, deadline_date


# Update priority and deadline for one table use function for each table respectively
def Logic_Update_Priority(db, table_name):

    if table_name not in ("Admin_Team", "Tech_Professionals"):
        raise ValueError("Invalid table name")

    c = db.cursor()
    current_date = datetime.now()

    c.execute(f"""
        SELECT ComplaintID, PriorityScore, Datetime
        FROM {table_name}
    """)

    complaint_data = c.fetchall()

    for complaint_id, Priority, date in complaint_data:

        date_created = datetime.fromisoformat(date)

        new_priority, deadline_date = Logic_Deadline_Classification(
            Priority, date_created, current_date
        )

        c.execute(
            f"""UPDATE {table_name}
                SET UpdatedScore = ?, Deadline = ?
                WHERE ComplaintID = ?""",
            (
                new_priority,
                deadline_date.strftime("%Y-%m-%d"),
                complaint_id
            )
        )


# Sort complaints from highest to lowest priority using SQL Desc
def Logic_Sort_Complaints(db, table_name):

    if table_name not in ("Admin_Team", "Tech_Professionals"):
        raise ValueError("Invalid table name")

    c = db.cursor()

    c.execute(f"""
        SELECT *
        FROM {table_name}
        ORDER BY UpdatedScore DESC, Deadline ASC
    """)

    return c.fetchall()


# Display sorted complaints for test only

def Logic_Display_Complaints(table_name, complaints):

    print(f"\n{table_name} Complaints:")

    for complaint in complaints:
        print(complaint)


# Main function applications for table 'tech_professional' & 'Admin' in 'complaint.db'


def Logic_Main():

    db = Logic_Connect_Database()

    try:
        # Assign complaints to departments
        Logic_Assign_Complaints(db)

        # Update priority and deadline
        Logic_Update_Priority(db, "Admin_Team")
        Logic_Update_Priority(db, "Tech_Professionals")

        # Save changes
        db.commit()

        # Sort complaints
        admin_complaints = Logic_Sort_Complaints(db, "Admin_Team")
        tech_complaints = Logic_Sort_Complaints(db, "Tech_Professionals")

        # Display complaints
        Logic_Display_Complaints("Admin_Team", admin_complaints)
        Logic_Display_Complaints("Tech_Professionals", tech_complaints)

    finally:
        db.close()

if __name__ == "__main__":
    Logic_Main()

