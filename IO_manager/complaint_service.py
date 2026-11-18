# Complaint use-case implementation that coordinates gateways and analysis.

from typing import Any, List

from IO_manager.io_manager_interfaces import (
    ComplaintAnalyzer,
    ComplaintGateway,
    ComplaintUseCase,
)


class ComplaintService(ComplaintUseCase):
    # Provide complaint loading, resolution, and AI analysis operations.

    def __init__(
        self,
        complaint_gateway: ComplaintGateway,
        analyzer: ComplaintAnalyzer,
    ):
        self._complaint_gateway = complaint_gateway
        self._analyzer = analyzer

    def customer_complaints(self, email: str) -> List[Any]:
        # Load complaints submitted by one customer.
        return self._complaint_gateway.customer_complaints(email)

    def employee_preview(self, department: str) -> List[Any]:
        # Load the department complaint preview.
        return self._complaint_gateway.employee_preview(department)

    def all_employee_complaints(self, department: str) -> List[Any]:
        # Combine unresolved and resolved complaints for an employee view.
        complaints = self._complaint_gateway.recalculate_unresolved(department)
        complaints.extend(self._complaint_gateway.resolved_complaints(department))
        return complaints

    def resolve_complaint(self, complaint_id: Any) -> bool:
        # Delegate a complaint resolution request to the gateway.
        return self._complaint_gateway.resolve_complaint(complaint_id)

    def analyze_complaint(self, email: str, subject: str, complaint: str) -> List[Any]:
        # Analyze complaint text and return the analyzer's classification.
        return self._analyzer.analyze(email, subject, complaint)
