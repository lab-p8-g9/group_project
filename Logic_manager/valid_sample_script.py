
import sqlite3
import json
from Logic_manager.logic_main import logic_main
from Data_manager.data_manager2 import db, c
from Logic_manager.logic_recalculate_score import recalculate_logic_score

def AI_Sample():

    emails = [
        {
            "email_address": "student1@gmail.com",
            "subject": "School WiFi Not Working",
            "content": "I cannot connect to the school WiFi.",
            "category": "Network Issue",
            "priority_score": 7,
            "assigned_to": "Tech"
        },
        {
            "email_address": "student2@gmail.com",
            "subject": "Incorrect School Fees",
            "content": "My school fee payment was charged twice.",
            "category": "Finance Issue",
            "priority_score": 6,
            "assigned_to": "Admin"
        },
        {
            "email_address": "student3@gmail.com",
            "subject": "Computer Cannot Start",
            "content": "The classroom computer cannot turn on.",
            "category": "Hardware Issue",
            "priority_score": 8,
            "assigned_to": "Tech"
        },
        {
            "email_address": "student4@gmail.com",
            "subject": "Student Card Replacement",
            "content": "I lost my student card and need a replacement.",
            "category": "Student Services",
            "priority_score": 3,
            "assigned_to": "Admin"
        },
        {
            "email_address": "student5@gmail.com",
            "subject": "School Portal Error",
            "content": "I cannot access the school portal.",
            "category": "Software Issue",
            "priority_score": 7,
            "assigned_to": "Tech"
        },
        {
            "email_address": "student6@gmail.com",
            "subject": "Incorrect Attendance",
            "content": "My attendance record is incorrect.",
            "category": "Academic Administration",
            "priority_score": 5,
            "assigned_to": "Admin"
        }
    ]

    with open("ai_output.json", "w", encoding="utf-8") as file:
        json.dump(emails, file, indent=4)

    print("AI sample generated successfully!")


# Run test directly

def create_test_accounts():
    for i in range(1, 7):
        email_address = f"student{i}@gmail.com"

        c.execute("""
            INSERT OR IGNORE INTO Accounts(Address, Password, Role)
            VALUES (?, ?, ?)
        """, (email_address, "TEST_ONLY_PASSWORD", "Student"))

    db.commit()

    print("Test accounts created successfully!")

def test_ai_sample_inserted():
    with open("ai_output.json", "r", encoding="utf-8") as file:
        emails = json.load(file)

    for email in emails:
        c.execute("""
            SELECT ComplaintID
            FROM Emails
            WHERE Address = ?
            AND Subject = ?
            AND Content = ?
        """, (
            email["email_address"],
            email["subject"],
            email["content"]
        ))

        result = c.fetchone()

        assert result is not None, (
            f"FAILED: {email['subject']} was not found in database!"
        )

        print(f"PASSED: {email['subject']} found in database!")

    print("\nALL AI SAMPLE EMAILS SUCCESSFULLY STORED!")

if __name__ == "__main__":
    AI_Sample()
    create_test_accounts()


    process = logic_main("ai_output.json")

    # Call its method to process all AI samples
    process.process_ai_sample()

    test_ai_sample_inserted()