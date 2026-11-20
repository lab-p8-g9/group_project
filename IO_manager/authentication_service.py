# Authentication use-case implementation shared by Flask routes.

from typing import Optional, Tuple

from IO_manager.io_manager_interfaces import AccountGateway, AuthenticationUseCase


class AuthenticationService(AuthenticationUseCase):
    # Coordinate customer and employee account operations through a gateway.

    def __init__(self, account_gateway: AccountGateway):
        self._account_gateway = account_gateway

    def create_customer_account(self, email: str, password: str) -> Optional[Tuple]:
        # Persist a new customer account and return its stored account data.
        account = self._account_gateway.customer_account(email, password)
        account.set_account()
        return account.get_account()

    def customer_account(self, email: str, password: str):
        # Retrieve customer account data only when both credentials match.
        return self._account_gateway.customer_account(email, password).authenticate()

    def employee_account(self, email: str, password: str):
        # Retrieve employee account data only for a recognized domain.
        account = self._account_gateway.employee_account(email, password)
        if account is None:
            return None
        return account.authenticate()
