import os
import logging
import re
from pygarble import EnsembleDetector #pip install pygarble
from dotenv import load_dotenv #pip install python-dotenv
from typing import Literal
from pydantic import BaseModel, Field #pip install pydantic
from openai import OpenAI #pip install openai
from data_manager import save_to_SQL

load_dotenv()

openrouter_key = os.getenv("OPENROUTER_API_KEY") #get your own api key

client = OpenAI(
  base_url = "https://openrouter.ai/api/v1",
  api_key = openrouter_key
)

CategoryType = Literal[
    "Security and Fraud",
    "Billing and Payment",
    "Technical Support",
    "Refund",
    "Product/Service Quality",
    "Delivery & Shipping",
    "Account",
    "General Inquiry",
    "Spam"
]

Team_Assignment = {
    "Security and Fraud": "Tech_Professionals",
    "Billing and Payment": "Tech_Professionals",
    "Technical Support": "Tech_Professionals",
    "Refund": "Admin_Team",
    "Product/Service Quality": "Admin_Team",
    "Delivery & Shipping": "Admin_Team",
    "Account": "Admin_Team",
    "General Inquiry": "Admin_Team",
}

URGENT_KEYWORDS = [
    "urgent", "asap", "emergency", "immediately", "critical",
    "lawsuit", "legal action", "breach", "system down", "outage"
]

BILLING_KEYWORDS = ["invoice", "refund", "charge", "payment", "billing", "overcharged"]
TECH_KEYWORDS = ["bug", "error", "broken", "login", "crash", "system", "down"]

class LLMAssessment(BaseModel):
    is_spam: bool = Field(
        description="Set to True if the email is spam or scam"
    )
    category: CategoryType = Field(
        description="Department routing category tag. Set to 'Spam' if is_spam is True."
    )
    priority_score: int = Field(
        ge=0, le=8,
        description="Priority rating (1 to 8). Set to 0 if the email is spam."
    )
    summary: str = Field(description="1-sentence summary of the email.")
    reasoning: str = Field(description="Explanation of the assessment and priority score.")


class FinalComplaintAnalysis(BaseModel):
    category: str
    priority_score: int
    assigned_to: Literal["Tech_Professionals", "Admin_Team", "Spam"]
    summary: str
    reasoning: str

#Exception handling senario if AI system is down    

def fallback_rule_analysis(subject: str, user_complaint: str) -> FinalComplaintAnalysis:
    full_text = f"{subject} {user_complaint}".lower()
    detector = EnsembleDetector()
    
    #1: Quick rule-based spam check
    spam_keywords = ["crypto", "gift", "prize", "congratulations", "wire"] #some typical scam keywords used 
    if any(keywords in full_text for keywords in spam_keywords):
        return FinalComplaintAnalysis(
            is_spam=True,
            category="Spam",
            priority_score=0,
            assigned_to="Spam",
            summary="Flagged as spam by rule fallback.",
            reasoning="Fallback detector triggered due to spam keywords."
        )
    elif detector.predict(full_text):
        return FinalComplaintAnalysis(
            is_spam=True,
            category="Gibberish/Invalid",
            priority_score=0,
            assigned_to="Spam",
            summary="Flagged as invalid text by rule fallback.",
            reasoning="Fallback detector triggered due to high gibberish probability."
        )
    #2: Category Determination based on keywords if AI is not available 
    if any(keywords in full_text for keywords in BILLING_KEYWORDS):
        category = "Billing and Payment"
    elif any(keywords in full_text for keywords in TECH_KEYWORDS):
        category = "Technical Support"
    else:
        category = "General Inquiry"

    assigned_to = Team_Assignment.get(category, "Admin")

    #3: Manual Priority Scoring (Base = 4; Urgent Keywords = 7)
    matched_urgent_words = [keywords for keywords in URGENT_KEYWORDS if re.search(rf"\b{keywords}\b", full_text)]
    
    if matched_urgent_words:
        priority_score = 7  # Elevate priority for urgent complaints
        reasoning = f"AI Offline. Priority elevated to {priority_score} due to urgency keywords: {', '.join(matched_urgent_words)}."
    else:
        priority_score = 4  # Standard medium priority
        reasoning = "AI Offline. Processed via standard keyword fallback rules."

    return FinalComplaintAnalysis(
        is_spam=False,
        category=category,
        priority_score=priority_score,
        assigned_to=assigned_to,
        summary="Processed via non-AI fallback rule.",
        reasoning=reasoning
    )


# Analysis System 

def analyse_complaint(subject: str, user_complaint: str) -> FinalComplaintAnalysis:
    prompt = f"SUBJECT: {subject}\nBODY: {user_complaint}"
    try:
        completion = client.beta.chat.completions.parse(
            model="nvidia/nemotron-3-ultra-550b-a55b:free",   #Can change llm model here eg. openrouter/free or nvidia/nemotron-3-ultra-550b-a55b:free
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI Email Filter and Complaint Manager. "
                        "First, evaluate if the email is spam, gibberish, unsolicited marketing, phishing, or an automated system message. "
                        "If it is valid customer communication, assign a priority score strictly as a whole number from 1 to 8 "
                        "based on situational severity, financial impact, legal risk, and immediate urgency. "
                        "Categorize the issue strictly into one of the allowed complaint categories."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format=LLMAssessment,
        )

        llm_res = completion.choices[0].message.parsed

        if llm_res is None:
            return FinalComplaintAnalysis(
                is_spam=True,
                category="General Inquiry",
                priority_score=0,
                assigned_to="Spam",
                summary="Unprocessable email content.",
                reasoning="Unreadable or gibberish input.",
            )

        if llm_res.is_spam:
            return FinalComplaintAnalysis(
                is_spam=True,
                category=llm_res.category,
                priority_score=0,
                assigned_to="Spam",
                summary=getattr(llm_res, "summary", "N/A"),
                reasoning=llm_res.reasoning,
            )

        assigned_to = Team_Assignment.get(llm_res.category, "Admin") #py will return Tech for "Security and Fraud", "Billing and Payment", and "Technical Support" and Admin for the rest

        return FinalComplaintAnalysis(
            is_spam=False,
            category=llm_res.category,
            priority_score=llm_res.priority_score,
            assigned_to=assigned_to,
            summary=getattr(llm_res, "summary", "N/A"),
            reasoning=llm_res.reasoning,
        )
    except Exception as e:
        # Log the exact error for debugging
        logging.error(f"AI Model failed/unreachable. Error: {e}. Falling back to rule-based logic.")
        
        # Trigger safe non-AI fallback
        return fallback_rule_analysis(subject, user_complaint)


# Passing of Data to Data Manager:
def ai_output_to_sql(complaint_id: int, subject: str, body: str):
    analysis = analyse_complaint(subject=subject, user_complaint=body)
    ai_list_output = [complaint_id, analysis.category, analysis.priority_score, analysis.assigned_to]

    # Filters spam emails from being stored
    if analysis.priority_score == 0:
        pass

    else:
        save_to_SQL('AI_Complaint_Analysis', ai_list_output)

        


#Test working example
if __name__ == "__main__":

    email_subject = input("Enter subject: ")
    email_body = input("Enter content: ")

    ai_output_to_sql(101, email_subject, email_body)