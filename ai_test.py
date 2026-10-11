# Test to check if analyse complaint as well as the fallback fucntion is working
# Turn off wifi to test for fallback function. 

from ai_manager import FinalComplaintAnalysis, analyse_complaint

# Test 1: Valid Technical Complaint
print("[Test 1] Testing Valid Technical Support Email")
result_1 = analyse_complaint(
    subject="System Error 500",
    user_complaint="I cannot log in to my account. It shows a server error.",
)

print(f"Category: {result_1.category} | Priority: {result_1.priority_score} | Assigned To: {result_1.assigned_to}")

if result_1.priority_score > 0:
    print("Test 1 PASSED")
else:
    print("Test 1 FAILED")

# Test 2: Blatant Spam
print("[Test 2] Testing Spam Email")
result_2 = analyse_complaint(
    subject="Claim your $1,000,000 prize now!",
    user_complaint="Click this link immediately for free cash.",
)

print(f"Category: {result_2.category} | Priority: {result_2.priority_score}")

if result_2.priority_score == 0 and result_2.assigned_to == "Spam":
    print("Test 2 PASSED")
else:
    print("Test 2 FAILED")

# Test 3: Gibberish / Fallback
print("[Test 3] Testing Gibberish Input")
result_3 = analyse_complaint(
    subject="asdfghjkl", 
    user_complaint="zxcvbnm 12345"
)

print(f"Category: {result_2.category} | Priority: {result_2.priority_score}")
if result_3.priority_score == 0:
    print("Test 3 PASSED")
else:
    print("Test 3 FAILED")