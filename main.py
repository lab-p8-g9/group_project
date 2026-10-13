#import all functions from io_manager to main.py
from io_manager import *

initialize()
choices = Menu()

while (choices != 5):
    match choices:
        case 1:
            Account()
        case 2:
            inputComplaint()
        case 3:
            loadSQL()
        case 4:
            summary("Fetch")
    choices = Menu()
summary("Fetch")