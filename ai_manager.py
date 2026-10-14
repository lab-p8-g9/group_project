import os
import logging
import re
import json
from pygarble import EnsembleDetector #pip install pygarble
from dotenv import load_dotenv #pip install python-dotenv
from openai import OpenAI #pip install openai
from logic_manager import Logic_Main, Logic_Create_Email_List



load_dotenv()

openrouter_key = os.getenv("OPENROUTER_API_KEY") #get your own api key

client = OpenAI(
  base_url = "https://openrouter.ai/api/v1",
  api_key = openrouter_key
)


def validate_response_schema(response_dict: dict) -> bool:
    if not isinstance(response_dict, dict): 
        return False
    
    required_keys = {"category", "priority_score", "reasoning"}
    if not required_keys.issubset(response_dict.keys()): 
        return False

    valid_categories = [
        "Security and Fraud", "Billing and Payment", "Technical Support",
        "Refund", "Product/Service Quality", "Delivery & Shipping",
        "Account", "General Inquiry", "Spam"
    ]
    if response_dict["category"] not in valid_categories: 
        return False
        
    if not isinstance(response_dict["priority_score"], int): 
        return False
    if not (0 <= response_dict["priority_score"] <= 8): 
        return False
    if not isinstance(response_dict["reasoning"], str): 
        return False

    return True

def analyse_complaint(email, subject: str, user_complaint: str, max_retries: int = 3) -> list:
    email_list = []

    prompt = f"SUBJECT: {subject}\nBODY: {user_complaint}"
    
    for attempt in range(max_retries): # to reject or retry on malformed AI output
        try:
            completion = client.chat.completions.create(
                model="openrouter/free", #Can change llm model here eg. openrouter/free or nvidia/nemotron-3-ultra-550b-a55b:free
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI Email Filter and Complaint Manager. "
                            "First, evaluate if the email is spam, gibberish, or valid. "
                            "If spam or invalid, set priority_score to 0. "
                            "You MUST respond strictly with a raw JSON object and nothing else. "
                            "Do not use markdown formatting or code blocks. "
                            "The JSON must contain exactly these keys: "
                            "\"category\" (string: exactly one of 'Security and Fraud', 'Billing and Payment', 'Technical Support', 'Refund', 'Product/Service Quality', 'Delivery & Shipping', 'Account', 'General Inquiry', 'Spam'), "
                            "\"priority_score\" (integer 0 to 8), "
                            "\"reasoning\" (string)."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ]
            )
            if getattr(completion, 'choices', None) is None:
                logging.warning(f"OpenRouter API returned a broken/empty response on attempt {attempt + 1}. Retrying...")
                continue

            message_content = completion.choices[0].message.content
            if not message_content:
                logging.warning(f"Empty response from model on attempt {attempt + 1}. Retrying...")
                continue
                
            raw_response_str = message_content.strip()

            if raw_response_str.startswith("```json"):
                raw_response_str = raw_response_str[7:]
            elif raw_response_str.startswith("```"):
                raw_response_str = raw_response_str[3:]
                
            if raw_response_str.endswith("```"):
                raw_response_str = raw_response_str[:-3]
                
            raw_response_str = raw_response_str.strip()

            ai_dictionary = json.loads(raw_response_str)

            if not validate_response_schema(ai_dictionary):
                logging.warning(f"Malformed output schema on attempt {attempt + 1}. Retrying...")
                continue 
            
            ai_list = [
                ai_dictionary["category"],          #order of analysis list
                ai_dictionary["priority_score"], 
                ai_dictionary["reasoning"]       
            ]

            print(ai_list)

            if 0 < ai_list[1] < 9:
                email_list.append(email)
                email_list.append(subject)
                email_list.append(user_complaint)
                

                Logic_Create_Email_List(email_list)
            return ai_list
            

        except json.JSONDecodeError:
            logging.warning(f"Failed to parse JSON on attempt {attempt + 1}. Retrying...")
            
        except Exception as e:
            logging.error(f"AI Model failed/unreachable. Error: {e}.")
            return None
            
    #return None

