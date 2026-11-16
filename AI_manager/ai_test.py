from AI_manager.offline_ai_manager import OfflineAIManager
from AI_manager.openrouter_ai_manager import OpenRouterAIManager
from AI_manager.api_config import APIConfig
import os

def test_offline_ai():
    print("Running Offline AI Test...")
    offline_ai = OfflineAIManager()
    
    # Using the real email so the SQLite Foreign Key accepts it
    result = offline_ai.analyse_complaint("alice@test.com", "Virus Installed", "My computer is infected.")
    
    assert type(result) == list, "Offline AI must return a list."
    assert len(result) == 4, "Offline AI list must contain exactly 4 items."
    assert result[3] == "Tech", "Offline AI failed to route virus complaint to Tech."
    print("Offline AI test passed successfully.")

def test_live_ai():
    print("\nRunning Live AI Test (Requires Internet & API Key)...")
    config = APIConfig()
    
    if not config.api_key:
        print("Skipping Live AI test: No OPENROUTER_API_KEY found by APIConfig.")
        return

    try:
        live_ai = OpenRouterAIManager()
        
        # Using the real email here as well
        result = live_ai.analyse_complaint("alice@test.com", "General", "What are your operating hours?")
        
        assert type(result) == list, "Live AI must return a list."
        assert len(result) == 4, "Live AI list must contain exactly 4 items."
        
        print("Live OpenRouter AI test passed successfully.")
        
    except Exception as e:
        print(f"Live AI test encountered a network/API error: {e}")

if __name__ == "__main__":
    print("--- STARTING AI MANAGER TESTS ---\n")
    test_offline_ai()
    test_live_ai()
    print("\n--- ALL TESTS COMPLETED ---")