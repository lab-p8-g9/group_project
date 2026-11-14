import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from IO_manager.account_gateway import DataManagerAccountGateway
from IO_manager.activity_summary import ActivitySummary
from IO_manager.authentication_service import AuthenticationService
from IO_manager.complaint_service import ComplaintService
from IO_manager.credential_validator import CredentialValidator
from IO_manager.io_manager_interfaces import (
    AccountGateway,
    ComplaintAnalyzer,
    ComplaintGateway,
)
from IO_manager.openrouter_complaint_analyzer import OpenRouterComplaintAnalyzer


class FakeAccount:
    def __init__(self, account_data):
        self.account_data = account_data
        self.created = False

    def set_account(self):
        self.created = True
        return True

    def get_account(self):
        return self.account_data


class FakeAccountGateway(AccountGateway):
    def __init__(self, customer_data=None, employee_data=None):
        self.customer_data = customer_data
        self.employee_data = employee_data
        self.customer = FakeAccount(customer_data)
        self.created_employee = None

    def customer_account(self, email, password):
        return self.customer

    def employee_account(self, email, password):
        if self.employee_data is None:
            return None
        self.created_employee = FakeAccount(self.employee_data)
        return self.created_employee


class FakeComplaintGateway(ComplaintGateway):
    def __init__(self):
        self.unresolved = [
            (1, "customer@example.com", "General", "Open complaint", "", "", 3, 4, "Unresolved")
        ]
        self.resolved = [
            (2, "customer@example.com", "Billing", "Closed complaint", "", "", 2, 2, "Resolved")
        ]
        self.resolved_ids = []

    def customer_complaints(self, email):
        return [("customer@example.com", email)]

    def employee_preview(self, department):
        return self.unresolved[:]

    def recalculate_unresolved(self, department):
        return self.unresolved[:]

    def resolved_complaints(self, department):
        return self.resolved[:]

    def resolve_complaint(self, complaint_id):
        self.resolved_ids.append(complaint_id)
        return True


class FakeComplaintAnalyzer(ComplaintAnalyzer):
    def __init__(self):
        self.arguments = None

    def analyze(self, subject, complaint):
        self.arguments = (subject, complaint)
        return ["General Inquiry", 4, "Valid complaint", "Admin"]


class CredentialValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = CredentialValidator()

    def test_accepts_valid_credentials(self):
        self.assertEqual(
            self.validator.validate("person@example.com", "StrongPassword1!"),
            "Valid input.",
        )

    def test_rejects_invalid_email(self):
        self.assertEqual(
            self.validator.validate("invalid-email", "StrongPassword1!"),
            "Error: Invalid email format.",
        )

    def test_rejects_weak_password(self):
        self.assertTrue(
            self.validator.validate("person@example.com", "weak").startswith(
                "Error: Password must be"
            )
        )


class ActivitySummaryTests(unittest.TestCase):
    def test_records_and_prints_summary_actions(self):
        activity_summary = ActivitySummary()
        activity_summary.summary("Update", "Complaint analyzed")

        output = StringIO()
        with redirect_stdout(output):
            activity_summary.summary("Fetch")

        self.assertEqual(activity_summary.log, ["Complaint analyzed"])
        self.assertIn("1)Complaint analyzed", output.getvalue())


class AuthenticationServiceTests(unittest.TestCase):
    def test_customer_signup_creates_and_returns_account(self):
        expected = ("person@example.com", "StrongPassword1!", "Customer")
        gateway = FakeAccountGateway(customer_data=expected)
        service = AuthenticationService(gateway)

        result = service.create_customer_account("person@example.com", "StrongPassword1!")

        self.assertTrue(gateway.customer.created)
        self.assertEqual(result, expected)

    def test_employee_login_returns_none_for_unmatched_domain(self):
        service = AuthenticationService(FakeAccountGateway())

        self.assertIsNone(service.employee_account("person@example.com", "StrongPassword1!"))


class AccountGatewayTests(unittest.TestCase):
    def test_routes_email_domains_to_account_types(self):
        gateway = DataManagerAccountGateway()
        email = "person@example.com"
        password = "StrongPassword1!"

        with (
            patch("IO_manager.account_gateway.CustomerA") as customer_class,
            patch("IO_manager.account_gateway.AdminA") as admin_class,
            patch("IO_manager.account_gateway.TechA") as tech_class,
        ):
            self.assertIs(
                gateway.customer_account(email, password),
                customer_class.return_value,
            )
            self.assertIs(
                gateway.employee_account("person@admin.com", password),
                admin_class.return_value,
            )
            self.assertIs(
                gateway.employee_account("person@tech.com", password),
                tech_class.return_value,
            )
            self.assertIsNone(gateway.employee_account(email, password))

        customer_class.assert_called_once_with(email, password)
        admin_class.assert_called_once_with("person@admin.com", password)
        tech_class.assert_called_once_with("person@tech.com", password)


class ComplaintServiceTests(unittest.TestCase):
    def setUp(self):
        self.gateway = FakeComplaintGateway()
        self.analyzer = FakeComplaintAnalyzer()
        self.service = ComplaintService(self.gateway, self.analyzer)

    def test_returns_unresolved_before_resolved(self):
        complaints = self.service.all_employee_complaints("Admin")

        self.assertEqual(
            [complaint[8] for complaint in complaints],
            ["Unresolved", "Resolved"],
        )

    def test_resolve_delegates_to_gateway(self):
        self.assertTrue(self.service.resolve_complaint("17"))
        self.assertEqual(self.gateway.resolved_ids, ["17"])

    def test_analysis_delegates_to_analyzer(self):
        result = self.service.analyze_complaint("Subject", "Complaint text")

        self.assertEqual(result[1], 4)
        self.assertEqual(self.analyzer.arguments, ("Subject", "Complaint text"))

    def test_loads_customer_complaints(self):
        complaints = self.service.customer_complaints("customer@example.com")

        self.assertEqual(complaints, [("customer@example.com", "customer@example.com")])

    def test_loads_employee_preview(self):
        self.assertEqual(self.service.employee_preview("Admin"), self.gateway.unresolved)


class OpenRouterAnalyzerTests(unittest.TestCase):
    def test_delegates_to_openrouter_manager(self):
        expected = ["General Inquiry", 4, "Reason", "Admin"]
        with patch(
            "IO_manager.openrouter_complaint_analyzer.OpenRouterAIManager"
        ) as manager_class:
            manager_class.return_value.analyse_complaint.return_value = expected

            result = OpenRouterComplaintAnalyzer().analyze("Subject", "Complaint")

        manager_class.return_value.analyse_complaint.assert_called_once_with(
            "Subject",
            "Complaint",
        )
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
