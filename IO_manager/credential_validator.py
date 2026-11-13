class CredentialValidator:
    def validate(self, email, password):
        if (not email or '@' not in email) and (
            not password
            or len(password) < 12
            or not any(char.isdigit() for char in password)
            or not any(char.isupper() for char in password)
            or not any(char.islower() for char in password)
            or not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password)
        ):
            return "Error: User enter an invalid email and password(min. 12 characters, 1 symbol, 1 number, 1 uppercase, 1 lowercase)"
        elif not email or '@' not in email:
            return "Error: Invalid email format."
        elif (
            not password
            or len(password) < 12
            or not any(char.isdigit() for char in password)
            or not any(char.isupper() for char in password)
            or not any(char.islower() for char in password)
            or not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password)
        ):
            return (
                "Error: Password must be at least 12 characters long and include at least one number, "
                "one uppercase letter, one lowercase letter, and one special character."
            )

        return "Valid input."
