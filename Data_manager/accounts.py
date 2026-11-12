import sqlite3
from abc import ABC, abstractmethod
from Data_manager.data_manager2 import db, c

class Account(ABC):
    VALID_ROLES = ("Admin", "Tech", "Customer")

    def __init__(self, address, password):
        if not isinstance(address, str) or not address.strip():
            raise ValueError("Address cannot be empty.")

        if not isinstance(password, str) or not password:
            raise ValueError("Password cannot be empty.")

        self._address = address.strip()
        self._pw = password
        self._role = self.assign_role()

    @property
    def address(self):
        return self._address

    @property
    def role(self):
        return self._role 

    @abstractmethod
    def assign_role(self):
        pass

    def set_account(self): #inserts account made into complaint.db - Accounts
        if self._role not in self.VALID_ROLES:
            print("Invalid account role.")

        try:
            c.execute(
                """
                INSERT INTO Accounts (Address, Password, Role)
                VALUES (?, ?, ?)
                """,
                (self._address, self._pw, self._role)
            )
            db.commit()
            return True

        except sqlite3.IntegrityError as error:
            db.rollback()
            raise ValueError(
                "Account already exists or violates a constraint."
            ) from error

        except sqlite3.DatabaseError:
            db.rollback()
            raise


    def get_account(self): #retrieves account info (address, pw, role) from complaint.db
        c.execute('''SELECT *
                    FROM Accounts 
                    WHERE Address = ?''', 
                    (self.address,))
        data = c.fetchone()

        if data == None: 
            print('Account not found.')
            return None
        return data  

    
        

