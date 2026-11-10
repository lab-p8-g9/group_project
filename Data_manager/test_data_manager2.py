
import sys
import sqlite3
from pathlib import Path

# Allow imports from Data_manager folder
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


def get_scores(table):
    dm.c.execute(f'''
        SELECT ComplaintID, PriorityScore, UpdatedScore, Status
        FROM {table}
    ''')

    return {
        row[0]: {
            "PriorityScore": row[1],
            "UpdatedScore": row[2],
            "Status": row[3]
        }
        for row in dm.c.fetchall()
    }


def get_status(complaint_id, department):
    if department == "Admin":
        table = "Admin_Team"
    else:
        table = "Tech_Professionals"

    dm.c.execute(
        f'''
        SELECT Status
        FROM {table}
        WHERE ComplaintID = ?
        ''',
        (complaint_id,)
    )

    result = dm.c.fetchone()
    return result[0] if result else None


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
        "Retrieve customer account",
        customer.get_account() is not None
    )

    check_exception(
        "Account is abstract",
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
        "Reject invalid priority",
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


# ---------------- 30 MIXED COMPLAINTS ----------------

def test_30_complaints():
    print("\n===== INSERTING 30 MIXED COMPLAINTS =====")

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

    created_ids = {"Admin": [], "Tech": []}

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

    check(
        "15 Admin complaints created",
        len(created_ids["Admin"]) == 15
    )

    check(
        "15 Tech complaints created",
        len(created_ids["Tech"]) == 15
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

        for table_name, description in [
            ("Emails", "original emails"),
            ("AI_Complaint_Analysis", "AI analyses"),
            (table, "departmental complaints")
        ]:
            dm.c.execute(
                f"""
                SELECT COUNT(*)
                FROM {table_name}
                WHERE ComplaintID IN ({placeholders})
                """,
                ids
            )

            check(
                f"{department}: 15 {description} saved",
                dm.c.fetchone()[0] == 15
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
            f"{department}: 15 complaints unresolved",
            dm.c.fetchone()[0] == 15
        )


# ---------------- JSON VERIFICATION ----------------

def verify_json():
    print("\n===== JSON VERIFICATION =====")

    for department, table in [
        ("Admin", "Admin_Team"),
        ("Tech", "Tech_Professionals")
    ]:
        dm.c.execute(f'''
            SELECT ComplaintID
            FROM {table}
            WHERE Status = 'Unresolved'
            ORDER BY UpdatedScore DESC,
                     Datetime ASC,
                     ComplaintID ASC
            LIMIT 10
        ''')

        expected_ids = [
            row[0] for row in dm.c.fetchall()
        ]

        records = dm.load_from_JSON(department)

        if not isinstance(records, list):
            check(f"{department}: JSON loads", False)
            continue

        actual_ids = [
            record["ComplaintID"]
            for record in records
        ]

        check(
            f"{department}: JSON contains top 10",
            len(records) == 10
        )

        check(
            f"{department}: JSON matches SQLite",
            actual_ids == expected_ids
        )

        check(
            f"{department}: Scores sorted correctly",
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


# ---------------- CUSTOMER HISTORY TESTS ----------------

def test_customer_history(created_ids, initial_ids):
    print("\n===== CUSTOMER HISTORY TESTS =====")

    complaints = dm.load_customer_complaints(
        "customer@test.com"
    )

    if not isinstance(complaints, list):
        check("Customer history loads", False)
        return

    expected_ids = set(
        created_ids["Admin"]
        + created_ids["Tech"]
        + initial_ids
    )

    actual_ids = {
        complaint[0] for complaint in complaints
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
        "Each complaint contains exactly 6 fields",
        all(len(complaint) == 6 for complaint in complaints)
    )

    check(
        "Complaint records are lists",
        all(
            isinstance(complaint, list)
            for complaint in complaints
        )
    )

    check(
        "Customer address is correct",
        all(
            complaint[1] == "customer@test.com"
            for complaint in complaints
        )
    )

    check(
        "Customer status is valid",
        all(
            complaint[5] in ("Resolved", "Unresolved")
            for complaint in complaints
        )
    )

    # Verify displayed statuses against SQLite
    correct_status = True

    for complaint in complaints:
        cid = complaint[0]
        displayed_status = complaint[5]

        dm.c.execute('''
            SELECT AssignedTo
            FROM AI_Complaint_Analysis
            WHERE ComplaintID = ?
        ''', (cid,))

        department = dm.c.fetchone()

        if department is None:
            if displayed_status != "Unresolved":
                correct_status = False
            continue

        actual_status = get_status(cid, department[0])

        if actual_status is None:
            actual_status = "Unresolved"

        if displayed_status != actual_status:
            correct_status = False

    check(
        "Customer statuses match SQLite",
        correct_status
    )

    # UPDATED: Sort by ComplaintID descending
    check(
        "Customer complaints sorted by ComplaintID descending",
        all(
            complaints[i][0] >= complaints[i + 1][0]
            for i in range(len(complaints) - 1)
        )
    )

    check(
        "Unknown customer returns empty list",
        dm.load_customer_complaints("unknown@test.com") == []
    )


# ---------------- DISPLAY CUSTOMER HISTORY ----------------

def test_display_customer_history():
    print("\n===== CUSTOMER COMPLAINT HISTORY =====")

    address = "customer@test.com"

    complaints = dm.load_customer_complaints(address)

    if complaints is None:
        check("Customer history retrieved successfully", False)
        return

    if not complaints:
        check("Customer history contains complaints", False)
        return

    print(f"\nCustomer: {address}")
    print(f"Total complaints submitted: {len(complaints)}")
    print("\n===== ALL SUBMITTED COMPLAINTS =====")

    for complaint in complaints:
        print("-" * 50)
        print(f"Complaint ID : {complaint[0]}")
        print(f"Address      : {complaint[1]}")
        print(f"Subject      : {complaint[2]}")
        print(f"Content      : {complaint[3]}")
        print(f"Datetime     : {complaint[4]}")
        print(f"Status       : {complaint[5]}")

    print("-" * 50)

    check(
        "All complaints belong to the correct customer",
        all(
            complaint[1] == address
            for complaint in complaints
        )
    )

    check(
        "Each displayed complaint contains 6 fields",
        all(len(complaint) == 6 for complaint in complaints)
    )

    check(
        "Displayed statuses are valid",
        all(
            complaint[5] in ("Resolved", "Unresolved")
            for complaint in complaints
        )
    )

    # UPDATED: Check ComplaintID descending
    check(
        "Displayed complaints sorted by ComplaintID descending",
        all(
            complaints[i][0] >= complaints[i + 1][0]
            for i in range(len(complaints) - 1)
        )
    )


# ---------------- BATCH SCORE UPDATE TESTS ----------------

def test_update_all_scores():
    print("\n===== UPDATE ALL SCORES TESTS =====")

    tables = ("Admin_Team", "Tech_Professionals")

    before = {
        table: get_scores(table)
        for table in tables
    }

    eligible = {}

    for table in tables:
        eligible[table] = sum(
            1
            for record in before[table].values()
            if record["Status"] == "Unresolved"
            and record["UpdatedScore"] is not None
            and record["UpdatedScore"] < 8
        )

    print("\nEligible complaints before update:")
    print("Admin:", eligible["Admin_Team"])
    print("Tech:", eligible["Tech_Professionals"])

    result = dm.update_all_scores()

    check(
        "update_all_scores returns True",
        result is True
    )

    after = {
        table: get_scores(table)
        for table in tables
    }

    for table in tables:
        department = (
            "Admin" if table == "Admin_Team" else "Tech"
        )

        correct_updates = True
        unchanged_resolved = True
        unchanged_maximum = True
        original_scores_unchanged = True

        updated_count = 0

        for cid, old in before[table].items():
            new = after[table].get(cid)

            if new is None:
                correct_updates = False
                continue

            old_score = old["UpdatedScore"]
            new_score = new["UpdatedScore"]

            if (
                old["Status"] == "Unresolved"
                and old_score is not None
                and old_score < 8
            ):
                if new_score == old_score + 1:
                    updated_count += 1
                else:
                    correct_updates = False
            else:
                if new_score != old_score:
                    correct_updates = False

            if old["Status"] == "Resolved":
                if new_score != old_score:
                    unchanged_resolved = False

            if old_score == 8:
                if new_score != 8:
                    unchanged_maximum = False

            if new["PriorityScore"] != old["PriorityScore"]:
                original_scores_unchanged = False

        check(
            f"{department}: All eligible scores increased by 1",
            correct_updates
        )

        check(
            f"{department}: Correct number of scores updated",
            updated_count == eligible[table]
        )

        check(
            f"{department}: Resolved scores unchanged",
            unchanged_resolved
        )

        check(
            f"{department}: Scores capped at 8",
            unchanged_maximum
        )

        check(
            f"{department}: Original PriorityScore unchanged",
            original_scores_unchanged
        )

        check(
            f"{department}: No complaints removed",
            set(before[table]) == set(after[table])
        )

    verify_json()


# ---------------- RESOLVED COMPLAINT BATCH TEST ----------------

def test_resolved_batch():
    print("\n===== RESOLVED COMPLAINT BATCH TEST =====")

    resolved_ids = {}

    for department in ("Admin", "Tech"):
        email = Email(
            "customer@test.com",
            f"Resolved Test {department}",
            "This complaint is used for testing.",
            "2026-11-10 15:00:00"
        )

        cid = email.add_to_DB()

        email.add_to_AI_C_A(
            "Test Issue", 3, department
        )

        complaint_class = (
            AdminE if department == "Admin" else TechE
        )

        complaint = complaint_class(
            cid,
            "Test Issue",
            email.address,
            email.subject,
            email.content,
            email.datetime,
            "2026-11-12 15:00:00",
            3
        )

        complaint.add_to_DB()
        complaint.resolve()

        resolved_ids[department] = cid

    before = {}

    for department, table in [
        ("Admin", "Admin_Team"),
        ("Tech", "Tech_Professionals")
    ]:
        dm.c.execute(
            f'''
            SELECT UpdatedScore
            FROM {table}
            WHERE ComplaintID = ?
            ''',
            (resolved_ids[department],)
        )

        before[department] = dm.c.fetchone()[0]

    dm.update_all_scores()

    for department, table in [
        ("Admin", "Admin_Team"),
        ("Tech", "Tech_Professionals")
    ]:
        dm.c.execute(
            f'''
            SELECT UpdatedScore, Status
            FROM {table}
            WHERE ComplaintID = ?
            ''',
            (resolved_ids[department],)
        )

        score, status = dm.c.fetchone()

        check(
            f"{department}: Resolved complaint not incremented",
            score == before[department]
            and status == "Resolved"
        )

    verify_json()


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

        test_display_customer_history()

        test_update_all_scores()

        test_resolved_batch()

    except Exception as error:
        failed += 1

        print(f"\n[ERROR] Test stopped: {error}")

        import traceback
        traceback.print_exc()

    finally:
        print("\n" + "=" * 50)
        print("FINAL TEST SUMMARY")
        print("=" * 50)

        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total: {passed + failed}")

        if failed == 0:
            print("\nALL CHECKS PASSED!")
        else:
            print("\nSOME CHECKS FAILED!")

        dm.db.close()


if __name__ == "__main__":
    run_tests()
