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
            if isinstance(list_of_data, list) and len(list_of_data) == 2:
                c.execute('''INSERT INTO Accounts VALUES(?, ?)''', (list_of_data[0], list_of_data[1]))
            else:
                print('Invalid input data.')
                db.close()
                return False
        except IntegrityError as e:
            db.rollback()

            if "UNIQUE" in str(e):
                c.execute('''SELECT (EXISTS (SELECT 1 FROM Accounts WHERE Address = ? AND Password = ?))''',(list_of_data[0], list_of_data[1]))
                result = c.fetchone()
                db.close()
                if (result[0] == 1):
                    return True
                else:
                    print('User already exists.')
                    return False 

            print("Database error:", e)
            db.close()
            return False
                    
    elif table_name == 'Emails': #1+4 data
        try:
            if isinstance(list_of_data, list) and len(list_of_data) == 4:
                c.execute('''INSERT INTO Emails VALUES(?, ?, ?, ?, ?)''', (None, list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3]))
            else:
                print('Invalid input data.')
                db.close()
                return False
        except (Error, IndexError, TypeError) as e:
            print('Failed to insert:', e)
            db.rollback()
            db.close()
            return False
            
    elif table_name == 'AI_Complaint_Analysis': #4 data
        try:
            if isinstance(list_of_data, list) and len(list_of_data) == 4:
                c.execute('''INSERT INTO AI_Complaint_Analysis VALUES(?, ?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3]))
            else:
                print('Invalid input data.')
                db.close()
                return False
        except (Error, IndexError, TypeError) as e:
            print('Failed to insert:', e)
            db.rollback()
            db.close()
            return False

    elif table_name == 'Admin_Team': #6 data
        try:
            if isinstance(list_of_data, list) and len(list_of_data) == 6:
                c.execute('''INSERT INTO Admin_Team VALUES(?, ?, ?, ?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3], list_of_data[4], list_of_data[5]))
            else:
                print('Invalid input data.')
                db.close()
                return False        
        except (Error, IndexError, TypeError) as e:
            print('Failed to insert:', e)
            db.rollback()
            db.close()
            return False

    elif table_name == 'Tech_Professionals': #6 data
        try:
            if isinstance(list_of_data, list) and len(list_of_data) == 6:
                c.execute('''INSERT INTO Tech_Professionals VALUES(?, ?, ?, ?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3], list_of_data[4], list_of_data[5]))
            else:
                print('Invalid input data.')
                db.close()
                return False
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
    print(table_name + ' table successfully updated!')
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
        print('Unable to load table.')
        return False 

    result = c.fetchall()

    db.close()
    print(result)
    return result

def save_to_JSON(complaint): #can handle one dict or list of dict
    try:
        complaints = load_from_JSON()

        if complaints is None:
            print('JSON file cannot be loaded.')
            return False

        if isinstance(complaint, dict):
            complaints.append(complaint)

        elif isinstance(complaint, list):
            for item in complaint:
                if not isinstance(item, dict):
                    print('Invalid complaint data.')
                    return False
                complaints.append(item)

        else:
            print('Invalid complaint data.')
            return False

        with open('complaint.json', 'w') as file:
            json.dump(complaints, file, indent=4)

        print('Complaint successfully added to JSON file.')
        return True

    except (OSError, TypeError, ValueError) as e:
        print('Error saving JSON file: ', e)
        return False
    
def load_from_JSON():
    try:
        with open('complaint.json', 'r') as file:
            records = json.load(file)

        if isinstance(records, list):
            return records
        else:
            print("Invalid JSON format.")
            return None

    except FileNotFoundError:
        print("complaint.json not found.")
        return []

    except json.JSONDecodeError:
        print("complaint.json is corrupted.")
        return None

    except OSError as e:
        print("Error loading JSON file:", e)
        return None

def new_JSON_section():
    try:
        with open('complaint.json', 'w') as file:
            json.dump([], file, indent=4)

        print('New JSON file created successfully.')
        return True

    except OSError as e:
        print('Unable to make new JSON file:', e)
        return False




#json: complaint id, email, subject, content, deadline

db.commit()
db.close()
