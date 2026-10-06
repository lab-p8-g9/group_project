from flask import Flask, render_template, request
from ai_manager import AIManager        # put ur function  name here

app = Flask(__name__)
ai_manager = AIManager()

# Route to display your separate HTML form
@app.route('/')
def home():
    return render_template('email.html')

# Route to receive and process the form data from the user
@app.route('/submit', methods=['POST'])
def submit():
    # 'user_email' matches the 'name' attribute of the email input field in index.html
    user_email = request.form.get('user_email')
    user_complaint = request.form.get('user_complaint')
    
    # You can process the data here in Python (e.g., save to a database, run a script)
    print(f"\n[PYTHON RECEIVE SUCCESS] The user submitted: {user_email}\n")
    print(f"[PYTHON RECEIVE SUCCESS] The user submitted: {user_complaint}\n")

    result = ai_manager.validate_email(user_email)  #call ur ai function here
    
    # Return a response back to the browser window
    return f"<h3>Python successfully received your data:</h3><p>{user_email}</p><p>{user_complaint}</p><a href='/'>Go Back</a>"

if __name__ == '__main__':
    # FIXED: Added host="0.0.0.0" and changed port to 8080
    app.run(host="127.0.0.1", port=8080, debug=True)