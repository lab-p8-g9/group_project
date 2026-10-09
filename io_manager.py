from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from ai_manager import analyse_complaint
from data_manager import add
app = Flask(__name__)

# Route to display your separate HTML form
@app.route('/')
def home():
    return render_template('account.html')

# Validate that the input format is correct
def validate_user_input(email, password):

    # Validate email format
    if not email or '@' not in email:
        return "Error: Invalid email format."

    # Validate password complexity
    if (not password or len(password) < 12 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password) or not any(char.islower() for char in password) or not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password)):
        return ("Error: Password must be at least 12 characters long and include at least one number, "
                "one uppercase letter, one lowercase letter, and one special character.")

    return "Valid input."

@app.route("/createAccount", methods=['POST'])
def createAccount():
    user_email = request.form.get('user_email')
    password = request.form.get('user_password')
    if(validate_user_input(user_email, password).strip() != "Valid input."):
        print(validate_user_input(user_email, password))
        return f"<p>{validate_user_input(user_email, password)}</p><a href='/'>Try Again</a>"
    else:
        userList = [user_email, password]
        print(userList)
        #if(add("Accounts", userList) == "Successfully Added"):
            #print()
        print("Account created")
        print("Redirecting to email complaint page")
        return redirect(url_for('emailPage'))
        #else:
            #print("Account already exists")
            #return("""
    # <!DOCTYPE html>
    # <html>
    # <body>
    #     <h2>Automatic Alert</h2>
    #     <script>
    #         alert("I am an automatic alert box!");
    #     </script>
    # </body>
    # </html>
    # """)
        

@app.route('/email')
def emailPage():
    return render_template('email.html')

@app.route('/submitComplaint', methods=['POST'])
def submit():
    # 'user_email' matches the 'name' attribute of the email input field in index.html
    user_email = request.form.get('user_email')
    subject = request.form.get('subject')
    user_complaint = request.form.get('user_complaint')
    
    # You can process the data here in Python (e.g., save to a database, run a script)
    print(f"\nThe user email is {user_email}\n")
    print(f"Subject of email is {subject}\n")
    print(f"Complaint: {user_complaint}\n")

    result = analyse_complaint(subject, user_complaint)
    if (0 < result.priority_score < 9):
        now = datetime.now()
        currentTime = now.strftime("%Y-%m-%d %H:%M:%S")
        complaintList = [user_email, subject, user_complaint, currentTime]
        print(complaintList)
        #add("Emails", complaintList)
        # Return a response back to the browser window
        return f"<h3>Complaint Successfully</h3><a href='/'>Go Back</a>"
    elif (result.priority_score == 0):
        print("Invalid complaint or Spam")
        return "<h3>Error</h3><p>This email is a spam</p>"
        
    
if __name__ == '__main__':
    # FIXED: Added host="0.0.0.0" and changed port to 8080
    app.run(host="127.0.0.1", port=8080, debug=True)


    #validate if email already exists in the database
    #set a format e.g. password must contain number, symbol, uppercase and lowercase with minimum 12 characters, and email must be in valid format. If not, return an error message to the user.
