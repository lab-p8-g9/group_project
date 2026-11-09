from Data_manager.accounts import Account

class CustomerA(Account):
    def assign_role(self): #for own usage 
        return 'Customer'
    
    def __init__(self, address, password):
        super().__init__(address, password)

    