from sqlite3 import *
from Data_manager.data_manager2 import db 

class Account:
    VALID_ROLES = ("Admin", "Tech", "Customer")

    def __init__(self, address, password):
        if not isinstance(address, str) or not address.strip():
            raise ValueError("Address cannot be empty.")

        if not isinstance(password, str) or not password:
            raise ValueError("Password cannot be empty.")
        
        self._address = address
        self._pw = password
        self._role = None 

    @property
    def address(self):
        return self._address

    @property
    def role(self):
        return self._role 

    def set_account(self): #inserts account made into complaint.db - Accounts
        try:
            c.execute('''INSERT INTO Accounts Address, Password, Role)
                        VALUES (?, ?, ?)''', (self._address, self._password, self._role))
            db.commit()

        except sqlite3.IntegrityError:
            db.rollback()
            raise ValueError("Account already exists.")

        except sqlite3.DatabaseError:
            db.rollback()
            raise

    def get_account(self): #retrieves account info (address, role) from complaint.db
        c.execute('''SELECT Address, Role FROM Accounts WHERE Address = ?''', (self.address,))
        return c.fetchone()

    
        

