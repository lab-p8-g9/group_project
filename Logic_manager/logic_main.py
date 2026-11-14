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
        sample = file.read()


        for item in sample:

            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


            email_process = logic_email_process(
                item["email_address"],
                item["subject"],
                item["content"],
                current_datetime,
                item["category"],
                item["priority_score"],
                item["assigned_to"]
            )
            
            strategy_class = self.get_strategy(item["assigned_to"])

            if strategy_class is None:
                raise ValueError(f"Unknown department: {item['assigned_to']}")

            email_id = email_process.process_data()


            new_score, deadline = email_process.get_classified_results()

            department_process = strategy_class(
                item["email_address"],
                item["subject"],
                item["content"],
                current_datetime,
                item["category"],
                item["priority_score"],
                item["assigned_to"],
                new_score,
                deadline,
                email_id
            )


            department_process.process_data()

        file.clear()

        print("AI Sample processed Successfully!")



    def get_strategy(self, assigned_to):

            department = assigned_to.strip().lower()

            if not re.fullmatch(r"[a-z][a-z0-9_]*", department):
                raise ValueError(f"Invalid department: {assigned_to}")

            module_name = f"Logic_manager_copy.logic_{department}_process"
            class_name = f"logic_{department}_process"

            try:
                module = import_module(module_name)
                strategy_class = getattr(module, class_name)

            except (ModuleNotFoundError, AttributeError) as error:
                raise ValueError(
                    f"Unknown department: {assigned_to}"
                ) from error

            if not isinstance(strategy_class, type) or not issubclass(strategy_class, logic_process):
                raise TypeError("Strategy must inherit from logic_process")

            return strategy_class