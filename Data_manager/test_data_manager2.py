
import sys
import sqlite3
import traceback
from pathlib import Path

# Allow imports from within Data_manager
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


# ---------------- TEST SETTINGS ----------------

CUSTOMER_EMAILS = [
    "alice@test.com",
    "bob@test.com",
    "charlie@test.com",
    "david@test.com",
    "emma@test.com"
]

DEPARTMENTS = {
    "Admin": "Admin_Team",
    "Tech": "Tech_Professionals"
}

passed = 0
failed = 0


# ---------------- TEST HELPERS ----------------

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
    table = DEPARTMENTS[department]

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

    customers = [
        CustomerA(address, "customer123")
        for address in CUSTOMER_EMAILS
    ]

    customers.append(
        CustomerA("customer@test.com", "customer123")
    )

    check("Admin role", admin.role == "Admin")
    check("Tech role", tech.role == "Tech")

    check(
        "Customer roles",
        all(customer.role == "Customer" for customer in customers)
    )

    for account in [admin, tech] + customers:
        existing = account.get_account()

        if existing is None:
            check(
                f"Create {account.address}",
                account.set_account() is True
            )
        else:
            check(
                f"Existing account {account.address}",
                existing[0] == account.address
                and existing[2] == account.role
            )

        # Verify get_account() returns the saved record
        data = account.get_account()

        check(
            f"get_account(): {account.address}",
            data is not None
            and data[0] == account.address
            and data[2] == account.role
        )

    check_exception(
        "Account is abstract",
        TypeError,
        lambda: Account("test@test.com", "123")
    )

    customer = customers[0]

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

    check_exception(
        "Empty password rejected",
        ValueError,
        lambda: CustomerA("test@test.com", "")
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

    data = email.get_email()

    check(
        "Retrieve original email",
        data is not None
        and data[0] == email_id
        and data[1] == email.address
        and data[2] == email.subject
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

    check_exception(
        "Reject invalid email address",
        ValueError,
        lambda: Email("", "Test", "Content", "2026-11-10")
    )

    check_exception(
        "Reject unsaved email retrieval",
        ValueError,
        lambda: Email(
            "customer@test.com",
            "Test",
            "Content",
            "2026-11-10"
        ).get_email()
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

    data = admin_email.get_email()

    check(
        "Retrieve Admin complaint",
        data is not None and data[0] == email_id
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
        dm.resolve(email_id) is True
        and get_status(email_id, "Admin") == "Resolved"
    )

    # Use the new external retrieval functions
    check(
        "Resolved Admin excluded from unresolved",
        all(
            row[0] != email_id
            for row in dm.load_all_unresolved("Admin")
        )
    )

    check(
        "Resolved Admin appears in resolved",
        any(
            row[0] == email_id
            for row in dm.load_all_resolved("Admin")
        )
    )

    check(
        "Resolving Admin complaint again keeps it resolved",
        dm.resolve(email_id) is True
        and get_status(email_id, "Admin") == "Resolved"
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

    data = tech_email.get_email()

    check(
        "Retrieve Tech complaint",
        data is not None and data[0] == email_id
    )

    check(
        "Increase Tech priority",
        tech_email.update_score() is True
        and tech_email.us == 6
    )

    check(
        "Resolve Tech complaint",
        dm.resolve(email_id) is True
        and get_status(email_id, "Tech") == "Resolved"
    )

    check(
        "Resolved Tech appears in resolved",
        any(
            row[0] == email_id
            for row in dm.load_all_resolved("Tech")
        )
    )

    check(
        "Resolved Tech excluded from unresolved",
        all(
            row[0] != email_id
            for row in dm.load_all_unresolved("Tech")
        )
    )

    check(
        "Resolving Tech complaint again keeps it resolved",
        dm.resolve(email_id) is True
        and get_status(email_id, "Tech") == "Resolved"
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
    created_by_customer = {
        address: [] for address in CUSTOMER_EMAILS
    }

    for i, (subject, content, score, department) in enumerate(
        test_complaints
    ):
        address = CUSTOMER_EMAILS[i % len(CUSTOMER_EMAILS)]

        email = Email(
            address,
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

        email.add_to_AI_C_A(category, score, department)

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
        created_by_customer[address].append(complaint_id)

        print(
            f"Added {i + 1:02d}/30 | "
            f"ID: {complaint_id} | "
            f"Customer: {address} | "
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

    return created_ids, created_by_customer


# ---------------- DATABASE VERIFICATION ----------------

def verify_database(created_ids):
    print("\n===== DATABASE VERIFICATION =====")

    for department, table in DEPARTMENTS.items():
        ids = created_ids[department]
        placeholders = ",".join("?" for _ in ids)

        for table_name, description in [
            ("Emails", "original emails"),
            ("AI_Complaint_Analysis", "AI analyses"),
            (table, "departmental complaints")
        ]:
            dm.c.execute(
                f'''
                SELECT COUNT(*)
                FROM {table_name}
                WHERE ComplaintID IN ({placeholders})
                ''',
                ids
            )

            check(
                f"{department}: 15 {description} saved",
                dm.c.fetchone()[0] == 15
            )

        dm.c.execute(
            f'''
            SELECT COUNT(*)
            FROM {table}
            WHERE ComplaintID IN ({placeholders})
            AND Status = 'Unresolved'
            ''',
            ids
        )

        check(
            f"{department}: 15 complaints unresolved",
            dm.c.fetchone()[0] == 15
        )


# ---------------- DEPARTMENT RETRIEVAL TESTS ----------------

def test_department_load_functions():
    print("\n===== DEPARTMENT RETRIEVAL TESTS =====")

    for department, table in DEPARTMENTS.items():
        top_10 = dm.load_first_10(department)
        unresolved = dm.load_all_unresolved(department)
        resolved = dm.load_all_resolved(department)

        check(
            f"{department}: Top 10 returns a list",
            isinstance(top_10, list)
        )

        check(
            f"{department}: Top 10 contains at most 10",
            len(top_10) <= 10
        )

        check(
            f"{department}: Top 10 matches unresolved list",
            top_10 == unresolved[:10]
        )

        check(
            f"{department}: Unresolved returns a list",
            isinstance(unresolved, list)
        )

        check(
            f"{department}: Resolved returns a list",
            isinstance(resolved, list)
        )

        check(
            f"{department}: Unresolved statuses correct",
            all(row[8] == "Unresolved" for row in unresolved)
        )

        check(
            f"{department}: Resolved statuses correct",
            all(row[8] == "Resolved" for row in resolved)
        )

        dm.c.execute(f"SELECT COUNT(*) FROM {table}")
        total = dm.c.fetchone()[0]

        check(
            f"{department}: All complaints accounted for",
            len(unresolved) + len(resolved) == total
        )

        check(
            f"{department}: Unresolved sorted correctly",
            all(
                (
                    -unresolved[i][7],
                    unresolved[i][4],
                    unresolved[i][0]
                ) <= (
                    -unresolved[i + 1][7],
                    unresolved[i + 1][4],
                    unresolved[i + 1][0]
                )
                for i in range(len(unresolved) - 1)
            )
        )

    check_exception(
        "Reject invalid department for top 10",
        ValueError,
        lambda: dm.load_first_10("Invalid")
    )

    check_exception(
        "Reject invalid department for unresolved",
        ValueError,
        lambda: dm.load_all_unresolved("Invalid")
    )

    check_exception(
        "Reject invalid department for resolved",
        ValueError,
        lambda: dm.load_all_resolved("Invalid")
    )


# ---------------- JSON TESTS ----------------

def verify_json():
    print("\n===== JSON VERIFICATION =====")

    for department, table in DEPARTMENTS.items():
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
            f"{department}: JSON contains correct number",
            len(records) == len(expected_ids)
        )

        check(
            f"{department}: JSON matches SQLite top 10",
            actual_ids == expected_ids
        )

        check(
            f"{department}: JSON sorted correctly",
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


def test_json_functions():
    print("\n===== JSON FUNCTION TESTS =====")

    for department in DEPARTMENTS:
        records = dm.load_from_JSON(department)

        check(
            f"{department}: load_from_JSON works",
            isinstance(records, list)
        )

        check(
            f"{department}: refresh_top_10 works",
            dm.refresh_top_10(department) is True
        )

        check(
            f"{department}: save_to_JSON works",
            dm.save_to_JSON(department, records) is True
        )

    check_exception(
        "Reject invalid JSON department",
        ValueError,
        lambda: dm.load_from_JSON("Invalid")
    )

    check_exception(
        "Reject more than 10 JSON complaints",
        ValueError,
        lambda: dm.save_to_JSON("Admin", [{}] * 11)
    )

    check_exception(
        "Reject non-list JSON data",
        TypeError,
        lambda: dm.save_to_JSON("Admin", {})
    )

    check_exception(
        "Reject invalid complaint dictionary",
        ValueError,
        lambda: dm.validate_complaint({})
    )


# ---------------- CUSTOMER HISTORY TESTS ----------------

def test_customer_history(created_by_customer, initial_ids):
    print("\n===== CUSTOMER HISTORY TESTS =====")

    for address in CUSTOMER_EMAILS:
        complaints = dm.load_customer_complaints(address)

        if not isinstance(complaints, list):
            check(f"{address}: History returns a list", False)
            continue

        actual_ids = {row[0] for row in complaints}
        expected_ids = set(created_by_customer[address])

        check(
            f"{address}: Contains all 6 new complaints",
            expected_ids.issubset(actual_ids)
            and len(expected_ids) == 6
        )

        check(
            f"{address}: No other customer complaints",
            all(row[1] == address for row in complaints)
        )

        check(
            f"{address}: Each record has 6 fields",
            all(len(row) == 6 for row in complaints)
        )

        check(
            f"{address}: Valid statuses",
            all(
                row[5] in ("Resolved", "Unresolved")
                for row in complaints
            )
        )

        check(
            f"{address}: ComplaintID descending",
            all(
                complaints[i][0] > complaints[i + 1][0]
                for i in range(len(complaints) - 1)
            )
        )

        # Verify status against the department table
        correct_status = True

        for complaint in complaints:
            cid = complaint[0]

            dm.c.execute('''
                SELECT AssignedTo
                FROM AI_Complaint_Analysis
                WHERE ComplaintID = ?
            ''', (cid,))

            result = dm.c.fetchone()

            if result is None:
                expected_status = "Unresolved"
            else:
                expected_status = get_status(cid, result[0])

                if expected_status is None:
                    expected_status = "Unresolved"

            if complaint[5] != expected_status:
                correct_status = False

        check(
            f"{address}: Status matches SQLite",
            correct_status
        )

    initial = dm.load_customer_complaints("customer@test.com")

    check(
        "Initial customer complaints preserved",
        isinstance(initial, list)
        and set(initial_ids).issubset(
            {row[0] for row in initial}
        )
    )

    check(
        "Unknown customer returns empty list",
        dm.load_customer_complaints("unknown@test.com") == []
    )


# ---------------- DISPLAY CUSTOMER HISTORY ----------------

def display_customer_history():
    print("\n===== CUSTOMER COMPLAINT HISTORY =====")

    for address in CUSTOMER_EMAILS:
        complaints = dm.load_customer_complaints(address)

        if not isinstance(complaints, list):
            print(f"[ERROR] Cannot load history for {address}")
            continue

        print("\n" + "=" * 50)
        print(f"Customer: {address}")
        print(f"Total complaints: {len(complaints)}")
        print("=" * 50)

        for complaint in complaints:
            print(f"Complaint ID : {complaint[0]}")
            print(f"Address      : {complaint[1]}")
            print(f"Subject      : {complaint[2]}")
            print(f"Content      : {complaint[3]}")
            print(f"Datetime     : {complaint[4]}")
            print(f"Status       : {complaint[5]}")
            print("-" * 50)


# ---------------- INDIVIDUAL SCORE UPDATE TESTS ----------------

def test_update_complaint_score(created_ids):
    print("\n===== INDIVIDUAL SCORE UPDATE TESTS =====")

    for department, table in DEPARTMENTS.items():
        # Select a newly created, unresolved complaint with room to increase.
        ids = created_ids[department]
        placeholders = ",".join("?" for _ in ids)
        dm.c.execute(f"""
            SELECT ComplaintID, UpdatedScore, PriorityScore
            FROM {table}
            WHERE ComplaintID IN ({placeholders})
              AND Status = 'Unresolved'
              AND UpdatedScore < 8
            ORDER BY ComplaintID
            LIMIT 1
        """, ids)
        target = dm.c.fetchone()
        check(f"{department}: Eligible test complaint exists", target is not None)
        if target is None:
            continue

        cid, old_score, priority = target
        before = get_scores(table)
        new_score = old_score + 1
        dm.update_complaint_score(department, cid, new_score)
        after = get_scores(table)

        check(f"{department}: Requested score saved", after[cid]["UpdatedScore"] == new_score)
        check(f"{department}: Original PriorityScore unchanged", after[cid]["PriorityScore"] == priority)
        check(f"{department}: Status unchanged", after[cid]["Status"] == "Unresolved")
        check(f"{department}: Other complaints unchanged",
              all(after[k] == before[k] for k in before if k != cid))

        # The current update_complaint_score() does not refresh JSON itself.
        # Refresh explicitly here so subsequent JSON verification is meaningful.
        check(f"{department}: Manual JSON refresh succeeds",
              dm.refresh_top_10(department) is True)

    check_exception(
        "Invalid department rejected for score update",
        ValueError,
        lambda: dm.update_complaint_score("Invalid", 1, 5)
    )
    verify_json()


# ---------------- RESOLVED BATCH TEST ----------------

def test_resolved_batch():
    print("\n===== RESOLVED BATCH TEST =====")

    resolved_ids = {}

    for department in DEPARTMENTS:
        email = Email(
            "customer@test.com",
            f"Resolved Test {department}",
            "Testing resolved complaint behaviour.",
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
        check(
            f"{department}: External resolve() succeeds",
            dm.resolve(cid) is True
            and get_status(cid, department) == "Resolved"
        )

        resolved_ids[department] = cid

    before = {}

    for department, table in DEPARTMENTS.items():
        dm.c.execute(
            f'''
            SELECT UpdatedScore
            FROM {table}
            WHERE ComplaintID = ?
            ''',
            (resolved_ids[department],)
        )

        before[department] = dm.c.fetchone()[0]

    for department, table in DEPARTMENTS.items():
        check_exception(
                f"{department}: Cannot update resolved complaint",
                ValueError,
                lambda: dm.update_complaint_score(
                    department,
                    resolved_ids[department],
                    7
                ))
        
    for department, table in DEPARTMENTS.items():
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
            f"{department}: Resolved complaint score unchanged",
            score == before[department]
            and status == "Resolved"
        )

    verify_json()


def test_resolve_invalid_id():
    print("\n===== RESOLVE ERROR TESTS =====")

    dm.c.execute("SELECT MAX(ComplaintID) FROM Emails")
    maximum_id = dm.c.fetchone()[0] or 0
    missing_id = maximum_id + 1000

    check_exception(
        "Resolving nonexistent complaint raises ValueError",
        ValueError,
        lambda: dm.resolve(missing_id)
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

        created_ids, created_by_customer = test_30_complaints()

        verify_database(created_ids)

        test_department_load_functions()

        verify_json()

        test_json_functions()

        test_customer_history(
            created_by_customer,
            [email_id, tech_id]
        )

        display_customer_history()

        test_update_complaint_score(created_ids)

        test_resolved_batch()

        test_resolve_invalid_id()

    except Exception as error:
        failed += 1
        print(f"\n[ERROR] Test stopped: {error}")
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

        try:
            dm.c.close()
        except sqlite3.ProgrammingError:
            pass

        dm.db.close()


if __name__ == "__main__":
    run_tests()
