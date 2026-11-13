from Data_manager.accounts import Account

class CustomerA(Account):
    def assign_role(self) -> str: #for own usage 
        return 'Customer'
    
    def __init__(self, address: str, password: str) -> None:
        super().__init__(address, password)

    