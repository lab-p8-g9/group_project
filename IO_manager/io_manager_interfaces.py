from abc import ABC, abstractmethod
from typing import Any, List, Optional

from Data_manager.accounts import Account


class AccountGateway(ABC):
    @abstractmethod
    def customer_account(self, email: str, password: str) -> Account:
        raise NotImplementedError

    @abstractmethod
    def employee_account(self, email: str, password: str) -> Optional[Account]:
        raise NotImplementedError


class AuthenticationUseCase(ABC):
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
    def analyze_complaint(self, subject: str, complaint: str) -> List[Any]:
        raise NotImplementedError


class ComplaintAnalyzer(ABC):
    @abstractmethod
    def analyze(self, subject: str, complaint: str) -> List[Any]:
        raise NotImplementedError
