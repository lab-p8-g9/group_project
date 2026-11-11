
import sys
import sqlite3
from pathlib import Path

# Allow imports from Data_manager folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Data_manager import data_manager2 as dm
from Data_manager.accounts import Account
from Data_manager.admin_accounts import AdminA
from Data_manager.tech_accounts import TechA
from Data_manager.customer_accounts import CustomerA
from Data_manager.all_emails import Email
from Data_manager.admin_emails import AdminE
from Data_manager.tech_emails import TechE

ivan = CustomerA('ivan@gmail.com', 'sjudcbfia')
print(ivan.get_account())