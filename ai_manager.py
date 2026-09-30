from typing import Literal
from pydantic import BaseModel, Field
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="insert own api key",
)

CATEGORY_SCORES = {
    "Security and Fraud": {"score": 8, "base_level": "Critical"},
    "Billing and Payment": {"score": 7, "base_level": "High"},
    "Technical Support": {"score": 6, "base_level": "High"},
    "Refund": {"score": 5, "base_level": "High"},
    "Product/Service Quality": {"score": 4, "base_level": "Medium"},
    "Delivery & Shipping": {"score": 3, "base_level": "Medium"},
    "Account": {"score": 2, "base_level": "Low"},
    "General Inquiry": {"score": 1, "base_level": "Low"},
}

CategoryType = Literal[
    "Security and Fraud",
    "Billing and Payment",
    "Technical Support",
    "Refund",
    "Product/Service Quality",
    "Delivery & Shipping",
    "Account",
    "General Inquiry"
]

class LLMAssessment(BaseModel):
    category: CategoryType = Field(
        description="Matched category from the allowed complaint priority list"
    )
    sentiment: Literal["Positive", "Neutral", "Negative"] = Field(
        description="Sentiment detected in the email tone"
    )
    urgency: Literal["Low", "Medium", "High", "Critical"] = Field(
        description="Inferred operational or temporal urgency"
    )
    reasoning: str = Field(
        description="Brief justification for category, sentiment, and urgency assignment"
    )


class FinalComplaintAnalysis(BaseModel):
    category: str
    sentiment: str
    urgency: str
    waiting_time_days: int
    initial_priority_score: int
    aging_adjustment: int
    final_priority_score: int
    priority_level: str
    recommended_action: str
    reasoning: str


def calculate_initial_score(category: str, sentiment: str, urgency: str) -> int:
    """Calculates Initial Priority Score (0-100 scale) using Category weight, Sentiment, and Urgency."""
    cat_weight = CATEGORY_SCORES.get(category, {}).get("score", 1) * 5  # Max 40 points
    
    urgency_weights = {"Low": 10, "Medium": 20, "High": 35, "Critical": 45} # Max 45 points
    sentiment_weights = {"Positive": 0, "Neutral": 5, "Negative": 15}       # Max 15 points
    
    score = cat_weight + urgency_weights.get(urgency, 10) + sentiment_weights.get(sentiment, 5)
    return min(100, score)


def map_final_level(score: int) -> tuple[str, str]:
    """Maps Final Score to Priority Level and Recommended Action."""
    if score >= 80:
        return "Critical", "Escalate immediately to senior lead / supervisor"
    elif score >= 65:
        return "High", "Escalate to tier-2 support team"
    elif score >= 40:
        return "Medium", "Standard queue processing"
    else:
        return "Low", "Automated / standard response queue"


def analyse_complaint(subject: str, body: str, waiting_time_days: int = 0) -> FinalComplaintAnalysis:
    """Combines LLM feature extraction with deterministic scoring rules."""
    
    prompt = f"""
    Analyse this customer email and extract category, sentiment, and urgency:
    
    SUBJECT: {subject}
    BODY: {body}
    """

    completion = client.beta.chat.completions.parse(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",      #Can change llm model here
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a customer service triage agent. Classify complaints accurately "
                    "into standard categories and evaluate sentiment and urgency."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format=LLMAssessment,
    )

    llm_out = completion.choices[0].message.parsed

    # Calculate initial score and aging adjustment
    initial_score = calculate_initial_score(llm_out.category, llm_out.sentiment, llm_out.urgency)
    
    # Aging adjustment: +3.75 points per waiting day (wait time heightened to max after 1 week (8 days), score capped at 30)
    aging_adjustment = min(30, int(waiting_time_days * 3.75))
    
    final_score = min(100, initial_score + aging_adjustment)
    priority_level, action = map_final_level(final_score)

    return FinalComplaintAnalysis(
        category=llm_out.category,
        sentiment=llm_out.sentiment,
        urgency=llm_out.urgency,
        waiting_time_days=waiting_time_days,
        initial_priority_score=initial_score,
        aging_adjustment=aging_adjustment,
        final_priority_score=final_score,
        priority_level=priority_level,
        recommended_action=action,
        reasoning=llm_out.reasoning,
    )


#Test working example
if __name__ == "__main__":
    email_subject = "Poor attitude of staff at Flagship Outlet"
    email_body = (
        "The staff, xxx, was very unhelpful in answering my questions and was very condesending."
        "Manager was also not in post at that time when I wanted to complain about the staff"
    )
    
    result = analyse_complaint(
        subject=email_subject, 
        body=email_body, 
        waiting_time_days=1             #can be changed accordingly
    )

    print("\n--- AI Analysis Result ---")
    print(f"Category:               {result.category}")
    print(f"Sentimental:            {result.sentiment}")
    print(f"Urgency:                {result.urgency}")
    print(f"Waiting time:           {result.waiting_time_days} days")
    print(f"Initial Priority score: {result.initial_priority_score} (based on category, sentimental and Urgency)")
    print(f"Aging Adjustment:       {result.aging_adjustment} (based on waiting time)")
    print(f"Final Priority score:   {result.final_priority_score} — {result.priority_level}")
    print(f"Recommended action:     {result.recommended_action}")