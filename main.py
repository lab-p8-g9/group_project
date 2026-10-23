#import all functions from io_manager to main.py
from io_manager import *

initialize()

try:
    choices = Menu()
    while (choices != 5):
        if(choices == 1):
            Account()
        elif(choices == 2):
            inputComplaint()
        elif(choices == 3):
            loadSQL()
        elif(choices == 4):
            summary("Fetch")
        else:
            print("\nThis is an invalid choice. Please enter a number between 1 - 5\n")     
        choices = Menu()
except ValueError:
    print("\nInvalid type, Please enter a number between 1- 5\n")
    choices = Menu()


summary("Fetch")