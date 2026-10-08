# import sqlite3
from datetime import datetime



priority_score = 7
date_created = datetime(2026, 10, 5)
current_date = datetime.now()


def Deadline_Classification(priority_score,date_created, current_date):

    days_passed = (current_date.date() - date_created.date()).days
    

    if days_passed <= 0:
        new_priority = priority_score
    
    elif days_passed >= 1:
        new_priority = priority_score + days_passed
    
    if new_priority > 8:
        new_priority = 8
        
    return new_priority


new_priority = Deadline_Classification(priority_score, date_created, current_date)

print("Original Priority:", priority_score)
print("Current Priority:", new_priority)






