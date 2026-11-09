import sqlite3
from Data_manager.data_manager2 import db, c

class Email: #creates email
    def __init__(self, address, subject, content, datetime):
        if not isinstance(address, str) or not address.strip():
            raise ValueError("Invalid email address.")

        if not isinstance(subject, str):
            raise ValueError("Invalid subject.")

        if not isinstance(content, str):
            raise ValueError("Invalid email content.")

        if not isinstance(datetime, str) or not datetime.strip():
            raise ValueError("Invalid datetime.")

        self._id = None
        self._address = address.strip()
        self._subject = subject
        self._content = content
        self._datetime = datetime
        self._status = "Unresolved"

    @property
    def id(self):
        return self._id 

    @id.setter
    def id(self, value):
        if value is not None:
            if type(value) is not int or value <= 0:
                raise ValueError("Invalid complaint ID.")
        self._id = value

    @property
    def address(self):
        return self._address

    @property
    def subject(self):
        return self._subject

    @property
    def content(self):
        return self._content

    @property
    def datetime(self):
        return self._datetime

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in ('Resolved', 'Unresolved'):
            raise ValueError("Invalid complaint status.")
        self._status = value

    def add_to_DB(self): #save to Emails table in db
        try:
            c.execute('''INSERT INTO Emails(Address, Subject, Content, Datetime) 
                        VALUES(?,?,?,?)''',
                    (self.address, self.subject, self.content, self.datetime))
            self.id = c.lastrowid
            db.commit()
            return self.id 
        
        except sqlite3.DatabaseError:
            db.rollback()
            raise

    def get_email(self): #return all info of ONE email
        if self.id is None:
            raise ValueError("Email has not been saved.")
        
        c.execute('''SELECT * 
                    FROM Emails         
                    WHERE ComplaintID = ?''', (self.id,))
        data = c.fetchone()
        return data #CID, address, subject, content, datetime

    def add_to_AI_C_A(self, category, ps, assignedto): #save to AI_Complaint_Analysis table in db
        if self.id is None:
            raise ValueError("Email must be saved first.")

        if type(ps) is not int or not 1 <= ps <= 8:
            raise ValueError("Priority score must be 1 to 8.")

        if not isinstance(category, str) or not category.strip():
            raise ValueError("Invalid category.")

        if assignedto not in ("Admin", "Tech"):
            raise ValueError("Invalid department.")

        try:
            c.execute(
                """
                INSERT INTO AI_Complaint_Analysis
                (ComplaintID, Category, PriorityScore, AssignedTo)
                VALUES (?, ?, ?, ?)
                """,
                (self.id, category, ps, assignedto)
            )
            db.commit()
            return True

        except sqlite3.DatabaseError:
            db.rollback()
            raise
    