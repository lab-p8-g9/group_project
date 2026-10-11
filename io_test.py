#test cases to check validate_user_input(), createAccount() and submit() function
#summary function not tested as it just used to log what happened in the other function


test_data = [
        ("loremipsum@gmail.com", "123"),
        ("helloworld.com", "!1Aaweds"),
        ("bobwashere", "Sodakid!1234"),
        ("workingemail@xyz.com", "!1Aanfcvjir3")
]    

test_data2 = ["george@gmail.com" , "loremipsum@gmail.com"]

# validate_user_input()
#verify the format of input is in the expected format
# Expected results: 
# If email or password format incorrect, user account will not be created.
# Else if, email and password format both correct, user account will be created
print("testing validate_user_input()")
for email, password in test_data:
    #check if email has @ included in it
    if not email or '@' not in email:
        emailFail = True
    elif '@' in email:
        emailFail = False

    # Validate password complexity
    if (not password or len(password) < 12 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password) or not any(char.islower() for char in password) or not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password)):
        passwordFail = True
    else:
        passwordFail = False
    if(passwordFail == False and emailFail == False):
        print("No issues")
    elif(passwordFail == False and emailFail == True):
        print(f"Email incorrect: {email}")
    elif(passwordFail == True and emailFail == False):
        print(f"Password incorrect: {password}")
    else:
        print(f"Both incorrect - Email: {email} | Password: {password}")

# createAccount()
# Expected Result:
# If email exists, user account will not be created
# Else if email does not exist yet, account will be created

# submit()
#testing if email exists, so systems know complaint is from a valid user
# Expected Result:
# If email doesn't exist user can't send complaint
# Else if email exist user complaint will be sent to AI_Manager for verification
print("\ntesting createAccount() and submit()")
for testEmails in test_data2:
    for index, email in enumerate(test_data):
        if(email[0] == testEmails):
            print("Email exists")
            break
        elif(email[0] != testEmails and index == 3):
            print("Email does not exist")
            break




        