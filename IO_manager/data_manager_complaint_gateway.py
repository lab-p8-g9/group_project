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
    def customer_complaints(self, email: str) -> List[Any]:
        return load_customer_complaints(email)

    def employee_preview(self, department: str) -> List[Any]:
        return load_from_JSON(department)

    def recalculate_unresolved(self, department: str) -> List[Any]:
        return recalculate_logic_score(department).update_all_score()

    def resolved_complaints(self, department: str) -> List[Any]:
        return load_all_resolved(department)

    def resolve_complaint(self, complaint_id: Any) -> bool:
        return resolve(complaint_id)
