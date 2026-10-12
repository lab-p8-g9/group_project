from datetime import datetime
from logic_manager import Logic_Deadline_Classification


# This test script focuses on the core priority and
# deadline calculation logic.
#
# Database operations and SQL sorting in logic_manager are outside
# the scope of these unit tests.
#
# Hardcoded test values are used to simulate
# priority scores without calling the live AI API.


# ComplaintID (input), PriorityScore (input), Datetime (input), ExpectedPriority, ExpectedDeadline
# Eg first data set has PriorityScore: 3 and the date created is 08 oct 2026
# if the function works it will have an updatescore as 5 and a due deadline date of 13 oct 2026

test_data = [
    (1, 3, "2026-10-08", 5, "2026-10-13"),
    (2, 5, "2026-10-07", 8, "2026-10-10"),
    (3, 7, "2026-10-09", 8, "2026-10-10")
]



current_date = datetime(2026, 10, 10)

for complaint_id, priority, date, expected_priority, expected_deadline in test_data:

    date_created = datetime.strptime(date, "%Y-%m-%d")

    actual_priority, actual_deadline = Logic_Deadline_Classification(
        priority, date_created, current_date
    )

    actual_deadline = actual_deadline.strftime("%Y-%m-%d")

    if actual_priority == expected_priority and actual_deadline == expected_deadline:
        print(f"Complaint {complaint_id}: PASS")
    else:
        print(f"Complaint {complaint_id}: FAIL")

