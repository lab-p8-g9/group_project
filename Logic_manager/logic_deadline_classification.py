from datetime import datetime, timedelta


class Logic_Deadline_Classification:

    def __init__(self, priority_score, current_date):

        self.__priority_score = priority_score
        self.__current_date = datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S")

        self.__max_priority = 8
        self.__min_priority = 0

    def classification(self):

        date_created = self.__current_date
        priority_score = self.__priority_score
        current_date = datetime.now()

    
        days_passed = (current_date.date() - date_created.date()).days

    
        if days_passed <= self.__min_priority:
            new_priority = priority_score
        else:
            new_priority = priority_score + days_passed

        # Maximum priority score is 8
        if new_priority > self.__max_priority:
            new_priority = self.__max_priority


        days_to_deadline = max(self.__min_priority, self.__max_priority - priority_score)

        deadline_date = date_created + timedelta(days=days_to_deadline)

        return new_priority, deadline_date



