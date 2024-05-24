from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'create the accounts_account table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('CREATE TABLE "accounts_account" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "first_name" varchar(50) NOT NULL, "last_name" varchar(50) NOT NULL, "username" varchar(50) NOT NULL UNIQUE, "email" varchar(200) NOT NULL UNIQUE, "phone_number" varchar(50) NOT NULL, "date_joined" datetime NOT NULL, "last_login" datetime NOT NULL, "is_admin" bool NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "is_superadmin" bool NOT NULL);')
            self.stdout.write(self.style.SUCCESS('Successfully craeted the accounts table'))