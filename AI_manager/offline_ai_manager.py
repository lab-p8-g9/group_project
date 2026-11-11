from AI_manager.ai_manager import AIManager

class OfflineAIManager(AIManager):
    # Inherits from BaseAIManager to satisfy OOP Polymorphism requirements.

    def analyse_complaint(self, subject: str, user_complaint: str, max_retries: int = 3) -> list:
        # Bypasses the live OpenRouter API and JSON validation.
        # Instantly returns a structured list based on the input text.
        # Format: [category, priority_score, reasoning, assigned_team]
        
        text_to_evaluate = (subject + " " + user_complaint).lower()

        # Matches the "Faulty Product" and "Virus Installed" items from complaint.json
        if "broken" in text_to_evaluate or "virus" in text_to_evaluate:
            return ["Security and Fraud", 8, "Simulated critical technical issue.", "Tech_Professionals"]
        # Default fallback for any other test data
        return ["General Inquiry", 1, "Simulated low-priority general inquiry.", "Admin_Team"]