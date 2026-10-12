from sqlite3 import *
import json 

db = connect('complaint.db')
c = db.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS Accounts(
            Address TEXT, 
            Password TEXT,
            PRIMARY KEY(Address));''')

c.execute('''CREATE TABLE IF NOT EXISTS Emails(
            ComplaintID INTEGER, 
            Email TEXT,
            Subject TEXT,
            Content TEXT,
            Datetime TEXT,
            PRIMARY KEY(ComplaintID),
            FOREIGN KEY(Email) REFERENCES Accounts(Address));''')

c.execute('''CREATE TABLE IF NOT EXISTS AI_Complaint_Analysis(
            ComplaintID INTEGER,
            Category TEXT,
            PriorityScore INTEGER,
            AssignedTo TEXT,
            FOREIGN KEY(ComplaintID) REFERENCES Emails(ComplaintID));''')

c.execute('''CREATE TABLE IF NOT EXISTS Admin_Team(
            ComplaintID INTEGER,
            Category TEXT,
            Datetime TEXT,
            Deadline TEXT,
            PriorityScore INTEGER,
            UpdatedScore INTEGER,
            FOREIGN KEY(ComplaintID) REFERENCES Emails(ComplaintID));''')

c.execute('''CREATE TABLE IF NOT EXISTS Tech_Professionals(
            ComplaintID INTEGER,
            Category TEXT,
            Datetime TEXT,
            Deadline TEXT,
            PriorityScore INTEGER,
            UpdatedScore INTEGER,
            FOREIGN KEY(ComplaintID) REFERENCES Emails(ComplaintID));''')

def save_to_SQL(table_name, list_of_data): #SQL is our main database
    db = connect('complaint.db')
    c = db.cursor()

    if table_name == 'Accounts': #2 data
        try: 
            c.execute('''INSERT INTO Accounts VALUES(?, ?)''', (list_of_data[0], list_of_data[1]))
        except IntegrityError as e:
            db.rollback()
            db.close()

            if "UNIQUE" in str(e):
                return "User already exists"

            print("Database error:", e)
            return False
                    
    elif table_name == 'Emails': #5 data, save to json backup as well
        try:
            c.execute('''INSERT INTO Emails VALUES(?, ?, ?, ?, ?)''', (None, list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3]))

            complaint = {
                        'ComplaintID': c.lastrowid,
                        'Email': list_of_data[0],
                        'Subject': list_of_data[1],
                        'Content': list_of_data[2],
                        'Datetime': list_of_data[3]
                        }

            db.commit()

            if not save_to_JSON(complaint):
                print('Complaint saved to SQL, but JSON backup failed.')

        except (Error, IndexError, TypeError) as e:
            print('Failed to insert:', e)
            db.rollback()
            db.close()
            return False
            
    elif table_name == 'AI_Complaint_Analysis': #4 data
        try:
            c.execute('''INSERT INTO AI_Complaint_Analysis VALUES(?, ?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3]))
        except (Error, IndexError, TypeError) as e:
            print('Failed to insert:', e)
            db.rollback()
            db.close()
            return False

    elif table_name == 'Admin_Team': #6 data
        try:
            c.execute('''INSERT INTO Admin_Team VALUES(?, ?, ?, ?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3], list_of_data[4], list_of_data[5]))
        except (Error, IndexError, TypeError) as e:
            print('Failed to insert:', e)
            db.rollback()
            db.close()
            return False

    elif table_name == 'Tech_Professionals': #6 data
        try:
            c.execute('''INSERT INTO Tech_Professionals VALUES(?, ?, ?, ?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3], list_of_data[4], list_of_data[5]))
        except (Error, IndexError, TypeError) as e:
            print('Failed to insert:', e)
            db.rollback()
            db.close()
            return False

    else:
        print('Invalid table name.')
        db.close()
        return False

    db.commit()
    db.close()
    return True

def load_from_SQL(table_name):
    db = connect('complaint.db')
    c = db.cursor()

    if table_name == 'Admin_Team':
        c.execute('''SELECT * FROM Admin_Team''')

    elif table_name == 'Tech_Professionals':
        c.execute('''SELECT * FROM Tech_Professionals''')
    else:
        db.close()
        return False 

    result = c.fetchall()

    db.close()
    return result

def save_to_JSON(complaint): #JSON is our backup database ; complaint is a DICTIONARY
    try:
        complaints = load_from_JSON()

        if complaints is None:
            print("JSON backup not updated.")
            return False

        complaints.append(complaint)

        with open('complaints.json', 'w') as f:
            json.dump(complaints, f, indent=4)

        return True
    except (OSError, TypeError, ValueError) as e:
        print("Error saving JSON file:", e)
        return False
    
def load_from_JSON():
    try:
        with open('complaints.json', 'r') as file:
            records = json.load(file)

        if isinstance(records, list):
            return records
        else:
            print("Invalid JSON format.")
            return None

    except FileNotFoundError:
        print("complaints.json not found.")
        return []

    except json.JSONDecodeError:
        print("complaints.json is corrupted.")
        return None

    except OSError as e:
        print("Error loading JSON file:", e)
        return None

def search_complaint(complaint_id):
    db = connect('complaint.db')
    c = db.cursor()

    c.execute('''SELECT * FROM Emails
                WHERE ComplaintID = ?''', (complaint_id,))

    result = c.fetchone()

    db.close()

    if result == None:
        print("Complaint ID " + str(complaint_id) + " not found." )
        return None
    else:
        return result

def check_email_in_accounts(email):
    db = connect('complaint.db')
    c = db.cursor()

    c.execute(''' SELECT Address FROM Accounts
                WHERE Address = ?''', (email,))

    result = c.fetchone()

    db.close()

    if result == None:
        print('Email ' + str(email) + ' not found.')
        return False
    else:
        print('Email ' + str(email) + ' found.')
        return True
   


#json: complaint id, user id, email, subject, content, datetime_sent

db.commit()
db.close()
