import os

from dotenv import load_dotenv
from typing import Literal
from pydantic import BaseModel, Field
from openai import OpenAI
#from io_manager import IOmanager

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
    "Security and Fraud": "Tech",
    "Billing and Payment": "Tech",
    "Technical Support": "Tech",
    "Refund": "Admin",
    "Product/Service Quality": "Admin",
    "Delivery & Shipping": "Admin",
    "Account": "Admin",
    "General Inquiry": "Admin",
}

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
    assigned_to: Literal["Tech", "Admin", "Spam"]
    summary: str
    reasoning: str


def analyse_complaint(subject: str, body: str) -> FinalComplaintAnalysis:
    prompt = f"SUBJECT: {subject}\nBODY: {body}"

    completion = client.beta.chat.completions.parse(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",   #Can change llm model here eg. openrouter/free
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI Email Filter and Complaint Manager. "
                    "First, evaluate if the email is spam, unsolicited marketing, phishing, or an automated system message. "
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


#Test working example
if __name__ == "__main__":
    email_subject = "Nigerian prince "
    email_body = "My oil business closed down. Ill give you 500 million"

    # Call function directly without instantiating a class object
    decision = analyse_complaint(subject=email_subject, body=email_body)
    
    if decision:
        print(f"Category: {decision.category} | Priority: {decision.priority_score} | Assigned To: {decision.assigned_to}")