from accounts.models import Account
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Deletes all accounts'

    def handle(self, *args, **options):
        # This will delete all accounts from the database
        Account.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all accounts'))
def delete_all_accounts():
    try:
        # Delete all records from the accounts table
        Account.objects.all().delete()
        print("All accounts deleted successfully.")
    except Exception as e:
        print(f"Error deleting accounts: {e}")

# Call the function to delete all accounts
delete_all_accounts()