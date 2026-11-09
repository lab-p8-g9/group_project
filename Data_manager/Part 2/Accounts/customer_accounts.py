from accounts import Account 

class Customer(Account):
    def __init__(self, address, password):
        super().__init__(address, password)
        self.role = 'Customer'

    