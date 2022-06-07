from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bank_app.models import Account, Ledger


class Command(BaseCommand):
    def handle(self, **options):
        print('Adding demo data ...')

        bank_user = User.objects.create_user('bank', email='', password='bankpassword')
        bank_user.is_active = False
        bank_user.save()
        ipo_account = Account.objects.create(user=bank_user, title='Bank IPO Account')
        ops_account = Account.objects.create(user=bank_user, title='Bank OPS Account')
        stock_account = Account.objects.create(user=bank_user, title='Bank Stock Account')
        Ledger.transfer(
            10_000_000,
            ipo_account, # debit
            'Operational Credit',
            ops_account, # credit
            'Operational Credit',
            is_loan=True
        )