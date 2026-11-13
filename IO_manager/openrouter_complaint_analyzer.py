from typing import Any, List

from AI_manager.openrouter_ai_manager import OpenRouterAIManager

from IO_manager.io_manager_interfaces import ComplaintAnalyzer


class OpenRouterComplaintAnalyzer(ComplaintAnalyzer):
    def analyze(self, subject: str, complaint: str) -> List[Any]:
        return OpenRouterAIManager().analyse_complaint(subject, complaint)
