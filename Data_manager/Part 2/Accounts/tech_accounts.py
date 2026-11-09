from accounts import Account 

class TechA(Account):
    def __init__(self, address, password):
        super().__init__(address, password)
        self.role = 'Tech'
    
