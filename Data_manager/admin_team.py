#child class 1
from Data_manager.complaint_email import Email
from Data_manager.complaint_email import Account 
from abc import ABC, abstractmethod
from Data_manager.data_manager2 import db, c, refresh_top_10

class Admin(Email):
    def __init__(self, id, category, address, subject, content, datetime, deadline, ps):
        super().__init__(address, subject, content, datetime)
        
        self.id = id
        self.category = category
        self.deadline = deadline 
        self.ps = ps
        self.us = ps 

    def add_to_DB(self): #override parent's add_to_DB()
        c.execute('''INSERT INTO Admin_Team VALUES(?,?,?,?,?,?,?,?,?)''',
                   (self.id, 
                    self.address, 
                    self.category, 
                    self.content, 
                    self.datetime, 
                    self.deadline, 
                    self.ps, 
                    self.us, 
                    self.status))

        db.commit()
        if not refresh_top_10('Admin'):
            raise RuntimeError(
                "Database updated, but Admin JSON refresh failed."
            )

    def get_email(self):
        c.execute('''SELECT * FROM Admin_Team 
                    WHERE ComplaintID = ?''', (self.id,))
        return c.fetchone()

    def update_score(self):
        c.execute(
            '''SELECT Status, UpdatedScore
            FROM Admin_Team
            WHERE ComplaintID = ?''',
            (self.id,)
        )

        result = c.fetchone()

        if result is None:
            raise ValueError(f"Complaint {self.id} not found.")

        status, current_score = result

        if status == 'Resolved' or current_score >= 8:
            return

        new_score = current_score + 1

        c.execute(
            '''UPDATE Admin_Team
            SET UpdatedScore = ?
            WHERE ComplaintID = ?
            AND Status = 'Unresolved'
            AND UpdatedScore = ?''',
            (new_score, self.id, current_score)
        )

        if c.rowcount == 0:
            db.rollback()
            raise RuntimeError("Complaint was modified concurrently.")

        db.commit()
        self.us = new_score

        if not refresh_top_10('Admin'):
            raise RuntimeError("Priority updated, but JSON refresh failed.")
        
    def resolve(self):
        c.execute('''UPDATE Admin_Team 
                    SET Status = ?
                    WHERE ComplaintID = ?''',
                    ('Resolved', self.id))

        if c.rowcount == 0:
            db.rollback()
            raise ValueError(f"Complaint {self.id} not found.")

        db.commit()
        self.status = 'Resolved'

        if not refresh_top_10('Admin'):
            raise RuntimeError("Complaint resolved, but JSON refresh failed.")

    def unresolve(self):
        c.execute('''UPDATE Admin_Team 
                    SET Status = ?
                    WHERE ComplaintID = ?''',
                    ('Unresolved', self.id))

        if c.rowcount == 0:
            db.rollback()
            raise ValueError(f"Complaint {self.id} not found.")
        
        db.commit()
        self.status = 'Unresolved'
        
        if not refresh_top_10('Admin'):
            raise RuntimeError("Complaint reopened, but JSON refresh failed.")
        

    def load_first_10(self):
        c.execute('''SELECT * FROM Admin_Team 
                    WHERE Status = 'Unresolved'
                    ORDER BY UpdatedScore DESC, Datetime ASC
                    LIMIT 10''')
        return c.fetchall()

    def load_all_unresolved(self):
        c.execute('''SELECT * FROM Admin_Team 
                    WHERE Status = 'Unresolved'
                    ORDER BY UpdatedScore DESC, Datetime ASC''')
        results = c.fetchall()
        return results

    def load_all_resolved(self):
        c.execute('''SELECT * FROM Admin_Team 
                    WHERE Status = 'Resolved'
                    ORDER BY UpdatedScore DESC, Datetime ASC''')
        results = c.fetchall()
        return results
