# Abstract interfaces between IO manager services and external implementations.

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from Data_manager.accounts import Account


class AccountGateway(ABC):
    # Contract for constructing customer and employee account objects.

    @abstractmethod
    def customer_account(self, email: str, password: str) -> Account:
        raise NotImplementedError

    @abstractmethod
    def employee_account(self, email: str, password: str) -> Optional[Account]:
        raise NotImplementedError


class AuthenticationUseCase(ABC):
    # Contract for account creation and customer or employee authentication.

    @abstractmethod
    def create_customer_account(self, email: str, password: str):
        raise NotImplementedError

    @abstractmethod
    def customer_account(self, email: str, password: str):
        raise NotImplementedError

    @abstractmethod
    def employee_account(self, email: str, password: str):
        raise NotImplementedError


class ComplaintGateway(ABC):
    # Contract for data access operations involving complaints.

    @abstractmethod
    def customer_complaints(self, email: str) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def employee_preview(self, department: str) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def recalculate_unresolved(self, department: str) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def resolved_complaints(self, department: str) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def resolve_complaint(self, complaint_id: Any) -> bool:
        raise NotImplementedError


class ComplaintUseCase(ABC):
    # Contract for complaint actions exposed by the IO manager.

    @abstractmethod
    def customer_complaints(self, email: str) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def employee_preview(self, department: str) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def all_employee_complaints(self, department: str) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def resolve_complaint(self, complaint_id: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def analyze_complaint(self, email: str, subject: str, complaint: str) -> List[Any]:
        raise NotImplementedError


class ComplaintAnalyzer(ABC):
    # Contract for services that classify and prioritize complaints.

    @abstractmethod
    def analyze(self, email: str, subject: str, complaint: str) -> List[Any]:
        raise NotImplementedError
