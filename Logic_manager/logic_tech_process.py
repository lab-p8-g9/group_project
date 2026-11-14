from Data_manager.tech_emails import TechE
from Logic_manager.logic_process import logic_process
from Logic_manager.logic_deadline_classification import Logic_Deadline_Classification



class logic_tech_process(logic_process):
    
    def __init__(self, email_address, subject, content, date_time, category, priority_score, assigned_to, new_score, deadline, id):
         super().__init__(email_address, subject, content, date_time, category, priority_score, assigned_to)
         self.id = id
         self.new_score = new_score
         self.deadline = deadline


    def process_data(self):
            
            tech_sample = TechE(self.id, 
                           self.category, 
                           self.email_address, 
                           self.subject, 
                           self.content, 
                           self.date_time, 
                           self.deadline, 
                           self.priority_score
                           )
            
            tech_sample.add_to_DB()
            tech_sample.update_score(self.new_score)


    def get_classified_results(self):
         process  = Logic_Deadline_Classification(self.priority_score, self.date_time)
         updated_score, deadline = process.classification()
         return updated_score, deadline
