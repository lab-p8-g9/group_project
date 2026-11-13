from flask import Flask

from IO_manager.account_gateway import DataManagerAccountGateway
from IO_manager.activity_summary import ActivitySummary
from IO_manager.authentication_service import AuthenticationService
from IO_manager.complaint_service import ComplaintService
from IO_manager.credential_validator import CredentialValidator
from IO_manager.data_manager_complaint_gateway import DataManagerComplaintGateway
from IO_manager.io_manager_controller import IOManager
from IO_manager.openrouter_complaint_analyzer import OpenRouterComplaintAnalyzer


app = Flask(__name__)
activity_summary = ActivitySummary()
credential_validator = CredentialValidator()
authentication_service = AuthenticationService(DataManagerAccountGateway())
complaint_service = ComplaintService(
    DataManagerComplaintGateway(),
    OpenRouterComplaintAnalyzer(),
)
io_manager = IOManager(
    app,
    authentication_service,
    complaint_service,
    credential_validator,
    activity_summary,
)
io_manager.register_routes()

# Preserve the module-level helpers and route callables for existing imports.
log = activity_summary.log
summary = io_manager.summary
validate_user_input = io_manager.validate_user_input
alertBox = io_manager.alertBox
home = io_manager.home
emailPage = io_manager.emailPage
employeeLoginPage = io_manager.employeeLoginPage
customerPage = io_manager.customerPage
employeePage = io_manager.employeePage
viewComplaintPage = io_manager.viewComplaintPage
accountPage = io_manager.accountPage
employeeHomePage = io_manager.employeeHomePage
resolving = io_manager.resolving
submit = io_manager.submit


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True, threaded=False)
