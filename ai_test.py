# Test to check if analyse complaint ai system is working as intended. 
from unittest.mock import patch
from ai_manager import analyse_complaint

# Mock Logic_Main and Logic_Create_Email_List so AI tests don't trigger SQL crashes
with patch("ai_manager.Logic_Main"), patch("ai_manager.Logic_Create_Email_List"):
    # Test 1: Valid Technical Complaint
    print("[Test 1] Testing Valid Technical Support Email")
    result_1 = analyse_complaint(
        email = "john@seed.com",
        subject="System Error 500",
        user_complaint="I cannot log in to my account. It shows a server error.",
    )

    print(f"Category: {result_1[0]} | Priority: {result_1[1]}")

    if 0 < result_1[1] <= 8:
        print("Test 1 PASSED")
    else:
        print("Test 1 FAILED")

    # Test 2: Blatant Spam
    print("[Test 2] Testing Spam Email")
    result_2 = analyse_complaint(
        email = "lottery@gmail.com",
        subject="Claim your $1,000,000 prize now!",
        user_complaint="Click this link immediately for free cash.",
    )

    print(f"Category: {result_2[0]} | Priority: {result_2[1]}")

    if result_2[1] == 0:
        print("Test 2 PASSED")
    else:
        print("Test 2 FAILED")

    # Test 3: Gibberish / Fallback
    print("[Test 3] Testing Gibberish Input")
    result_3 = analyse_complaint(
        email = "swe12@gmail.com",
        subject="asdfghjkl", 
        user_complaint="zxcvbnm 12345"
    )

    print(f"Category: {result_3[0]} | Priority: {result_3[1]}")
    if result_3[1] == 0:
        print("Test 3 PASSED")
    else:
        print("Test 3 FAILED")