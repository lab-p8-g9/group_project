from c_all_emails import Email
from c_admin_emails import AdminE
from c_tech_emails import TechE
from datetime import datetime, timedelta
# ai_process classify objects into deadline classification 



class logic_data_process():
    def __init__(self, email_address, subject, content, category, priority_score, assigned_to):
          self.__email_address = email_address
          self.__subject = subject
          self.__content = content
          self.__category = category
          self.__priority_score = priority_score
          self.__assigned_to = assigned_to
          self.__current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_emails_object(self):

         object = Email(self.__email_address, self.__subject, self.__content, self.__current_datetime)
         id = object.add_to_DB()
         object.add_to_AI_C_A(self.__category, self.__priority_score, self.__assigned_to)
         return id

    def get_priority_score(self):
         return self.__priority_score

    def get_current_datetime(self):
         return self.__current_datetime



    def Tech_Admin_to_SQL(self, id, current_datetime, new_priority_score, deadline):
      category = self.__category
      email_address = self.__email_address
      subject = self.__subject
      content = self.__content
      priority_score = self.__priority_score

      if self.__assigned_to == "Tech_Professionals":
            object = TechE(id, category, email_address, subject, content, current_datetime, deadline, priority_score)
            object.add_to_DB()
            object.update_score(new_priority_score)

      elif self.__assigned_to == "Admin_Team":
            object = AdminE(id, category, email_address, subject, content, current_datetime, deadline, priority_score)
            object.add_to_DB()
            object.update_score(new_priority_score) 


