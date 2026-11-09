from Data_manager.accounts import Account

class TechA(Account):
    def assign_role(self): #for own usage
        return 'Tech'
    
    def __init__(self, address, password):
        super().__init__(address, password)
    
