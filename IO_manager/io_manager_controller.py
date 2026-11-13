import json

from flask import Flask, jsonify, redirect, render_template, request, url_for

from IO_manager.activity_summary import ActivitySummary
from IO_manager.credential_validator import CredentialValidator
from IO_manager.io_manager_interfaces import AuthenticationUseCase, ComplaintUseCase


class IOManager:
    def __init__(
        self,
        app: Flask,
        authentication_service: AuthenticationUseCase,
        complaint_service: ComplaintUseCase,
        credential_validator: CredentialValidator,
        activity_summary: ActivitySummary,
    ):
        self.app = app
        self.authentication_service = authentication_service
        self.complaint_service = complaint_service
        self.credential_validator = credential_validator
        self.activity_summary = activity_summary
        self.log = activity_summary.log

    def register_routes(self):
        routes = (
            ("/", "home", self.home, ["GET"]),
            ("/email", "emailPage", self.emailPage, ["GET"]),
            ("/employeeLogin", "employeeLoginPage", self.employeeLoginPage, ["GET"]),
            ("/customer", "customerPage", self.customerPage, ["GET"]),
            ("/employee", "employeePage", self.employeePage, ["GET"]),
            ("/viewComplaint", "viewComplaintPage", self.viewComplaintPage, ["GET"]),
            ("/Account", "accountPage", self.accountPage, ["POST"]),
            ("/Home", "employeeHomePage", self.employeeHomePage, ["POST"]),
            ("/resolved", "resolving", self.resolving, ["POST"]),
            ("/submitComplaint", "submit", self.submit, ["POST"]),
        )
        for rule, endpoint, view_func, methods in routes:
            self.app.add_url_rule(
                rule,
                endpoint=endpoint,
                view_func=view_func,
                methods=methods,
            )

    def summary(self, updates, actions=""):
        self.activity_summary.summary(updates, actions)

    def validate_user_input(self, email, password):
        result = self.credential_validator.validate(email, password)
        if result == "Error: User enter an invalid email and password(min. 12 characters, 1 symbol, 1 number, 1 uppercase, 1 lowercase)":
            self.summary("Update", "Invalid email and password")
        elif result == "Error: Invalid email format.":
            self.summary("Update", "User entered an invalid email")
        elif result.startswith("Error: Password must be"):
            self.summary("Update", "User enter an invalid password")
        return result

    def alertBox(self, msg):
        return f"<script> alert('{msg}'); window.history.back();</script>"

    def alert_and_redirect(self, message, destination):
        return (
            f"<script>alert({json.dumps(message)});"
            f"window.location.replace({json.dumps(destination)});</script>"
        )

    def home(self):
        return render_template('account.html')

    def emailPage(self):
        return render_template('email.html')

    def employeeLoginPage(self):
        return render_template('employee.html')

    def customerPage(self):
        userEmail = request.args.get('userEmail')
        userRole = request.args.get('userRole')
        customer_complaint = self.complaint_service.customer_complaints(userEmail)
        return render_template(
            'customer.html',
            data=customer_complaint,
            email=userEmail,
            role=userRole,
        )

    def employeePage(self):
        self.summary("Fetch")
        userEmail = request.args.get('userEmail')
        userRole = request.args.get('userRole')
        top10Complaint = self.complaint_service.employee_preview(userRole)
        return render_template(
            'home.html',
            data=top10Complaint,
            email=userEmail,
            role=userRole,
        )

    def viewComplaintPage(self):
        userEmail = request.args.get('userEmail')
        userRole = request.args.get('userRole')
        complaints = self.complaint_service.all_employee_complaints(userRole)
        return render_template(
            'complaints.html',
            data=complaints,
            email=userEmail,
            role=userRole,
        )

    def accountPage(self):
        button_clicked = request.form.get("action")
        if button_clicked == "login" or button_clicked == "signup":
            user_email = request.form.get("user_email")
            password = request.form.get("user_password")

            if self.validate_user_input(user_email, password).strip() != "Valid input.":
                print(self.validate_user_input(user_email, password))
                return f"""<script>
                                alert("{self.validate_user_input(user_email, password)}");
                                window.history.back();
                            </script>
                            """

            self.summary(
                "Update",
                "User entered a valid email and password and is redirected to customer Homepage",
            )
            if button_clicked == "signup":
                try:
                    userData = self.authentication_service.create_customer_account(
                        user_email,
                        password,
                    )
                    print("Account Created")
                    print("Redirecting to Customer Homepage")
                    return redirect(
                        url_for(
                            'customerPage',
                            userEmail=userData[0],
                            userRole=userData[2],
                        )
                    )
                except ValueError as err:
                    if str(err) == "Account already exists.":
                        self.summary("Update", "User inputted the wrong password")
                        print("Incorrect Password")
                        return self.alertBox("Incorrect Password")

            if button_clicked == "login":
                userData = self.authentication_service.customer_account(
                    user_email,
                    password,
                )
                if userData is None:
                    return self.alertBox("User does not exist")
                return redirect(
                    url_for(
                        'customerPage',
                        userEmail=userData[0],
                        userPassword=userData[1],
                        userRole=userData[2],
                    )
                )
        elif button_clicked == "employee":
            print("Redirecting to employee login page")
            return redirect(url_for('employeeLoginPage'))

    def employeeHomePage(self):
        user_email = request.form.get("user_email")
        password = request.form.get("user_password")

        if self.validate_user_input(user_email, password).strip() != "Valid input.":
            print(self.validate_user_input(user_email, password))
            return f"""<script>
                            alert("{self.validate_user_input(user_email, password)}");
                            window.history.back();
                        </script>
                        """
        try:
            userData = self.authentication_service.employee_account(
                user_email,
                password,
            )
            print(
                self.authentication_service.employee_account(
                    user_email,
                    password,
                )
            )
            print("Login Successful")
            print("Redirecting to Employee Homepage")
            destination = url_for(
                'employeePage',
                userEmail=userData[0],
                userPassword=userData[1],
                userRole=userData[2],
            )
            if userData[2] == "Admin":
                return self.alert_and_redirect(
                    "Please view the terminal to view summary of customer Action",
                    destination,
                )
            return redirect(destination)
        except ValueError as err:
            if str(err) == "Account already exists.":
                print("Account already exists")
                return self.alertBox(err)
        except TypeError:
            return self.alertBox("userData is empty")

    def resolving(self):
        resolveBtn = request.form.get('resolveBtn')
        self.complaint_service.resolve_complaint(resolveBtn)
        return jsonify(status="Resolved")

    def submit(self):
        subject = request.form.get('subject')
        user_complaint = request.form.get('user_complaint')
        self.summary("Update", "User has entered, his complaint")
        print("analyzing complaint")
        result = self.complaint_service.analyze_complaint(subject, user_complaint)
        print("analyze done")
        if 0 < result[1] < 9:
            self.summary(
                "Update",
                f"Complaint is valid with a priority score of {result[1]} with the category: {result[0]}",
            )
            self.summary("Fetch")
            return self.alertBox(
                f"Complaint is valid with a priority score of {result[1]} with the category: {result[0]}"
            )
        if result[1] == 0:
            self.summary("Update", "User entered an invalid complaint, please try again")
            print("Invalid complaint or Spam")
            return self.alertBox("Invalid complaint or Spam")
