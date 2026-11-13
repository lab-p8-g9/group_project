from AI_manager.ai_manager import AIManager
from Logic_manager.logic_main import logic_main

class OfflineAIManager(AIManager):
    # Inherits from BaseAIManager to satisfy OOP Polymorphism requirements.

    # def analyse_complaint(self, subject: str, user_complaint: str, max_retries: int = 3) -> list:
    #     # Bypasses the live OpenRouter API and JSON validation.
    #     # Instantly returns a structured list based on the input text.
    #     # Format: [category, priority_score, reasoning, assigned_team]
        
    #     text_to_evaluate = (subject + " " + user_complaint).lower()

    #     # Matches the "Faulty Product" and "Virus Installed" items from complaint.json
    #     if "broken" in text_to_evaluate or "virus" in text_to_evaluate:
    #         return ["Security and Fraud", 8, "Simulated critical technical issue.", "Tech_Professionals"]
    #     # Default fallback for any other test data
    #     return ["General Inquiry", 1, "Simulated low-priority general inquiry.", "Admin_Team"]

    def analyse_complaint(self, email: str, subject: str, user_complaint: str, max_retries: int = 3):
        # Your dummy offline logic...
        category = "Technical Support"
        priority = 5
        reasoning = "Offline test mode."
        assigned_to = "Tech"
        
        # The offline manager MUST also create the JSON file for the Logic Manager!
        self._log_to_json(email, subject, user_complaint, category, priority, assigned_to)

        process = logic_main("ai_output.json")
        process.process_ai_sample()   
             
        return [category, priority, reasoning, assigned_to]