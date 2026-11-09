
import sys
import sqlite3
from pathlib import Path

# Allow imports when running from Data_manager folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Data_manager import data_manager2 as dm
from Data_manager.accounts import Account
from Data_manager.admin_accounts import AdminA
from Data_manager.tech_accounts import TechA
from Data_manager.customer_accounts import CustomerA
from Data_manager.all_emails import Email
from Data_manager.admin_emails import AdminE
from Data_manager.tech_emails import TechE


# ---------------- TEST RESULTS ----------------

passed = 0
failed = 0


def check(name, condition):
    global passed, failed

    if condition:
        print(f"[PASS] {name}")
        passed += 1
    else:
        print(f"[FAIL] {name}")
        failed += 1


def check_exception(name, exception_type, function):
    try:
        function()
        check(name, False)

    except exception_type:
        check(name, True)

    except Exception as error:
        print(f"Unexpected error: {error}")
        check(name, False)


# ---------------- ACCOUNT TESTS ----------------

def test_accounts():
    print("\n===== ACCOUNT TESTS =====")

    admin = AdminA("admin@test.com", "admin123")
    tech = TechA("tech@test.com", "tech123")
    customer = CustomerA("customer@test.com", "customer123")

    check("Admin role", admin.role == "Admin")
    check("Tech role", tech.role == "Tech")
    check("Customer role", customer.role == "Customer")

    for account in (admin, tech, customer):
        existing = account.get_account()

        if existing is None:
            check(
                f"Save {account.role} account",
                account.set_account() is True
            )
        else:
            check(
                f"{account.role} account already exists",
                existing[2] == account.role
            )

    check(
        "Retrieve Customer account",
        customer.get_account() is not None
    )

    check_exception(
        "Abstract Account cannot be instantiated",
        TypeError,
        lambda: Account("test@test.com", "123")
    )

    check_exception(
        "Duplicate account rejected",
        ValueError,
        lambda: customer.set_account()
    )

    check_exception(
        "Empty address rejected",
        ValueError,
        lambda: CustomerA("", "password123")
    )


# ---------------- EMAIL TESTS ----------------

def test_email():
    print("\n===== EMAIL TESTS =====")

    email = Email(
        "customer@test.com",
        "Initial Account Complaint",
        "I cannot log into my account.",
        "2026-11-10 09:00:00"
    )

    email_id = email.add_to_DB()

    check(
        "Save original email",
        isinstance(email_id, int) and email_id > 0
    )

    result = email.get_email()

    check(
        "Retrieve original email",
        result is not None and result[0] == email_id
    )

    check(
        "Save AI analysis",
        email.add_to_AI_C_A(
            "Account Issue", 6, "Admin"
        ) is True
    )

    check_exception(
        "Reject invalid priority score",
        ValueError,
        lambda: email.add_to_AI_C_A(
            "Account Issue", 9, "Admin"
        )
    )

    check_exception(
        "Reject invalid department",
        ValueError,
        lambda: email.add_to_AI_C_A(
            "Account Issue", 6, "Invalid"
        )
    )

    return email, email_id


# ---------------- ADMIN TESTS ----------------

def test_admin(email, email_id):
    print("\n===== ADMIN TESTS =====")

    admin_email = AdminE(
        email_id,
        "Account Issue",
        email.address,
        email.subject,
        email.content,
        email.datetime,
        "2026-11-12 09:00:00",
        6
    )

    check(
        "Save Admin complaint",
        admin_email.add_to_DB() == email_id
    )

    check(
        "Retrieve Admin complaint",
        admin_email.get_email()[0] == email_id
    )

    check(
        "Increase Admin priority to 7",
        admin_email.update_score() is True
        and admin_email.us == 7
    )

    check(
        "Increase Admin priority to 8",
        admin_email.update_score() is True
        and admin_email.us == 8
    )

    check(
        "Admin priority capped at 8",
        admin_email.update_score() is False
        and admin_email.us == 8
    )

    check(
        "Resolve Admin complaint",
        admin_email.resolve() is True
        and admin_email.status == "Resolved"
    )

    check(
        "Resolved Admin excluded from unresolved",
        all(
            row[0] != email_id
            for row in admin_email.load_all_unresolved()
        )
    )

    check(
        "Resolved Admin appears in resolved",
        any(
            row[0] == email_id
            for row in admin_email.load_all_resolved()
        )
    )

    check(
        "Reopen Admin complaint",
        admin_email.unresolve() is True
        and admin_email.status == "Unresolved"
    )

    return admin_email


# ---------------- TECH TESTS ----------------

