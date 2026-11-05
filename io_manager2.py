# importing external libraries
from flask import Flask, render_template, request, redirect, url_for
from ai_manager import analyse_complaint
from data_manager import save_to_SQL, load_from_SQL, load_from_JSON
app = Flask(__name__)

# collect summary of what happened in the I/O Manager
log = []
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

# function for repetitive alertBoxes
def alertBox(msg):
    return f"<script> alert('{msg}'); window.history.back();</script>"

# Declare starting page as 127.0.0.1:8080 using load.html as the template
@app.route('/')
def home():
    return render_template('account.html')
#     # on initialization load data from Admin_Team and Tech_Professionals Data and display them in a table
#     admins = load_from_SQL("Admin_Team")
#     techPro = load_from_SQL("Tech_Professionals")
#     return render_template('load.html', items_list = admins, items_list2 = techPro)

# # Head to 127.0.0.1:8080/json page using json.html as its template
# @app.route("/json")
# def loadJSON():
#     # load data from complaints.json file and display in a table
#     json_data = load_from_JSON()
#     return render_template('json.html', data = json_data)

# Head to 127.0.0.1:8080 page using the account.html as template
@app.route("/Account", methods=["POST"])
def accountPage():
    button_clicked = request.form.get("action")
    if button_clicked == "login" or button_clicked == "signup":
        user_email = request.form.get("user_email")
        password = request.form.get("user_password")
        
        # if user typed an invalid email and password, user will be prompted to retype a valid one
        if(validate_user_input(user_email, password).strip() != "Valid input."):
            print(validate_user_input(user_email, password))
            return (f"""<script>
                            alert("{validate_user_input(user_email, password)}");
                            window.history.back();
                        </script>
                        """)
        # if user typed in a valid email and password
        else:
            # added to log to display summary at the end
            summary("Update", "User entered a valid email and password and is redirected to complaint page")
            userList = [user_email, password]
            print(userList)
            # call save_to_SQL function in data_manager.py and send userList which contains
            # email and password
            if(save_to_SQL("Accounts", userList) == True):
                print("Login/Account Created")
                print("Redirecting to email complaint page")
                # bring user to 127.0.0.1:8080/email page that uses email.html as template
                return redirect(url_for('emailPage'))
            # if user tries to type in an email that already exists but used wrong password
            else:
                # added to log to display summary at the end
                summary("Update", "User inputted an account that already exists")
                print("Account already exists")
                # alert user that they are trying to create an account that already exists
                return(alertBox("Account already exists"))
    elif button_clicked == "employee":
        print("Redirecting to employee login page")
        return redirect(url_for('employeeLoginPage'))
        
# Head to 127.0.0.1:8080/email page using the email.html as template
@app.route('/email')
def emailPage():
    return render_template('email.html')

@app.route('/employeeLogin')
def employeeLoginPage():
    return render_template('employee.html')

@app.route('/Home', methods=["POST"])
def employeeHomePage():
    user_email = request.form.get("user_email")
    password = request.form.get("user_password")
    # if user typed an invalid email and password, user will be prompted to retype a valid one
    if(validate_user_input(user_email, password).strip() != "Valid input."):
        print(validate_user_input(user_email, password))
        return (f"""<script>
                        alert("{validate_user_input(user_email, password)}");
                        window.history.back();
                    </script>
                    """)
    # if user typed in a valid email and password
    else:
        # added to log to display summary at the end
        summary("Update", "Employee entered a valid email and password and is redirected to employee home page")
        userList = [user_email, password]
        print(userList)
        # call save_to_SQL function in data_manager.py and send userList which contains
        # email and password
        return redirect(url_for('employeePage'))

@app.route('/employee')
def employeePage():
    return render_template('home.html')

# function for user to submit their complaint
@app.route('/submitComplaint', methods=['POST'])
def submit():
    # 'user_email' matches the 'name' attribute of the email input field in email.html
    # email address, subject of email and complaint of email from html form
    user_email = request.form.get('user_email')
    subject = request.form.get('subject')
    user_complaint = request.form.get('user_complaint')
    # added to log to display summary at the end
    summary("Update", "User has entered, his complaint")

    print(f"\nThe user email is {user_email}\n")
    print(f"Subject of email is {subject}\n")
    print(f"Complaint: {user_complaint}\n")
    # if user is trying to use an email that doesn't exist in the database
    if(check_email_in_accounts(user_email) == False):
        # added to log to display summary at the end
        summary("Update", "User needs to re-enter an existing email")
        print("Please input an email that exists")
        # alert user that they are trying to complaint with an email that doesn't exist
        return(alertBox("Email does not exist in the database"))
    # else if email exists
    elif(check_email_in_accounts(user_email) == True):
        # added to log to display summary at the end
        summary("Update", "User's email is valid, complaint is being assessed by AI now")
        print("AI is starting its analysis")
        # call the analyse_complaint function in AI_Manager taking subject of email and user's complaint
        result = analyse_complaint(subject, user_complaint)
            # added to log to display summary at the end
        if(0 < result.priority_score < 9):
            summary("Update", f"Complaint is valid with a priority score of {result.priority_score} with the category: {result.category}")
            # reach end of program fetch summary of all the things that happened
            summary("Fetch")
            return f"<h3>Complaint Successful!</h3><a href='/'>Go Back</a>"
        # else if priority score equals to 0
        elif (result.priority_score == 0):
            # added to log to display summary at the end
            summary("Update", "User entered an invalid complaint, please try again")
            print("Invalid complaint or Spam")
            return(alertBox("Invalid complaint or Spam"))

    
if __name__ == '__main__':
    # Added host="0.0.0.0" and changed port to 8080
    app.run(host="127.0.0.1", port=8080, debug=True)