def fallback_rule_analysis(subject: str, user_complaint: str) -> list:
    full_text = f"{subject} {user_complaint}".lower()
    detector = EnsembleDetector()
    
    # 1: Quick rule-based spam check
    spam_keywords = ["crypto", "gift", "prize", "congratulations", "wire"] 
    if any(keyword in full_text for keyword in spam_keywords):
        return ["Spam", 0, "Fallback detector triggered due to spam keywords."]
        
    if detector.predict(full_text):
        return ["Spam", 0, "Fallback detector triggered due to high gibberish probability."]

    # 2: Category Determination based on keywords
    BILLING_KEYWORDS = ["invoice", "refund", "charge", "payment", "billing", "overcharged"]
    TECH_KEYWORDS = ["bug", "error", "broken", "login", "crash", "system", "down"]
    
    if any(keyword in full_text for keyword in BILLING_KEYWORDS):
        category = "Billing and Payment"
    elif any(keyword in full_text for keyword in TECH_KEYWORDS):
        category = "Technical Support"
    else:
        category = "General Inquiry"

    # 3: Manual Priority Scoring
    URGENT_KEYWORDS = ["urgent", "asap", "emergency", "immediately", "critical", "lawsuit", "legal action", "breach", "system down", "outage"]
    matched_urgent = [kw for kw in URGENT_KEYWORDS if re.search(rf"\b{kw}\b", full_text)]
    
    if matched_urgent:
        priority_score = 7 
        reasoning = f"AI Offline. Priority elevated to {priority_score} due to urgency keywords."
    else:
        priority_score = 4 
        reasoning = "AI Offline. Processed via standard keyword fallback rules."

    return [category, priority_score, reasoning]

def process_and_save_complaint(email: str, subject: str, body: str):
    

    analysis = analyse_complaint(subject=subject, user_complaint=body)
    
    if analysis is None:
        print("AI processing failed. Routing to fallback rules...")
        analysis = fallback_rule_analysis(subject, body)

    category = analysis[0]
    priority_score = analysis[1]
    reasoning = analysis[2]
    
    team_assignment_rules = {
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
    assigned_to = team_assignment_rules.get(category, "Admin_Team")

    if priority_score == 0 or category == "Spam":
        print(f"Spam/Invalid detected. Not saved to database. Reasoning: {reasoning}")
        print(analysis)
    else:
        save_to_json(email, subject, body, priority_score, assigned_to, category)
        print(f"Success! Saved to JSON. Assigned to: {assigned_to}. Priority: {priority_score} Reasoning: {reasoning}")
        print(analysis)

def complaint_from_json(file_name: str = "complaint.json"):
    try:
        with open(file_name, "r") as file:
            data = json.load(file)
            
        # 2. Extract the list of emails
        email_list = data.get("emails", [])
        
        if not email_list:
            print(f"No emails found in {input_filename}.")
            return 
            
        # 3. Loop through the list and process each email
        for index, record in enumerate(email_list, 1):
            print(f"\n--- Processing Email {index} ---")
            
            # Extract the exact fields (trusting the other managers validated them)
            user_email = record["Email"]
            user_subject = record["Subject"]
            user_body = record["Content"]
            
            # Feed the data into your Logic/Orchestrator layer
            process_and_save_complaint(
                email=user_email, 
                subject=user_subject, 
                body=user_body
            )

    except FileNotFoundError:
        print("Error: The file was not found.")
    except json.JSONDecodeError:
        print("Error: not a valid JSON file.")
    except KeyError as e:
        print(f"Error: Missing expected data field {e} in the JSON file.")

DB_FILE = "complaints_database.json"   #output json

def save_to_json(email: str, subject: str, content: str, category: str, priority_score: int, assigned_to: str):
    new_record = {
        "email_address": email,
        "subject": subject,
        "content": content,
        "category": category,
        "priority_score": priority_score,
        "assigned_to": assigned_to
    }

    records = []
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as file:
                records = json.load(file)
        except (json.JSONDecodeError, IOError):
            logging.warning("Database file missing or corrupted. Creating a new one.")
            records = []

    records.append(new_record)

    try:
        with open(DB_FILE, 'w') as file:
            json.dump(records, file, indent=4) 
    except IOError as e:
        logging.error(f"Failed to save data: {e}")

#if __name__ == "__main__":



    # Fixed the function call to match the required arguments
    # process_and_save_complaint(test_email, test_subject, test_body)
    

# structured output json

# email, subject, complain, (category, priority score, assigned_to) append this to complain.json