from sqlite3 import connect
from datetime import datetime, timedelta



# Connect to database 'complain.db"
def Logic_Connect_Database():
    return connect("complaint.db")


def Logic_Assign_Complaints(db):

    c = db.cursor()

    # Retrieve all AI-classified complaints
    c.execute("""
        SELECT ComplaintID, Category, PriorityScore, AssignedTo
        FROM AI_Complaint_Analysis
    """)

    complaints = c.fetchall()

    for complaint_id, category, priority, assigned_to in complaints:

        if assigned_to == "Tech_Professionals":
            table_name = "Tech_Professionals"

        elif assigned_to == "Admin_Team":
            table_name = "Admin_Team"

        else:
            continue

        # Insert complaint into the correct table
        c.execute(f"""
            INSERT INTO {table_name}
            (ComplaintID, Category, PriorityScore)
            VALUES (?, ?, ?)
        """, (complaint_id, category, priority))



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

        date_created = datetime.strptime(date, "%Y-%m-%d")

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
        # Step 1: Assign complaints to their respective tables
        Logic_Assign_Complaints(db)

        # Step 2: Update priorities and deadlines
        for table_name in ("Admin_Team", "Tech_Professionals"):
            Logic_Update_Priority(db, table_name)

        # Step 3: Save database changes
        db.commit()

        # Step 4: Sort and display complaints
        for table_name in ("Admin_Team", "Tech_Professionals"):
            sorted_complaints = Logic_Sort_Complaints(db, table_name)

            Logic_Display_Complaints(table_name, sorted_complaints)

    finally:
        db.close()


if __name__ == "__main__":
    Logic_Main()

