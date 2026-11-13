from Data_manager.accounts import Account

class TechA(Account):
    def assign_role(self) -> str: #for own usage
        return 'Tech'
    
    def __init__(self, address: str, password: str) -> None:
        super().__init__(address, password)
    
