from logic_deadline_classification import Logic_Deadline_Classification
from Data_manager.data_manager2 import load_all_unresolved, update_complaint_score
from Data_manager.tech_emails import TechE
from Data_manager.admin_emails import AdminE


class recalculate_logic_score:
    def __init__(self, department:str):
        self.__department = department

    def update_all_score(self):

        complaint = load_all_unresolved(self.__department)

        for item in complaint:
            id = item[0]
            current_datetime = item[4]
            priority_score = item[6]


            rows = Logic_Deadline_Classification(priority_score, current_datetime)
            new_priority_score, deadline  = rows.classification()
            update_complaint_score(self.__department, id, new_priority_score)
        
