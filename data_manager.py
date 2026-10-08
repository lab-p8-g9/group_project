from sqlite3 import * 

db = connect('complaint.db')
c = db.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS Accounts(
            UserID INTEGER, 
            Address TEXT, 
            Password TEXT,
            PRIMARY KEY(UserID));''')

c.execute('''CREATE TABLE IF NOT EXISTS Emails(
            ComplaintID INTEGER, 
            UserID INTEGER, 
            Email TEXT,
            Subject TEXT,
            Content TEXT,
            Datetime TEXT,
            PRIMARY KEY(ComplaintID),
            FOREIGN KEY(UserID) REFERENCES Accounts(UserID));''')

c.execute('''CREATE TABLE IF NOT EXISTS AI_Complaint_Analysis(
            ComplaintID INTEGER,
            Category TEXT,
            PriorityScore INTEGER,
            AssignedTo TEXT,
            FOREIGN KEY(ComplaintID) REFERENCES Emails(ComplaintID));''')

c.execute('''CREATE TABLE IF NOT EXISTS Admin_Team(
            ComplaintID INTEGER,
            Category TEXT,
            Deadline TEXT,
            FOREIGN KEY(ComplaintID) REFERENCES Emails(ComplaintID));''')

c.execute('''CREATE TABLE IF NOT EXISTS Tech_Professionals(
            ComplaintID INTEGER,
            Category TEXT,
            Deadline TEXT,
            FOREIGN KEY(ComplaintID) REFERENCES Emails(ComplaintID));''')

def add(table_name, list_of_data):
    if table_name == 'Accounts': #3 data
        c.execute('''INSERT INTO(?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2]))

    elif table_name == 'Emails': #6 data
        c.execute('''INSERT INTO(?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3], list_of_data[4], list_of_data[5]))

    elif table_name == 'AI_Complaint_Analysis': #4 data
        c.execute('''INSERT INTO(?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2], list_of_data[3]))

    elif table_name == 'Admin Team': #3 data
        c.execute('''INSERT INTO(?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2]))

    elif table_name == 'Tech Professionals': #3 data
        c.execute('''INSERT INTO(?, ?, ?)''', (list_of_data[0], list_of_data[1], list_of_data[2]))

db.commit()
db.close()