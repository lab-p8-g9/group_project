#parent class 
import sqlite3
from abc import ABC, abstractmethod 
from Data_manager.data_manager2 import db, c

class Account:
    def __init__(self, address, password):
        self.address = address
        self.pw = password

    def set_account(self):
        try:
            c.execute('''INSERT INTO Accounts VALUES(?,?)''',
                    (self.address, self.pw))
            db.commit()

        except sqlite3.IntegrityError:
            db.rollback()
            raise ValueError("Account already exists.")

        except sqlite3.DatabaseError:
            db.rollback()
            raise

    def get_account(self):
        c.execute('''SELECT * FROM Accounts WHERE Address = ?''', (self.address,))
        data = c.fetchone()
        return data

class Email(ABC): #creates email
    def __init__(self, address, subject, content, datetime):
        self.address = address
        self.subject = subject
        self.content = content
        self.datetime = datetime 
        self.status = 'Unresolved'

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
