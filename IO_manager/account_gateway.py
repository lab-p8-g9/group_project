# Gateway adapter that creates account objects for each supported role.

from typing import Optional

from Data_manager.accounts import Account
from Data_manager.admin_accounts import AdminA
from Data_manager.customer_accounts import CustomerA
from Data_manager.tech_accounts import TechA

from IO_manager.io_manager_interfaces import AccountGateway


class DataManagerAccountGateway(AccountGateway):
    # Translate account requests into Data Manager account implementations.

    def customer_account(self, email: str, password: str) -> Account:
        # Create the account object used by customer sign-up and login.
        return CustomerA(email, password)

    def employee_account(self, email: str, password: str) -> Optional[Account]:
        # Route recognized employee domains to their matching account role.
        if "@admin.com" in email:
            return AdminA(email, password)
        if "@tech.com" in email:
            return TechA(email, password)
        return None
