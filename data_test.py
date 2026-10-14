from data_manager import *

#testing new_JSON_section()
new_JSON_section()

#testing save_to_SQL(table_name, list_of_data)
test1 = ['sally@yahoo.com', 'strawberry123']
test1failed = ['sally@yahoo.com', 'blueberry456'] #user already exists

test2 = ['sally@yahoo.com', 'broken product', 'I received a broken keyboard', '12-03-2026']
test2failed = ['john@gmail.com', 'hi', '67777']
test2failed2 = 'i want to complain'

test3 = [1, 'Faulty Product', 6, 'Admin Team']
test3failed = 'faulty product'

test4 = [1, 'Faulty Product', '12-03-2026', '14-03-2026', 6, 7]
test4_2 = [3, 'Product Enquiry', '03-03-2026', '10-03-2026', 1, 1]
test4failed = [1, 'Faulty Product', '12-03-2026', 6, 7]
test4failed2 = 'faulty product'

test5 = [2, 'Virus Installed', '24-08-2025', '25-08-2025', 8, 8]
test5_2 = [4, 'Got hacked', '22-10-2026', '23-10-2026', 8, 8]
test5failed = ['Virus Installed', '24-08-2025', '25-08-2025', 8, 8]
test5failed2 = 'got virus'

print('########### TESTING save_to_SQL(table_name, list_of_data) ##############')
save_to_SQL('Accounts', test1)
save_to_SQL('Accounts', test1failed)
print()
save_to_SQL('Emails', test2)
save_to_SQL('Emails', test2failed)
save_to_SQL('Emails', test2failed2)
print()
save_to_SQL('AI_Complaint_Analysis', test3)
save_to_SQL('AI_Complaint_Analysis', test3failed)
print()
save_to_SQL('Admin_Team', test4)
save_to_SQL('Admin_Team', test4_2)
save_to_SQL('Admin_Team', test4failed)
save_to_SQL('Admin_Team', test4failed2)
print()
save_to_SQL('Tech_Professionals', test5)
save_to_SQL('Tech_Professionals', test5_2)
save_to_SQL('Tech_Professionals', test5failed)
save_to_SQL('Tech_Professionals', test5failed2)
print()
save_to_SQL('Front Office', test1)
print()

#testing load_from_SQL(table_name)
print('############### TESTING load_from_SQL(table_name) #################')
load_from_SQL('Admin_Team')
load_from_SQL('Tech_Professionals')
load_from_SQL('Chiikawa')
print()

#testing save_to_JSON(complaint) - can handle a list of dictionaries or a single dictionary input
test6 = [{'Email': 'sally@yahoo.com',
          'Subject': 'Faulty Product',
          'Content': 'I received a broken keyboard'
          },
          {'Email': 'john@gmail.com',
           'Subject': 'Virus Installed',
           'Content': 'I accidentally downloaded a virus and I need help resolving it.'
          }]
test7 = {'Email': 'sally@yahoo.com',
          'Subject': 'Faulty Product',
          'Content': 'I received a broken keyboard'}
test8failed = None #something wrong happened with json file
test9failed = [{'Email': 'sally@yahoo.com',
                'Subject': 'Faulty Product',
                'Content': 'I received a broken keyboard'
                },
                {'Email': 'john@gmail.com',
                'Subject': 'Virus Installed',
                'Content': 'I accidentally downloaded a virus and I need help resolving it.'
                }, 'hello']
test10failed = 'virus'

print('############# TESTING save_to_JSON(complaint) ################')
save_to_JSON(test6)
save_to_JSON(test7)
save_to_JSON(test8failed)
save_to_JSON(test9failed)
save_to_JSON(test10failed)
print()

#testing load_from_JSON()
load_from_JSON()
