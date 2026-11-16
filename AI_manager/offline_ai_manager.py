import json
from AI_manager.ai_manager import AIManager
from Logic_manager.logic_main import logic_main

class OfflineAIManager(AIManager):

    def _log_to_json(self, email, subject, user_complaint, category, priority, assigned_to):
        output_data = {
            "email_address": email,
            "subject": subject,
            "content": user_complaint,
            "category": category,
            "priority_score": priority,
            "assigned_to": assigned_to
        }
        
        with open("ai_output.json", "w") as json_file:
            json.dump([output_data], json_file, indent=4)

    def analyse_complaint(self, email: str, subject: str, user_complaint: str, max_retries: int = 3):
        category = "Technical Support"
        priority = 5
        reasoning = "Offline test mode."
        assigned_to = "Tech"
        
        self._log_to_json(email, subject, user_complaint, category, priority, assigned_to)

        process = logic_main("ai_output.json")
        process.process_ai_sample()   
             
        return [category, priority, reasoning, assigned_to]
