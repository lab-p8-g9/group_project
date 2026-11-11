from data_manager2 import *
from datetime import datetime, timedelta
from Data_manager.all_emails import Email
from Data_manager.tech_emails import TechE
from Data_manager.admin_emails import AdminE
import os


# Ai json sample: email_address, subject, content, category, priorityscore, assignedto

# [sql] emails: complaintid, email, subject, content, datatime
# [sql] ai_complaint_analysis: complaintid, category, priorityscore, assignedto
# [sql] admin_team: compalintid, category, datatime, deadline, priorityscore, updatedpriorityscore
# [sql] tech_team: compalintid, category, datatime, deadline, priorityscore, updatedpriorityscore

# [transfer] emails: email, subject, content

#used class_emails.py, class_admin_team.py, class_tech_emails.py


def process_ai_sample(ai_file):
    with open(ai_file, "r", encoding="utf-8") as file:
        sample = json.load(file)
        
        for item in sample:
            ID, current_datetime = emails_AI_analysis_to_SQL(item)
            new_priority_score, deadline = Logic_Deadline_Classification(item, current_datetime)
            Tech_Admin_to_SQL(item, ID, current_datetime, new_priority_score, deadline)
        
        clear_ai_sample(ai_file)
        print("AI Sample processed Successfully!")




def clear_ai_sample(ai_file):
    with open(ai_file, "w", encoding="utf-8") as file:
        json.dump([], file, indent=4)

def emails_AI_analysis_to_SQL(item):

    email_address = item["email_address"]
    subject = item["subject"]
    content = item["content"]
    category = item["category"]
    priority_score = item["priority_score"]
    assigned_to = item["assigned_to"]
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    object = Email(email_address, subject, content, current_datetime)
    id = object.add_to_DB()
    object.add_to_AI_C_A(category, priority_score, assigned_to)
    
    return id, current_datetime



def Logic_Deadline_Classification(item, date_created):

    date_created = datetime.strptime(date_created, "%Y-%m-%d %H:%M:%S")
    priority_score = item["priority_score"]
    current_date = datetime.now()

    max_priority = 8
    min_priority = 0

    days_passed = (current_date.date() - date_created.date()).days

    if days_passed <= min_priority:
        new_priority = priority_score
    else:
        new_priority = priority_score + days_passed

    if new_priority > max_priority:
        new_priority = max_priority

    days_to_deadline = max(min_priority, max_priority - priority_score)
    deadline_date = date_created + timedelta(days=days_to_deadline)

    return new_priority, deadline_date



def Tech_Admin_to_SQL(item, id, current_datetime, new_priority_score, deadline):
    id1 = id
    category = item["category"]
    email_address = item["email_address"]
    subject = item["subject"]
    content = item["content"]
    priority_score = item["priority_score"]

    if item["assigned_to"] == "Tech_Professionals":
        object = TechE(id1, category, email_address, subject, content, current_datetime, deadline, priority_score)
        object.add_to_DB()
        object.update_score(new_priority_score)

    elif item["assigned_to"] == "Admin_Team":
        object = AdminE(id1, category, email_address, subject, content, current_datetime, deadline, priority_score)
        object.add_to_DB()
        object.update_score(new_priority_score) 



        
def Top10_List(table):
        
        refresh_top_10(table)
        data = load_from_JSON(table)
        return data


def display_Top10(data):
    for item in data:
        print(f"ComplaintID: {item["ComplaintID"]}")
        print(f"Address: {item["Address"]}")             
        print(f"Content: {item["Content"]}")           
        print(f"Deadline: {item["Deadline"]}")   
        print(f"UpdatedScore: {item["UpdatedScore"]}")   

