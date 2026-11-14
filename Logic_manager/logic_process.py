from abc import ABC, abstractmethod


class logic_process(ABC):
    
    def __init__(self, email_address, subject, content, date_time, category, priority_score, assigned_to):
         self.email_address = email_address
         self.subject = subject
         self.content = content
         self.date_time = date_time
         self.category = category
         self.priority_score = priority_score
         self.assigned_to = assigned_to

    @abstractmethod

    def process_data(self):
         pass
