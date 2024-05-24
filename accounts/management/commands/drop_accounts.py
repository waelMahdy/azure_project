from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Drops the accounts_account table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE IF EXISTS  accounts_Account;')
            self.stdout.write(self.style.SUCCESS('Successfully dropped the accounts_account table'))
# def drop_accounts():
#     try:
         
#          with connection.cursor() as cursor:
#             cursor.execute('DROP TABLE IF EXISTS accounts_Account;')
#     except Exception as e:
#         print(f"Error deleting accounts: {e}")        
# drop_accounts()
