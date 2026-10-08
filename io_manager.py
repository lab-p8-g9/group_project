from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
#from ai_manager import AIManager        # put ur function  name here

app = Flask(__name__)
#ai_manager = AIManager()

# Route to display your separate HTML form
@app.route('/')
def home():
    return render_template('account.html')

# Route to receive and process the form data from the user

@app.route("/createAccount", methods=['POST'])
def createAccount():
    print("Account created")
    print("Redirecting to email complaint page")
    return redirect(url_for('emailPage'))

@app.route('/email')
def emailPage():
    return render_template('email.html')

@app.route('/submitComplaint', methods=['POST'])
def submit():
    # 'user_email' matches the 'name' attribute of the email input field in index.html
    user_email = request.form.get('user_email')
    user_complaint = request.form.get('user_complaint')

    #if user_email is invalid format, return an error message
    if not user_email or '@' not in user_email:
        return "<h3>Error: Invalid email format. Please go back and enter a valid email.</h3><a href='/'>Go Back</a>"
    
    # You can process the data here in Python (e.g., save to a database, run a script)
    print(f"\nThe user email is {user_email}\n")
    print(f"Complaint: {user_complaint}\n")

    #result = ai_manager.validate_email(user_email)  #call ur ai function here
    #if (result == "Valid"):
        #search last complaint id in database and fetch it and increment by 1 and
        #send the complaint id, email and complaint, datetime back to the database
        # Return a response back to the browser window
        
    return f"<h3>Complaint Successfully</h3><a href='/'>Go Back</a>"

if __name__ == '__main__':
    # FIXED: Added host="0.0.0.0" and changed port to 8080
    app.run(host="127.0.0.1", port=8080, debug=True)


    #validate if username already taken and if email already exists in the database
    #set a format e.g. password must contain number, symbol, uppercase and lowercase with minimum 12 characters, and email must be in valid format. If not, return an error message to the user.
def validate_user_input(username, email, password):
    # Validate username
    if not username or len(username) < 3:
        return "Error: Username must be at least 3 characters long."

    # Validate email format
    if not email or '@' not in email:
        return "Error: Invalid email format."

    # Validate password complexity
    if (not password or len(password) < 12 or
            not any(char.isdigit() for char in password) or
            not any(char.isupper() for char in password) or
            not any(char.islower() for char in password) or
            not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password)):
        return ("Error: Password must be at least 12 characters long and include at least one number, "
                "one uppercase letter, one lowercase letter, and one special character.")

    return "Valid input."