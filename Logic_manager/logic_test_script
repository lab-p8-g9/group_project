
from datetime import datetime, timedelta
from logic_deadline_classification import Logic_Deadline_Classification


today = datetime.now().replace(microsecond=0)

# Test cases: (priority_score, days_ago)
test_cases = [
    (3, 0),    # New task
    (3, 2),    # Priority increase
    (6, 5),    # Maximum priority
    (0, 0),    # Minimum priority
    (8, 0),    # Highest priority
    (2, 10),   # Overdue task
    (4, -2),   # Future task
]

passed = 0
failed = 0

for i, (priority_score, days_ago) in enumerate(test_cases, 1):

    date_created = today - timedelta(days=days_ago)
    date_string = date_created.strftime("%Y-%m-%d %H:%M:%S")

    task = Logic_Deadline_Classification(
        priority_score,
        date_string
    )

    new_priority, deadline_date = task.classification()

    # Expected results
    expected_priority = min(8, priority_score + max(0, days_ago))
    expected_deadline = date_created + timedelta(
        days=max(0, 8 - priority_score)
    )

    # Check PASS or FAIL
    if (new_priority == expected_priority and
            deadline_date == expected_deadline):
        result = "PASS"
        passed += 1
    else:
        result = "FAIL"
        failed += 1

    print(f"Test {i}: {result}")
    print(f"Original Priority: {priority_score}")
    print(f"Days Passed: {days_ago}")
    print(f"Expected Priority: {expected_priority}")
    print(f"Actual Priority: {new_priority}")
    print(f"Expected Deadline: {expected_deadline}")
    print(f"Actual Deadline: {deadline_date}")
    print("-" * 40)

print("TEST SUMMARY")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total: {len(test_cases)}")
