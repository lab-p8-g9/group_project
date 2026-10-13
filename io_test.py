#test cases to check validate_user_input(), Account(), inputComplaint(), loadSQL() function
#summary function not tested as it just used to log what happened in the other function
from data_manager import load_from_SQL, save_to_SQL
from ai_manager import analyse_complaint
from io_manager import validate_user_input, emailPass


test_data = [
        ("loremipsum@gmail.com", "123"),
        ("helloworld.com", "!1Aaweds"),
        ("bobwashere", "Sodakid!1234"),
        ("workingemail@xyz.com", "!1Aanfcvjir3")
]    

test_data2 = [
        ("george@gmail.com", "jnad!dsmlk23" ), 
        ("workingemail@xyz.com", "!1aAnfcv39ejid"),
        ("workingemail@xyz.com", "!1Aanfcvjir3")
              ]

# validate_user_input()
#verify the format of input is in the expected format
# Expected results: 
# If email or password format incorrect, user account will not be created.
# Else if, email and password format both correct, user account will be created

print("testing validate_user_input()")
for email, password in test_data:
    if (not email or '@' not in email) and (not password or len(password) < 12 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password) or not any(char.islower() for char in password) or not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password)):
        print("Error: User enter an invalid email and password(min. 12 characters, 1 symbol, 1 number, 1 uppercase, 1 lowercase)")
    # Validate email format
    elif not email or '@' not in email:
        print("Error: Invalid email format.")

    # Validate password complexity, must contain at least 12 character, 1 uppercase and lowercase, 1 symbol and number
    elif (not password or len(password) < 12 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password) or not any(char.islower() for char in password) or not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password)):
        print("Error: Password must be at least 12 characters long and include at least one number, "
                "one uppercase letter, one lowercase letter, and one special character.")
    else:
        print("Valid input.")

# Account()
# Expected Result:
# If email exists and password is correct, user will be able to login
# Else if email exists and password is incorrect, user will not be able to login or create new account

print("\ntesting Account()")
for email, password in test_data2:
    try:
        #call the validation input function
        validation = validate_user_input(email, password)
        emailPass[0] = email
        emailPass[1] = password
        #if user inputted an email or password or both in the wrong format
        if(validation != "Valid input."):
            raise ValueError(validation)    #raise the output from validation into ValueError
        else:
            result = save_to_SQL("Accounts", emailPass)
            #if user tries to input an email with the wrong password or 
            # trying to create new account with existing email
            if result == "User already exists":
                # added to log to display summary at the end
                raise ValueError(result)    #raise the output from result if it gave an error into ValueError    
    #fall into except if ValueError
    except ValueError as e:
        print(e)    #print the value in ValueError
        continue    #go to next iteration
    else:   #else if user enter everything right
        print("Account successfully created/ Login Successful\n")
        break   #escape the loop


# inputComplaint()
# Expected Result:
# If user hasn't login, they can't send a complaint
# Else if already login, then if the AI rates it a 0, it is spam
# Else if 1 to 9, AI acknowledges that it is a valid complaint
testData4 = [
    ("", ""), 
    ("workingemail@xyz.com", "!1Aanfcvjir3")
]
testData5 = [
    ("AMOSD", "doawmd"),
    ("General", "My account got locked")
]
print("\ntesting inputComplaint()")
for email, password in testData4:
    count = 0
    if(email == "" or password == ""):
        print("User needs to login first")
    else:
        print("User has login already")
        for subject, complaint in testData5:
            AI_result = analyse_complaint(subject, complaint)
            if(AI_result[1] == 0):
                print("Complaint is a spam")
            elif(0 < AI_result[1] < 9):
                print("Complaint is valid")

# loadSQL()
# Expected Result:
# If user inputted 1, it will load the Admin_Team table in SQL
# Else if user inputted 1, it will load the Tech_Professionals table in SQL
# Else user will be prompted to re-enter their input as 1 or 2
print("\ntesting loadSQL()")
testData6 = [1,2,"sd"]
for i in testData6:
    while True:
        match i:
            case 1:
                result = load_from_SQL("Admin_Team")
                print("\n")
                for complaint in result:
                    # 1. Unpack the columns for the current row
                    complaint_id, category, priorityScore, date, deadline = complaint[:5]
                    print(f"ComplaintID: {complaint_id}\nCategory: {category}\nPriority Score: {priorityScore}")
                    print(f"Datetime: {date}\nDeadline: {deadline}")
                    print("-" * 20 + "\n")
                break
            case 2:
                load_from_SQL("Tech_Professionals")
                print("\n")
                for complaint in result:
                    # 1. Unpack the columns for the current row
                    complaint_id, category, priorityScore, date, deadline = complaint[:5]
                    print(f"ComplaintID: {complaint_id}\nCategory: {category}\nPriority Score: {priorityScore}")
                    print(f"Datetime: {date}\nDeadline: {deadline}")
                    print("-" * 20 + "\n")
                break
            case _:
                print("invalid input. Try 1 or 2.")
                print("User will be prompted to enter a valid input")
                break