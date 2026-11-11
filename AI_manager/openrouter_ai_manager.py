import json
import logging
from openai import OpenAI
from AI_manager.ai_manager import AIManager
from AI_manager.schema_validator import SchemaValidator
from AI_manager.ai_connection_error import AIConnectionError
from AI_manager.schema_validation_error import SchemaValidationError
from AI_manager.api_config import APIConfig 

class OpenRouterAIManager(AIManager):
    def __init__(self):
        
        config = APIConfig() #class to get api key
        
        self.__client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key, 
            timeout=config.timeout
        )
        # Composition: Instantiating the validator class
        self._validator = SchemaValidator()
        
        # Encapsulated Business Logic (Formatted mapping for the Data Manager)
        self._team_assignment_rules = {
            "Technical Support": "Tech_Professionals",
            "Billing and Payment": "Tech_Professionals",
            "Security and Fraud": "Tech_Professionals",
            "Refund": "Admin_Team",
            "Product/Service Quality": "Admin_Team",
            "Delivery & Shipping": "Admin_Team",
            "Account": "Admin_Team",
            "General Inquiry": "Admin_Team",
            "Spam": "Spam"
        }

    def _clean_json_string(self, raw_str: str) -> str:
        # Encapsulation: Private helper method to handle markdown backticks
        raw_str = raw_str.strip()
        if raw_str.startswith("```json"):
            raw_str = raw_str[7:]
        elif raw_str.startswith("```"):
            raw_str = raw_str[3:]
        if raw_str.endswith("```"):
            raw_str = raw_str[:-3]
        return raw_str.strip()

    def analyse_complaint(self, subject: str, user_complaint: str, max_retries: int = 3) -> list:
        prompt = f"SUBJECT: {subject}\nBODY: {user_complaint}"
        
        for attempt in range(max_retries):
            try:
                completion = self.__client.chat.completions.create(
                    #To fulfil ai outputing a structured JSON output 
                    model="openrouter/free",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an AI Email Filter and Complaint Manager. "
                                "Evaluate if the email is spam, gibberish, or valid. "
                                "If spam or invalid, set priority_score to 0. "
                                "Otherwise, set priority_score between 1 to 8, with 1 being the least priority to 8 being the highest priority"
                                "You MUST respond strictly with a raw JSON object and nothing else. "
                                "The JSON must contain exactly these keys: "
                                "\"category\" (string: exactly one of 'Security and Fraud', 'Billing and Payment', 'Technical Support', 'Refund', 'Product/Service Quality', 'Delivery & Shipping', 'Account', 'General Inquiry', 'Spam'), "
                                "\"priority_score\" (integer 0 to 8), "
                                "\"reasoning\" (string)."
                            )
                        },
                        {"role": "user", "content": prompt},
                    ]
                )
                
                if not getattr(completion, 'choices', None) or not completion.choices[0].message.content:
                    logging.warning(f"Empty API response on attempt {attempt + 1}.")
                    continue
                    
                raw_content = completion.choices[0].message.content
                cleaned_json = self._clean_json_string(raw_content)
                ai_dictionary = json.loads(cleaned_json)

                if not self._validator.is_valid(ai_dictionary):
                    logging.warning(f"Schema validation failed on attempt {attempt + 1}.")
                    continue 
                
                # Assign team based on the validated category
                category = ai_dictionary["category"]
                assigned_to = self._team_assignment_rules.get(category, "Admin")
                
                return [
                    category,
                    ai_dictionary["priority_score"], 
                    ai_dictionary["reasoning"],
                    assigned_to 
                ]

            except json.JSONDecodeError:
                logging.warning(f"JSON parsing failed on attempt {attempt + 1}.")
            except Exception as e:
                # 1. Network/API errors should immediately break the loop or raise here
                logging.error(f"API Connection error: {e}")
                raise AIConnectionError(f"Failed to connect to OpenRouter: {e}")

        # Graceful Failure State: Raise exception cleanly instead of hard-coding a fake response
        logging.error("AI returned malformed data after maximum retries.")
        raise SchemaValidationError("Failed to get valid JSON schema from OpenRouter.")