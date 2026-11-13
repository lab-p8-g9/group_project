from abc import ABC, abstractmethod

class AIManager(ABC):
    @abstractmethod
    def analyse_complaint(self, email: str, subject: str, user_complaint: str, max_retries: int = 3) -> list:
        """Processes the text and returns: [category, priority, reasoning, assigned_team]"""
        pass