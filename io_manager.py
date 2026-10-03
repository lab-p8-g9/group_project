from datetime import datetime
emailContent = []

def receiveEmails():
    while True:
        try:
            customerID = int(input("Enter the customer ID: "))
            if customerID == 0:
                print("Customer ID cannot be zero. Please try again.")
                continue
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a valid customer ID.")
    subject = input("Enter the email subject: ")
    body = input("Enter the email body: ")
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emailContent.append({
        "customerID": customerID,
        "date": date,
        "subject": subject,
        "body": body
    })

while(True):
    receiveEmails()