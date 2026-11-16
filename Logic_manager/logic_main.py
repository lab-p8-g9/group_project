import json
from datetime import datetime
from importlib import import_module #strategy
import re  #strategy
from Logic_manager.logic_process import logic_process
from Logic_manager.logic_email_process import logic_email_process
from Data_manager.json_handling import json_handling

class logic_main:

    def __init__(self, ai_file):
        self.__ai_file = ai_file

    def process_ai_sample(self):
        file = json_handling(self.__ai_file)
        errors = []
        processed_count = 0
        skipped_count = 0

        # Read AI sample
        try:
            sample = file.read()

            if not isinstance(sample, list):
                raise ValueError("AI sample must contain a list of emails")

        except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as error:
            errors.append({
                "type": "file",
                "error": f"Cannot read AI sample: {error}"
            })

            self.show_error_report(errors, skipped_count)
            return

        for item in sample:

            # Validate AI sample before processing
            try:
                if not isinstance(item, dict):
                    raise ValueError("Invalid email sample format")

                required_fields = [
                    "email_address", "subject", "content",
                    "category", "priority_score", "assigned_to"
                ]

                for field in required_fields:
                    if field not in item:
                        raise KeyError(f"Missing required field: {field}")

                # Validate email information
                for field in ["email_address", "subject", "content", "category", "assigned_to"]:
                    if not isinstance(item[field], str) or not item[field].strip():
                        raise ValueError(f"Invalid {field}: cannot be empty")

                if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", item["email_address"]):
                    raise ValueError(f"Invalid email address: {item['email_address']}")

                # Validate priority score
                priority_score = item["priority_score"]

                if type(priority_score) is not int or not 1 <= priority_score <= 8:
                    raise ValueError(
                        f"Invalid priority score: {priority_score}. Must be an integer between 1 and 8"
                    )

                # Find department strategy
                assigned_to = item["assigned_to"]

                try:
                    strategy_class = self.get_strategy(assigned_to)

                except (ValueError, TypeError) as error:
                    raise ValueError(
                        f"No assigned_to process department created for '{assigned_to}'"
                    ) from error

                assigned_to = assigned_to.strip().capitalize()
                current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                email_process = logic_email_process(
                    item["email_address"], item["subject"], item["content"],
                    current_datetime, item["category"], priority_score,
                    assigned_to
                )

                # Calculate deadline before saving
                new_score, deadline = email_process.get_classified_results()

            except (KeyError, ValueError, TypeError, OverflowError) as error:
                errors.append({
                    "type": "email",
                    "email_address": item.get("email_address", "Unknown") if isinstance(item, dict) else "Unknown",
                    "subject": item.get("subject", "Missing") if isinstance(item, dict) else "Missing",
                    "assigned_to": item.get("assigned_to", "Missing") if isinstance(item, dict) else "Missing",
                    "error": str(error)
                })

                skipped_count += 1
                continue

            # Process valid email
            email_id = email_process.process_data()

            department_process = strategy_class(
                item["email_address"], item["subject"], item["content"],
                current_datetime, item["category"], priority_score,
                assigned_to, new_score, deadline, email_id
            )

            department_process.process_data()
            processed_count += 1

        # Clear AI sample
        try:
            file.clear()

        except OSError as error:
            errors.append({
                "type": "file",
                "error": f"Cannot clear AI sample: {error}"
            })

        print("\nAI Sample processing completed!")
        print(f"Successfully processed: {processed_count}")

        self.show_error_report(errors, skipped_count)

    def get_strategy(self, assigned_to):
        department = assigned_to.strip().lower()

        if not re.fullmatch(r"[a-z][a-z0-9_]*", department):
            raise ValueError(f"Invalid department: {assigned_to}")

        module_name = f"Logic_manager.logic_{department}_process"
        class_name = f"logic_{department}_process"

        try:
            module = import_module(module_name)
            strategy_class = getattr(module, class_name)

        except ModuleNotFoundError as error:
            if error.name != module_name:
                raise

            raise ValueError(f"Unknown department: {assigned_to}") from error

        except AttributeError as error:
            raise ValueError(f"Unknown department: {assigned_to}") from error

        if not isinstance(strategy_class, type) or not issubclass(strategy_class, logic_process):
            raise TypeError("Strategy must inherit from logic_process")

        return strategy_class

    def show_error_report(self, errors, skipped_count):

        if not errors:
            print("No error encountered in AI sample.")
            return

        print("\n========== AI SAMPLE ERROR REPORT ==========")

        email_number = 0

        for error in errors:
            if error["type"] == "file":
                print("\nAI Sample File Error:")
                print(f"Error : {error['error']}")

            else:
                email_number += 1

                print(f"\nEmail {email_number}:")
                print(f"Email Address : {error['email_address']}")
                print(f"Subject       : {error['subject']}")
                print(f"Assigned To   : {error['assigned_to']}")
                print(f"Error         : {error['error']}")

            print("-" * 40)

        print(f"\nTotal skipped emails: {skipped_count}")
