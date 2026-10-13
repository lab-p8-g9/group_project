from sqlite3 import connect
from data_manager import *
from datetime import datetime, timedelta
import json
import os



def Logic_Create_Email_List(email, subject, content):

    email_list = [{
        "Email": email,
        "Subject": subject,
        "Content": content
    }]

    save_to_JSON(email_list)



# STEP 1: READ INCOMING AI JSON FILE

def Logic_Read_AI_JSON(file_name):

    with open(file_name, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


# STEP 2: SAVE EMAILS INTO SQL


def Logic_Save_Emails_To_SQL(db, emails):

    c = db.cursor()

    for email_data in emails:

        # Get email details from JSON
        email_address = email_data["email_address"]
        subject = email_data["subject"]
        content = email_data["content"]

        # Generate current date and time
        current_datetime = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Insert email into Emails table
        c.execute("""
            INSERT INTO Emails
            (Email, Subject, Content, Datetime)
            VALUES (?, ?, ?, ?)
        """, (
            email_address,
            subject,
            content,
            current_datetime
        ))

        # Get ComplaintID automatically assigned by SQLite
        complaint_id = c.lastrowid

        # STEP 3: Save corresponding AI analysis
        Logic_Save_AI_Analysis_To_SQL(
            db,
            email_data,
            complaint_id
        )



# STEP 3: SAVE AI ANALYSIS INTO SQL

def Logic_Save_AI_Analysis_To_SQL(db, email_data, complaint_id):

    c = db.cursor()

    category = email_data["category"]
    priority_score = email_data["priority_score"]
    assigned_to = email_data["assigned_to"]

    c.execute("""
        INSERT INTO AI_Complaint_Analysis
        (ComplaintID, Category, PriorityScore, AssignedTo)
        VALUES (?, ?, ?, ?)
    """, (
        complaint_id,
        category,
        priority_score,
        assigned_to
    ))




# STEP 4: PROCESS INCOMING JSON

def Logic_Process_Incoming_JSON(file_name):

    if not os.path.exists(file_name):
        print("AI JSON file not found.")
        return False

    db = Logic_Connect_Database()

    try:

        # Read JSON file
        emails = Logic_Read_AI_JSON(file_name)

        # Insert Emails and AI analysis into SQL
        Logic_Save_Emails_To_SQL(db, emails)

        db.commit()



        print("Incoming JSON processed successfully.")
        return True

    except Exception as error:
        db.rollback()
        print("Error processing incoming JSON:", error)
        return False

    finally:
        db.close()

#======================================================================================================


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
    print(complaint_data)
    print("2")
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


def Logic_Class_Main():

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


def Logic_Main(file_name):

    # Step 1: Process incoming AI JSON
    if Logic_Process_Incoming_JSON(file_name):

        # Step 2: Run original Logic Manager functions
        Logic_Class_Main()

    else:
        print("JSON processing failed. Logic Manager stopped.")



