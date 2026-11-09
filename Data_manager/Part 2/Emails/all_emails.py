#parent class 
import sqlite3
from abc import ABC, abstractmethod 
from accounts import Account 
from Data_manager.data_manager2 import db, c

class Email(ABC): #creates email
    def __init__(self, address, subject, content, datetime):
        self.address = address
        self.subject = subject
        self.content = content
        self.datetime = datetime 
        self.status = 'Unresolved'

    @property
    def status(self):
        self._status

    @status.setter
    def status(self, value):
        if value not in ('Resolved', 'Unresolved'):
            raise ValueError("Invalid complaint status.")
        self._status = value

    def add_to_DB(self): #child classes need, add to Emails table
        c.execute('''INSERT INTO Emails(Address, Subject, Content, Datetime) VALUES(?,?,?,?)''',
                  (self.address, self.subject, self.content, self.datetime))
        self.id = c.lastrowid
        db.commit()
        return self.id 

    def get_email(self): #child classes need
        c.execute('''SELECT * 
                    FROM Emails         
                    WHERE ComplaintID = ?''', (self.id,))
        data = c.fetchone()
        return data 

    def add_to_AI_C_A(self, category, ps, assignedto):
        if getattr(self, 'id', None) is None:
            raise ValueError("Email must be saved first.")
        
        if type(ps) is not int or not 1 <= ps <= 8:          
            raise ValueError("Priority score must be between 1 and 8.")

        if not isinstance(category, str) or not category.strip():
            raise ValueError("Invalid category.")

        if assignedto not in ('Admin', 'Tech'):
            raise ValueError("Invalid department.")

        c.execute('''INSERT INTO AI_Complaint_Analysis VALUES (?, ?, ?, ?)''',
                    (self.id, category, ps, assignedto))

        db.commit() 
    
    @abstractmethod
    def update_score(self): #child classes need
        pass

    @abstractmethod
    def resolve(self): #child classes need
        pass

    @abstractmethod
    def unresolve(self): #child classes need
        pass

    @abstractmethod
    def load_first_10(self): #child classes need
        pass

    @abstractmethod
    def load_all_unresolved(self):
        pass

    @abstractmethod
    def load_all_resolved(self):
        pass
