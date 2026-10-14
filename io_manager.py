#import external functions from the data_manger and ai_manager
from data_manager import save_to_SQL, load_from_SQL, load_from_JSON
from ai_manager import analyse_complaint, process_and_save_complaint

#log to store summary of what happened
log = []
#emailPass to store email and password
emailPass = ["677667", "ywdgywdg"]

#inititalize the Program
def initialize():
    print("---------------------------------")
    print("Welcome to AI Complaint Classifier")
    print("---------------------------------")
    print("This is the complaints from previous Session")
    result = load_from_JSON()
    print("\n")
    for complaint in result:
        print(f"Email: {complaint["Email"]}\nSubject: {complaint["Subject"]}\nContent: {complaint["Content"]}")
        print("-" * 20 + "\n")


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

    if (not email or '@' not in email) and (not password or len(password) < 12 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password) or not any(char.islower() for char in password) or not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password)):
        summary("Update", "Invalid email and password")
        return "Error: User enter an invalid email and password(min. 12 characters, 1 symbol, 1 number, 1 uppercase, 1 lowercase)"
    # Validate email format
    elif not email or '@' not in email:
        # added to log to display summary at the end
        summary("Update", "User entered an invalid email")
        return "Error: Invalid email format."

    # Validate password complexity, must contain at least 12 character, 1 uppercase and lowercase, 1 symbol and number
    elif (not password or len(password) < 12 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password) or not any(char.islower() for char in password) or not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password)):
        # added to log to display summary at the end
        summary("Update", "User enter a invalid password")
        return ("Error: Password must be at least 12 characters long and include at least one number, "
                "one uppercase letter, one lowercase letter, and one special character.")

    return "Valid input."

#function for user to login/ create account
def Account():
    # while True, try to input an email and password that exists or a valid new one then save to SQL
    while True:
        try:
            #request for user to input email and password
            email = input("Please input your email here: ")
            password = input("Please input your password: ")
            #call the validation input function
            validation = validate_user_input(email, password)
            #store the inputted email and password to the emailPass list
            emailPass[0] = email
            emailPass[1] = password
            #if user inputted an email or password or both in the wrong format
            if(validation != "Valid input."):
            # added to log to display summary at the end
                summary("Update", validation)
                raise ValueError(validation)    #raise the output from validation into ValueError
            else:
                result = save_to_SQL("Accounts", emailPass)
                #if user tries to input an email with the wrong password or 
                # trying to create new account with existing email
                if result == "User already exists":
                    # added to log to display summary at the end
                    summary("Update", "Email already in Use")
                    raise ValueError(result)    #raise the output from result if it gave an error into ValueError    
        #fall into except if ValueError
        except ValueError as e:
            print(e)    #print the value in ValueError
            continue    #go to next iteration
        else:   #else if user enter everything right
            # added to log to display summary at the end
            summary("Update", "User created new account/ login successful")
            print("Account successfully created/ Login Successful\n")
            break   #escape the loop
            
#function to let user input their complaints to be verified by the AI
def inputComplaint():
    #if user tried to issue complain before inputting a valid account details
    if (emailPass[0] == "" or emailPass[1] == ""):
        # added to log to display summary at the end
        summary("Update", "User tried to send complaint without login")
        print("Please Login first\n")
    else:   # else if user already login
        #collect user's complaint to be send to AI to analyze
        subject = input("Please type subject of your email: ")
        complaint = input("Please type your complaint: ")
        # added to log to display summary at the end
        summary("Update", "AI_manager is analyzing whether complaint is valid")
        print("AI is starting its analysis")
        AI_result = analyse_complaint(emailPass[0],subject, complaint)   #call analyze complaint with the arguments: subject and complaints

        print("AI analysis ended")
        # if priority score is more than 0 and less than 9
        if(0 < AI_result[1] < 9):
            # added to log to display summary at the end
            summary("Update", "User complaint sent successfully")
            print("Not spam")
            
        # else if priority score is 0 meaning it is a spam/invalid complaint
        elif(AI_result[1] == 0):
            # added to log to display summary at the end
            summary("Update", "Complaint is invalid/spam")
            print("Invalid Complaint or Spam")
#function to load either the Admin_Team table or Tech_Professionals table
def loadSQL():
    while True:
        #take user input either 1 or 2 only
        tables = int(input("Choose which table to load(Admin (1) or Tech (2)): "))
        match tables:
            # if user input 1, display Admin_Team
            case 1:
                # added to log to display summary at the end
                summary("Update", "Loaded data from Admin_Team in SQL")
                result = load_from_SQL("Admin_Team")
                print("\n")
                for complaint in result:
                    # 1. Unpack the columns for the current row
                    complaint_id, category, priorityScore, date, deadline = complaint[:5]
                    print(f"ComplaintID: {complaint_id}\nCategory: {category}\nPriority Score: {priorityScore}")
                    print(f"Datetime: {date}\nDeadline: {deadline}")
                    print("-" * 20 + "\n")
                break
            # if user input 2, display Tech_Professionals
            case 2:
                # added to log to display summary at the end
                summary("Update", "Loaded data from Tech_Professionals in SQL")
                result = load_from_SQL("Tech_Professionals")
                print("\n")
                for complaint in result:
                    # 1. Unpack the columns for the current row
                    complaint_id, category, priorityScore, date, deadline = complaint[:5]
                    print(f"ComplaintID: {complaint_id}\nCategory: {category}\nPriority Score: {priorityScore}")
                    print(f"Datetime: {date}\nDeadline: {deadline}")
                    print("-" * 20 + "\n")
                break
            # if user input anything other then 1 or 2
            case _:
                summary("Update", "User input is invalid")
                print("invalid input. Try 1 or 2.")
                tables = int(input("Choose which table to load(Admin (1) or Tech (2)): "))

def Menu():
    print("Below are your options(1,2,3,4,5):")
    print("Option 1: Login/Create Account")
    print("Option 2: Input Complaint")
    print("Option 3: Load SQL")
    print("Option 4: Fetch Summary Log")
    print("Option 5: End the program")
    options = int(input("Please input your option here: "))
    return options