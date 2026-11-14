import sqlite3
from Data_manager.all_emails import Email
from Data_manager.data_manager2 import db, c, refresh_top_10

class AdminE(Email):
    def __init__(self, id: int | None, category: str, address: str, subject: str, content: str, datetime: str, deadline: str, ps: int) -> None:

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
    def category(self) -> str:
        return self._category

    @property
    def deadline(self) -> str:
        return self._deadline

    @property
    def ps(self) -> int:
        return self._ps

    @property
    def us(self) -> int:
        return self._us

    def add_to_DB(self) -> int:
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
                INSERT INTO Admin_Team
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

        if not refresh_top_10("Admin"):
            raise RuntimeError(
                "Complaint saved, but Admin JSON refresh failed."
            )

        return self.id

    def get_email(self) -> tuple | None:
        c.execute('''SELECT * FROM Admin_Team 
                    WHERE ComplaintID = ?''', (self.id,))
        return c.fetchone()

    def update_score(self, us) -> bool:
        try:
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
                self._us = current_score
                return False

            new_score = us

            c.execute(
                '''UPDATE Admin_Team
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

        if not refresh_top_10('Admin'):
            raise RuntimeError(
                "Priority updated, but Admin JSON refresh failed."
            )

        return True
 