# Project Initial Details
1. Data and user input:
    - Subject Line 
    - Email Body
    - Timestamp (Date and Time received)
2. AI Classification
    - Categorisation: Automatically map inbound emails to one of 8 pre-defined categories (Security & Fraud, Billing, Technical, Refund, Product Quality, Delivery, Account, General Inquiry).
    - Urgency and Sentiment Analsyis: Detect urgency (Crtitical, High, Medium, Low) and sentiment (Postitive, Neutral, Negative) from email context.
    - Dyanmic Priority Scoring:
        - Calculate Initial Priority Score using: Category Base Score + Sentiment + Urgency
        - Calculate Aging Adjustment dynamically based on total unresolved waiting time. 
        - Compute Final Priority Score: Inital Score + Aging Adjustment 
    - Recommended Action: Output the Next Step (eg. Escalate, Standard Queue)

3. Business Rules and Automation
    - SLA Timers: Assign strict response deadlines tied directly to the calculated priority level.
    - Auto-Escalation Threshold: Trigger an SLA breach alert/expedition flag when an unresolved ticket reaches 80% of its response deadline.
    - Constraint Checking: Validate AI output against mandatory workflow constraints before updating the agent queue.