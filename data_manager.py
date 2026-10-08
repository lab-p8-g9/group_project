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

db.commit()
db.close()