from datetime import datetime
from logic_manager import Logic_Deadline_Classification


# While our actual logic_manager access SQL files to excute Dealine_Classification and file sorting.
# This test script is strictly testing whether our deadline_Classification is working as expected. 
# SQL file handling functions are strictly not tested due to the nature of manipulating files!
#ExpectPriority score and ExpectedDealine are the last two corner of the test_data this data are being changed by Deadline_Classfication
#actual_priority and actual_deadline are the value we are supposed to update in the last two column of the test_data
#Thus, ExpectPriority and ExpectedDealine are use to compared to the return value of actual_priority abd actual_deadline


# ComplaintID, PriorityScore, Datetime, ExpectedPriority, ExpectedDeadline
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