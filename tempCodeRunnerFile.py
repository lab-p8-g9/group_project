from sqlite3 import connect
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
        c.execute('''INSERT INTO Accounts VALUES(?, ?)''', (list_of_data[0], list_of_data[1]))

    elif table_name == 'Emails': #5 data
        c.execute('''INSERT INTO Emails VALUES(?, ?, ?, ?, ?)''', (None, list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3]))

    elif table_name == 'AI_Complaint_Analysis': #4 data
        c.execute('''INSERT INTO AI_Complaint_Analysis VALUES(?, ?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3]))

    elif table_name == 'Admin_Team': #6 data
        c.execute('''INSERT INTO Admin_Team VALUES(?, ?, ?, ?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3], list_of_data[4], list_of_data[5]))

    elif table_name == 'Tech_Professionals': #6 data
        c.execute('''INSERT INTO Tech_Professionals VALUES(?, ?, ?, ?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3], list_of_data[4], list_of_data[5]))

    else:
        print('Invalid table name.')

    db.commit()
    db.close()

def save_to_JSON(complaints): #JSON is our backup database ; complaints is a LIST of DICTIONARIES 
    try:
        with open('complaints.json', 'w') as f:
            json.dump(complaints, f, indent=4)

    except (OSError, TypeError, ValueError) as e:
        print("Error saving JSON file:", e)
    

def load_from_JSON():
    try:
        with open('complaints.json', 'r') as file:
            records = json.load(file)

        if isinstance(records, list):
            return records
        else:
            print("Invalid JSON format.")
            return []

    except FileNotFoundError:
        print("complaints.json not found.")
        return []

    except json.JSONDecodeError:
        print("complaints.json is corrupted.")
        return []

    except OSError as e:
        print("Error loading JSON file:", e)
        return []

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
        return 'Email ' + str(email) + ' not found.'
    else:
        return 'Email ' + str(email) + ' found.'
   


#json: complaint id, user id, email, subject, content, datetime_sent

db.commit()
db.close()