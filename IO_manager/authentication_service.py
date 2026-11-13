from typing import Optional, Tuple

from IO_manager.io_manager_interfaces import AccountGateway, AuthenticationUseCase


class AuthenticationService(AuthenticationUseCase):
    def __init__(self, account_gateway: AccountGateway):
        self._account_gateway = account_gateway

    def create_customer_account(self, email: str, password: str) -> Optional[Tuple]:
        account = self._account_gateway.customer_account(email, password)
        account.set_account()
        return account.get_account()

    def customer_account(self, email: str, password: str):
        return self._account_gateway.customer_account(email, password).get_account()

    def employee_account(self, email: str, password: str):
        account = self._account_gateway.employee_account(email, password)
        if account is None:
            return None
        return account.get_account()