def test_tech():
    print("\n===== TECH TESTS =====")

    email = Email(
        "customer@test.com",
        "Initial Technical Complaint",
        "My computer keeps crashing.",
        "2026-11-10 09:30:00"
    )

    email_id = email.add_to_DB()

    check(
        "Save Tech original email",
        isinstance(email_id, int) and email_id > 0
    )

    check(
        "Save Tech AI analysis",
        email.add_to_AI_C_A(
            "Technical Issue", 5, "Tech"
        ) is True
    )

    tech_email = TechE(
        email_id,
        "Technical Issue",
        email.address,
        email.subject,
        email.content,
        email.datetime,
        "2026-11-12 09:30:00",
        5
    )

    check(
        "Save Tech complaint",
        tech_email.add_to_DB() == email_id
    )

    check(
        "Retrieve Tech complaint",
        tech_email.get_email()[0] == email_id
    )

    check(
        "Increase Tech priority",
        tech_email.update_score() is True
        and tech_email.us == 6
    )

    check(
        "Resolve Tech complaint",
        tech_email.resolve() is True
        and tech_email.status == "Resolved"
    )

    check(
        "Reopen Tech complaint",
        tech_email.unresolve() is True
        and tech_email.status == "Unresolved"
    )

    return email_id


# ---------------- 30 MIXED COMPLAINT TEST ----------------

def test_30_complaints():
    print("\n===== INSERTING 30 MIXED COMPLAINTS =====")

    # Mixed order: 15 Admin and 15 Tech complaints
    test_complaints = [
        ("Account Locked", "Cannot log in", 3, "Admin"),
        ("WiFi Not Working", "Cannot connect to WiFi", 3, "Tech"),
        ("Computer Crashing", "Computer keeps crashing", 7, "Tech"),
        ("Payment Failed", "Payment was rejected", 7, "Admin"),
        ("Wrong Invoice", "Incorrect billing amount", 5, "Admin"),
        ("Printer Offline", "Printer cannot connect", 5, "Tech"),
        ("Slow Internet", "Internet connection is slow", 2, "Tech"),
        ("Refund Request", "Refund not received", 2, "Admin"),
        ("Server Down", "Company server is unavailable", 8, "Tech"),
        ("Account Hacked", "Someone accessed my account", 8, "Admin"),
        ("Late Delivery", "Package arrived late", 4, "Admin"),
        ("Software Error", "Application displays an error", 4, "Tech"),
        ("Data Loss", "Important files have disappeared", 8, "Tech"),
        ("Double Charge", "Charged twice", 6, "Admin"),
        ("Keyboard Fault", "Keyboard keys are not working", 1, "Tech"),
        ("Missing Refund", "Still waiting for refund", 1, "Admin"),
        ("Login Error", "Cannot access company system", 7, "Tech"),
        ("Account Suspended", "Unexpected suspension", 7, "Admin"),
        ("Billing Error", "Wrong amount charged", 5, "Admin"),
        ("Monitor Issue", "Monitor flickers frequently", 5, "Tech"),
        ("Email Not Syncing", "Emails are not updating", 4, "Tech"),
        ("Subscription Issue", "Unable to cancel subscription", 4, "Admin"),
        ("Security Breach", "Suspicious system activity", 8, "Tech"),
        ("Fraudulent Payment", "Unknown transaction detected", 8, "Admin"),
        ("Database Error", "Unable to connect to database", 6, "Tech"),
        ("Incorrect Account Details", "My account details are wrong", 3, "Admin"),
        ("System Freezing", "Computer freezes during operation", 6, "Tech"),
        ("Membership Renewal", "Incorrect renewal charge", 6, "Admin"),
        ("Network Outage", "Entire office network is down", 8, "Tech"),
        ("Unauthorised Purchase", "Purchase made without consent", 8, "Admin")
    ]

    created_ids = {
        "Admin": [],
        "Tech": []
    }

    for i, (subject, content, score, department) in enumerate(
        test_complaints
    ):
        email = Email(
            "customer@test.com",
            subject,
            content,
            f"2026-11-10 10:{i:02d}:00"
        )

        complaint_id = email.add_to_DB()

        category = (
            "Account/Billing Issue"
            if department == "Admin"
            else "Technical Issue"
        )

        email.add_to_AI_C_A(
            category,
            score,
            department
        )

        if department == "Admin":
            complaint = AdminE(
                complaint_id,
                category,
                email.address,
                email.subject,
                email.content,
                email.datetime,
                "2026-11-12 10:00:00",
                score
            )
        else:
            complaint = TechE(
                complaint_id,
                category,
                email.address,
                email.subject,
                email.content,
                email.datetime,
                "2026-11-12 10:00:00",
                score
            )

        complaint.add_to_DB()
        created_ids[department].append(complaint_id)

        print(
            f"Added {i + 1:02d}/30 | "
            f"ID: {complaint_id} | "
            f"Department: {department} | "
            f"Priority: {score} | "
            f"{subject}"
        )

    return created_ids


# ---------------- DATABASE VERIFICATION ----------------

