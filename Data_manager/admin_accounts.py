from Data_manager.accounts import Account

class AdminA(Account):
    def assign_role(self): #for own usage 
        return 'Admin'
    
    def __init__(self, address, password):
        super().__init__(address, password)

    