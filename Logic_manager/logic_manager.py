from Logic_manager.logic_main import logic_main
from Data_manager.data_manager2 import db, c




if __name__ == "__main__":



    # Create an object from your new processing class
    process = logic_main("ai_output.json")

    # Call its method to process all AI samples
    process.process_ai_sample()

    print("AI sample processed successfully!")