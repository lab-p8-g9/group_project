from typing import Optional

from Data_manager.accounts import Account
from Data_manager.admin_accounts import AdminA
from Data_manager.customer_accounts import CustomerA
from Data_manager.tech_accounts import TechA

from IO_manager.io_manager_interfaces import AccountGateway


class DataManagerAccountGateway(AccountGateway):
    def customer_account(self, email: str, password: str) -> Account:
        return CustomerA(email, password)

    def employee_account(self, email: str, password: str) -> Optional[Account]:
        if "@admin.com" in email:
            return AdminA(email, password)
        if "@tech.com" in email:
            return TechA(email, password)
        return None
