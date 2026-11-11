class SchemaValidator:
    def __init__(self):
        # Encapsulation: Hidden attributes
        self._valid_categories = {
            "Security and Fraud", "Billing and Payment", "Technical Support",
            "Refund", "Product/Service Quality", "Delivery & Shipping",
            "Account", "General Inquiry", "Spam"
        }

    def is_valid(self, response_dict: dict) -> bool:
        if not isinstance(response_dict, dict): 
            return False
        
        required_keys = {"category", "priority_score", "reasoning"}
        if not required_keys.issubset(response_dict.keys()): 
            return False

        if response_dict["category"] not in self._valid_categories: 
            return False
            
        if type(response_dict["priority_score"]) is not int: 
            return False
        if not (0 <= response_dict["priority_score"] <= 8): 
            return False
        if not isinstance(response_dict["reasoning"], str): 
            return False

        return True