from Data_manager.accounts import Account

class AdminA(Account):
    def assign_role(self) -> str: #for own usage 
        return 'Admin'
    
    def __init__(self, address: str, password: str) -> None:
        super().__init__(address, password)

    