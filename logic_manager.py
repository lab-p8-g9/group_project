from datetime import datetime


priority_score = 3
date_created = datetime(2026, 10, 5)


current_date = datetime.now()


days_passed = (current_date.date() - date_created.date()).days


if days_passed <= 0:
    new_priority = priority_score

elif days_passed >= 1:
    new_priority = priority_score + days_passed


if new_priority > 8:
    new_priority = 8

print("Original Priority:", priority_score)
print("Days Passed:", days_passed)
print("Current Priority:", new_priority)