# Gateway adapter for complaint operations in the Data Manager.

from typing import Any, List

from Data_manager.data_manager2 import (
    load_all_resolved,
    load_customer_complaints,
    load_from_JSON,
    resolve,
)
from Logic_manager.logic_recalculate_score import recalculate_logic_score

from IO_manager.io_manager_interfaces import ComplaintGateway


class DataManagerComplaintGateway(ComplaintGateway):
    # Translate complaint use cases into Data Manager function calls.

    def customer_complaints(self, email: str) -> List[Any]:
        # Load a customer's complaints from the Data Manager.
        return load_customer_complaints(email)

    def employee_preview(self, department: str) -> List[Any]:
        # Load unresolved complaint preview data for the department.
        return load_from_JSON(department)

    def recalculate_unresolved(self, department: str) -> List[Any]:
        # Recalculate and return unresolved complaint scores.
        return recalculate_logic_score(department).update_all_score()

    def resolved_complaints(self, department: str) -> List[Any]:
        # Load the department's resolved complaints.
        return load_all_resolved(department)

    def resolve_complaint(self, complaint_id: Any) -> bool:
        # Mark one complaint as resolved in the Data Manager.
        return resolve(complaint_id)