def verify_database(created_ids):
    print("\n===== DATABASE VERIFICATION =====")

    for department, table in [
        ("Admin", "Admin_Team"),
        ("Tech", "Tech_Professionals")
    ]:
        ids = created_ids[department]
        placeholders = ",".join("?" for _ in ids)

        dm.c.execute(
            f"""
            SELECT COUNT(*)
            FROM Emails
            WHERE ComplaintID IN ({placeholders})
            """,
            ids
        )
        email_count = dm.c.fetchone()[0]

        dm.c.execute(
            f"""
            SELECT COUNT(*)
            FROM AI_Complaint_Analysis
            WHERE ComplaintID IN ({placeholders})
            """,
            ids
        )
        ai_count = dm.c.fetchone()[0]

        dm.c.execute(
            f"""
            SELECT COUNT(*)
            FROM {table}
            WHERE ComplaintID IN ({placeholders})
            """,
            ids
        )
        department_count = dm.c.fetchone()[0]

        check(
            f"{department}: 15 original emails saved",
            email_count == 15
        )

        check(
            f"{department}: 15 AI analyses saved",
            ai_count == 15
        )

        check(
            f"{department}: 15 department records saved",
            department_count == 15
        )

        dm.c.execute(
            f"""
            SELECT COUNT(*)
            FROM {table}
            WHERE ComplaintID IN ({placeholders})
            AND Status = 'Unresolved'
            """,
            ids
        )

        check(
            f"{department}: All 15 new complaints unresolved",
            dm.c.fetchone()[0] == 15
        )


# ---------------- JSON VERIFICATION ----------------

def verify_json():
    print("\n===== JSON VERIFICATION =====")

    for department, table in [
        ("Admin", "Admin_Team"),
        ("Tech", "Tech_Professionals")
    ]:
        print(f"\n----- {department.upper()} -----")

        dm.c.execute(f"""
            SELECT ComplaintID
            FROM {table}
            WHERE Status = 'Unresolved'
            ORDER BY UpdatedScore DESC,
                     Datetime ASC,
                     ComplaintID ASC
            LIMIT 10
        """)

        expected_ids = [
            row[0] for row in dm.c.fetchall()
        ]

        records = dm.load_from_JSON(department)

        if not isinstance(records, list):
            check(
                f"{department}: JSON loads successfully",
                False
            )
            continue

        actual_ids = [
            record["ComplaintID"]
            for record in records
        ]

        check(
            f"{department}: JSON contains exactly 10",
            len(records) == 10
        )

        check(
            f"{department}: JSON matches SQLite top 10",
            actual_ids == expected_ids
        )

        check(
            f"{department}: Priority sorted descending",
            all(
                records[i]["UpdatedScore"]
                >= records[i + 1]["UpdatedScore"]
                for i in range(len(records) - 1)
            )
        )

        check(
            f"{department}: Only unresolved complaints",
            all(
                record["Status"] == "Unresolved"
                for record in records
            )
        )

        print(f"\n{department} Top 10:")

        for position, record in enumerate(records, 1):
            print(
                f"{position:02d}. "
                f"ID: {record['ComplaintID']} | "
                f"Score: {record['UpdatedScore']} | "
                f"Status: {record['Status']}"
            )


# ---------------- CUSTOMER HISTORY TESTS ----------------

def test_customer_history(created_ids, initial_ids):
    print("\n===== CUSTOMER HISTORY TESTS =====")

    complaints = dm.load_customer_complaints(
        "customer@test.com"
    )

    if not isinstance(complaints, list):
        check("Customer complaint history loads", False)
        return

    expected_ids = set(
        created_ids["Admin"]
        + created_ids["Tech"]
        + initial_ids
    )

    actual_ids = {
        record[0] for record in complaints
    }

    check(
        "Customer history includes all new complaints",
        expected_ids.issubset(actual_ids)
    )

    check(
        "Customer history contains at least 32 complaints",
        len(complaints) >= 32
    )

    check(
        "Unknown customer has no complaints",
        dm.load_customer_complaints(
            "unknown@test.com"
        ) == []
    )


# ---------------- MAIN TEST RUNNER ----------------

def run_tests():
    global passed, failed

    passed = 0
    failed = 0

    print("=" * 50)
    print("DATA MANAGER FUNCTIONAL TEST")
    print("USING ACTUAL complaint.db")
    print("=" * 50)

    print(f"\nDatabase: {dm.BASE_DIR / 'complaint.db'}")

    try:
        test_accounts()

        email, email_id = test_email()

        test_admin(email, email_id)

        tech_id = test_tech()

        created_ids = test_30_complaints()

        verify_database(created_ids)

        verify_json()

        test_customer_history(
            created_ids,
            [email_id, tech_id]
        )

    except (sqlite3.DatabaseError, ValueError, RuntimeError) as error:
        failed += 1
        print(f"\n[ERROR] Test stopped: {error}")

    finally:
        print("\n" + "=" * 50)
        print("FINAL TEST SUMMARY")
        print("=" * 50)

        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total:  {passed + failed}")

        if failed == 0:
            print("\nALL CHECKS PASSED!")
        else:
            print("\nSOME CHECKS FAILED!")

        dm.db.close()


if __name__ == "__main__":
    run_tests()
