from data_manager import save_to_SQL, load_from_SQL
from ai_manager import analyse_complaint

def initialize():
    print("---------------------------------")
    print("Welcome to AI Complaint Classifier")
    print("---------------------------------")

# collect summary of what happened in the I/O Manager
def summary(updates,actions=""):
    if(updates == "Update"):
        log.append(actions)
    elif(updates == "Fetch"):
        i=1
        print("Summary:\n")
        for history in log:
            print(f"{i}){history}")
            i+=1

# Validate that the input format is correct
def validate_user_input(email, password):

    # Validate email format
    if not email or '@' not in email:
        # added to log to display summary at the end
        summary("Update", "User entered a invalid email")
        return "Error: Invalid email format."

    # Validate password complexity, must contain at least 12 character, 1 uppercase and lowercase, 1 symbol and number
    if (not password or len(password) < 12 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password) or not any(char.islower() for char in password) or not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password)):
        # added to log to display summary at the end
        summary("Update", "User enter a invalid password")
        return ("Error: Password must be at least 12 characters long and include at least one number, "
                "one uppercase letter, one lowercase letter, and one special character.")

    return "Valid input."

#WORKS
def createAccount():
    while True:
        try:
            email = input("Please input your email here: ")
            password = input("Please input your password: ")
            validation = validate_user_input(email, password)
            userInput[0] = email
            userInput[1] = password
            result = save_to_SQL("Accounts", userInput)
            if result == "User already exists":
                summary("Update", "Email already in Use")
                raise ValueError(result)
            elif validation != "Valid input.":
                summary("Update", validation)
                raise ValueError(validation)
        except ValueError as e:
            print(e)
            continue
        else:
            summary("Update", "User created new account/ login successfule")
            print("Account successfully created/ Login Successful\n")
            break
            

def inputComplaint():
    if (userInput[0] == "" or userInput[1] == ""):
        summary("Update", "User tried to send complaint without login")
        print("Please Login first\n")
    else:
        subject = input("Please type subject of your email: ")
        complaint = input("Please type your complaint: ")
        summary("Update", "AI_manager is analyzing whether complaint is valid")
        print("AI is starting its analysis")
        AI_result = analyse_complaint(subject, complaint)
        print("AI analysis ended")
        if(0 < AI_result[1] < 9):
            summary("Update", "User complaint sent successfully")
            #logicManagerFunction(AI_result)
            print("Not spam")
        elif(AI_result[1] == 0):
            summary("Update", "Complaint is invalid/spam")
            print("Invalid Complaint or Spam")

def loadSQL():
    tables = int(input("Choose which table to load(Admin (1) or Tech (2)): "))
    match tables:
        case 1:
            summary("Update", "Loaded data from Admin_Team in SQL")
            load_from_SQL("Admin_Team")
        case 2:
            summary("Update", "Loaded data from Tech_Professionals in SQL")
            load_from_SQL("Tech_Professionals")

def Menu():
    # load from JSON
    print("Below are your options(1,2,3,4,5):")
    print("Option 1: Login/Create Account")
    print("Option 2: Input Complaint")
    print("Option 3: Load SQL") #admin, tech
    print("Option 4: Fetch Summary Log")
    print("Option 5: End the program")
    options = int(input("Please input your option here: "))
    return options

initialize()
log = []
userInput = ["", ""]
choices = Menu()

while (choices != 5):
    match choices:
        case 1:
            createAccount()
        case 2:
            inputComplaint()
        case 3:
            loadSQL()
        case 4:
            summary("Fetch")
    choices = Menu()
summary("Fetch")