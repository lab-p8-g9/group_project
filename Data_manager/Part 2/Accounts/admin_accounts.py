from accounts import Account 

class AdminA(Account):
    def __init__(self, address, password):
        super().__init__(address, password)
        self.role = 'Admin'

    