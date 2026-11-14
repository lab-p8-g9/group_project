from Data_manager.all_emails import Email
from Logic_manager.logic_process import logic_process
from Logic_manager.logic_deadline_classification import Logic_Deadline_Classification



class logic_email_process(logic_process):
     
    def __init__(self, email_address, subject, content, date_time, category, priority_score, assigned_to):
     super().__init__(email_address, subject, content, date_time, category, priority_score, assigned_to)


    def process_data(self):

         email_sample = Email(self.email_address, self.subject, self.content, self.date_time)
         id = email_sample.add_to_DB()
         email_sample.add_to_AI_C_A(self.category, self.priority_score, self.assigned_to)
         return id

    def get_classified_results(self):
         process  = Logic_Deadline_Classification(self.priority_score, self.date_time)
         updated_score, deadline = process.classification()
         return updated_score, deadline
