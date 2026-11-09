import sqlite3
from Data_manager.all_emails import Email
from Data_manager.data_manager2 import db, c, refresh_top_10

class TechE(Email):
    def __init__(self, id, category, address, subject, content, datetime, deadline, ps):

        super().__init__(address, subject, content, datetime)

        if not isinstance(category, str) or not category.strip():
            raise ValueError("Invalid complaint category.")

        if type(ps) is not int or not 1 <= ps <= 8:
            raise ValueError("Priority score must be between 1 and 8.")

        self.id = id
        self._category = category
        self._deadline = deadline
        self._ps = ps
        self._us = ps

    @property
    def category(self):
        return self._category

    @property
    def deadline(self):
        return self._deadline

    @property
    def ps(self):
        return self._ps

    @property
    def us(self):
        return self._us

    def add_to_DB(self): #adds email to Tech_Professionals table in db
        if self.id is None:
            raise ValueError("Original email must be saved first.")

        try:
            c.execute(
                "SELECT ComplaintID FROM Emails WHERE ComplaintID = ?",
                (self.id,)
            )

            if c.fetchone() is None:
                raise ValueError("Original email does not exist.")

            c.execute(
                """
                INSERT INTO Tech_Professionals
                (ComplaintID, Address, Category, Content, Datetime,
                Deadline, PriorityScore, UpdatedScore, Status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.id, self.address, self.category,
                    self.content, self.datetime, self.deadline,
                    self.ps, self.us, self.status
                )
            )

            db.commit()

        except (sqlite3.DatabaseError, ValueError):
            db.rollback()
            raise

        if not refresh_top_10("Tech"):
            raise RuntimeError(
                "Complaint saved, but Tech JSON refresh failed."
            )

        return self.id

    def get_email(self): #retrieves all info for ONE email
        c.execute('''SELECT * FROM Tech_Professionals 
                    WHERE ComplaintID = ?''', (self.id,))
        return c.fetchone()

    def update_score(self):
        try:
            c.execute(
                '''SELECT Status, UpdatedScore
                FROM Tech_Professionals
                WHERE ComplaintID = ?''',
                (self.id,)
            )

            result = c.fetchone()

            if result is None:
                raise ValueError(f"Complaint {self.id} not found.")

            status, current_score = result

            if status == 'Resolved' or current_score >= 8:
                self._us = current_score
                return False

            new_score = current_score + 1

            c.execute(
                '''UPDATE Tech_Professionals
                SET UpdatedScore = ?
                WHERE ComplaintID = ?
                AND Status = 'Unresolved'
                AND UpdatedScore = ?''',
                (new_score, self.id, current_score)
            )

            if c.rowcount == 0:
                raise RuntimeError("Complaint was modified concurrently.")

            db.commit()
            self._us = new_score

        except (sqlite3.DatabaseError, ValueError, RuntimeError):
            db.rollback()
            raise

        if not refresh_top_10('Tech'):
            raise RuntimeError(
                "Priority updated, but Tech JSON refresh failed."
            )

        return True
    
    def resolve(self):
        try:
            c.execute(
                '''UPDATE Tech_Professionals
                SET Status = ?
                WHERE ComplaintID = ?''',
                ('Resolved', self.id)
            )

            if c.rowcount == 0:
                raise ValueError(f"Complaint {self.id} not found.")

            db.commit()
            self.status = 'Resolved'

        except (sqlite3.DatabaseError, ValueError):
            db.rollback()
            raise

        if not refresh_top_10('Tech'):
            raise RuntimeError(
                "Complaint resolved, but Tech JSON refresh failed."
            )

        return True

    def unresolve(self):
        try:
            c.execute(
                '''UPDATE Tech_Professionals
                SET Status = ?
                WHERE ComplaintID = ?''',
                ('Unresolved', self.id)
            )

            if c.rowcount == 0:
                raise ValueError(f"Complaint {self.id} not found.")

            db.commit()
            self.status = 'Unresolved'

        except (sqlite3.DatabaseError, ValueError):
            db.rollback()
            raise

        if not refresh_top_10('Tech'):
            raise RuntimeError(
                "Complaint reopened, but Tech JSON refresh failed."
            )

        return True

    def load_first_10(self): 
        c.execute('''SELECT * FROM Tech_Professionals 
                    WHERE Status = 'Unresolved'
                    ORDER BY UpdatedScore DESC, Datetime ASC, ComplaintID ASC
                    LIMIT 10''')
        return c.fetchall()

    def load_all_unresolved(self):
        c.execute('''SELECT * FROM Tech_Professionals 
                    WHERE Status = 'Unresolved'
                    ORDER BY UpdatedScore DESC, Datetime ASC, ComplaintID ASC''')
        results = c.fetchall()
        return results

    def load_all_resolved(self):
        c.execute('''SELECT * FROM Tech_Professionals 
                    WHERE Status = 'Resolved'
                    ORDER BY UpdatedScore DESC, Datetime ASC, ComplaintID ASC''')
        results = c.fetchall()
        return results
