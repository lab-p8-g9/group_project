
import json
from Logic_manager.logic_data_process import logic_data_process
from Logic_manager.logic_deadline_classification import Logic_Deadline_Classification


class logic_main():

    def __init__(self, ai_file):
        self.__ai_file = ai_file


    def process_ai_sample(self):

        with open(self.__ai_file, "r", encoding="utf-8") as file:
            samples = json.load(file)

        for item in samples:

            process = logic_data_process(
                item["email_address"],
                item["subject"],
                item["content"],
                item["category"],
                item["priority_score"],
                item["assigned_to"]
            )

            ID = process.add_emails_object()
            classification = Logic_Deadline_Classification(process.get_priority_score(),process.get_current_datetime())
            new_priority_score, deadline = (classification.classification())
            process.add_admin_tech_object(ID, process.get_current_datetime(), new_priority_score,deadline)

      
        self.clear_ai_sample()
        print("AI Sample processed Successfully!")

    
    def clear_ai_sample(self):

        with open(self.__ai_file, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)
