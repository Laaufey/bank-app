from curses.ascii import FF
from multiprocessing import context
from tokenize import blank_re
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
import requests
import environ
import uuid
from .models import Account, Customer, Ledger, StockHoldings
from django.contrib.auth.models import User
from .forms import createAccount, createCustomer, createUser, UpdateUserForm, UpdateCustomerForm, TransferForm, LoanForm, TickerForm, SellStockForm, StockForm
from decimal import Decimal
from rest_framework import permissions
from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from twilio.rest import Client
from .stocks import get_meta_data, get_price_data, get_apple_price, get_google_price, get_microsoft_price, get_amazon_price, get_tesla_price, get_tesla_info


def index(request):
    return render(request, 'bank_app/index.html')


@login_required
def home(request):
    user = request.user
    if request.method == "POST":
        account_form = createAccount(request.POST)
        if account_form.is_valid():
            Account.objects.create(user=User.objects.get(
                pk=user.id), title=account_form.cleaned_data['title'])
    if request.user.is_staff:
        context = {
            'form': createAccount,
            'accounts': Account.objects.all(),
            'user_id': user.id,
            'customers': Customer.objects.all(),
        }
        return render(request, 'bank_app/staff.html', context)
    else:
        context = {
            'form': createAccount,
            'accounts': Account.objects.all(),
            'user_id': user.id,
            'customers': Customer.objects.all(),
        }
        return render(request, 'bank_app/home.html', context)


@login_required
def accounts(request):
    user = request.user
    context = {
        'accounts': Account.objects.all(),
        'user_id': user.id,
        'ledger': Ledger.objects.all(),
        'count': Account.objects.count()
    }
    return render(request, 'bank_app/accounts.html', context)


@login_required
def loans(request):
    user = request.user
    if not request.user.customer.customer_rank == "GOLD" and not request.user.customer.customer_rank == "silver":
        context = {

        }
        return render(request, 'bank_app/loans.html', context)
    if request.method == "POST":
        loan_form = LoanForm(request.POST)
        loan_form.fields['account'].queryset = request.user.customer.accounts
        if loan_form.is_valid():
            amount = loan_form.cleaned_data['amount']
            loan_account = Account.objects.create(
                user=request.user, title="Loan Account", account_type='Loan Account')
            account = Account.objects.get(
                pk=loan_form.cleaned_data['account'].pk)
            debit_text = loan_form.cleaned_data['debit_text']
            credit_text = loan_form.cleaned_data['credit_text']
            is_loan = True
            transfer = Ledger.transfer(
                amount, loan_account, debit_text, account, credit_text, is_loan)
            print(transfer)
            return HttpResponseRedirect('/loans')
    else:
        loan_form = LoanForm()
        loan_form.fields['account'].queryset = request.user.customer.accounts
    context = {
        'user_id': user.id,
        'customers': Customer.objects.all(),
        'loan_form': loan_form,
        'accounts': Account.objects.all(),
        'ledger': Ledger.objects.all()
    }
    return render(request, 'bank_app/loans.html', context)


@login_required
def loan_details(request, id):
    account = Account.objects.filter(id=id)
    # transactions = Ledger.objects.filter(transaction_id=transaction_id)
    # print(transactions)
    if request.method == "POST":
        loan_form = LoanForm(request.POST)
        loan_form.fields['account'].queryset = request.user.customer.accounts
        if loan_form.is_valid():
            amount = loan_form.cleaned_data['amount']
            customer_account = Account.objects.get(
                pk=loan_form.cleaned_data['account'].pk)
            # account = Account.objects.get(pk=11) #The Bank
            account = Account.objects.get(pk=id)
            debit_text = loan_form.cleaned_data['debit_text']
            credit_text = loan_form.cleaned_data['credit_text']
            transfer = Ledger.transfer(
                amount, customer_account, debit_text, account, credit_text)
            print(transfer)
            return HttpResponseRedirect(f'/loan_details/{id}')
    else:
        loan_form = LoanForm()
        loan_form.fields['account'].queryset = request.user.customer.accounts

    context = {
        # 'transactions':transactions,
        'account': account,
        'accounts': Account.objects.all(),
        'loan_form': loan_form,
    }
    return render(request, 'bank_app/loan_details.html', context)


@login_required
def transfer(request):

    if request.method == "POST":
        transfer_form = TransferForm(request.POST)
        transfer_form.fields['debit_account'].queryset = Account.objects.filter(
            user=request.user, account_type='Savings account' or 'Debit card' or 'Credit card')
        if transfer_form.is_valid():
            credit_bank_id = transfer_form.cleaned_data['credit_bank']
            amount = transfer_form.cleaned_data['amount']
            debit_text = transfer_form.cleaned_data['debit_text']
            credit_text = transfer_form.cleaned_data['credit_text']

            # Internal bank transfers
            if credit_bank_id == 1:
                debit_account = Account.objects.get(
                    pk=transfer_form.cleaned_data['debit_account'].pk)
                credit_account = Account.objects.get(
                    pk=transfer_form.cleaned_data['credit_account'])
                transfer = Ledger.transfer(
                    amount, debit_account, debit_text, credit_account, credit_text)
                print(transfer)
                env = environ.Env()
                environ.Env.read_env()
                account_sid = env("TWILIO_ACCOUNT_SID")
                auth_token = env('TWILIO_AUTH_TOKEN')
                client = Client(account_sid, auth_token)
                number = Customer.objects.get(
                    user_id=credit_account.user_id).phone_number
                message = client.messages \
                    .create(
                        body=f"You got sent {amount} kr. from {request.user}. Explaination:{debit_text}",
                        from_='+14782092875',
                        to=f"{number}"
                    )
                print(message.sid)
                print(Customer.objects.get(
                    user_id=credit_account.user_id).phone_number)
                return HttpResponseRedirect('/transfer')

            # External bank transfers
            elif credit_bank_id == 2:
                env = environ.Env()
                environ.Env.read_env()
                bank_auth_key_1 = env("BANK_AUTH_KEY_1")
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': bank_auth_key_1
                }
                transaction_id = uuid.uuid4()
                account = Account.objects.get(
                    pk=transfer_form.cleaned_data['debit_account'].pk)
                bank = Account.objects.get(title="Bank IPO Account")
                text = transfer_form.cleaned_data['credit_text']
                id = request.POST["credit_account"]
                print("id: ", id)
                # transfer = Ledger.externalTransfer(amount, debit_account, debit_text, bank, credit_text)
                find_account_url = (
                    "http://127.0.0.1:7000/api/v1/get-account/?id=%s" % id)
                transfer_url = f"http://127.0.0.1:7000/api/v1/external-transfer/?id={id}&transaction_id={transaction_id}&amount={amount}&text={text}"
                print("find account url: ", find_account_url)
                print("transfer url: ", transfer_url)
                account_response = requests.get(find_account_url)
                if account_response.ok:
                    print("Found the account")
                    # print(transfer)
                    transfer_response = requests.post(
                        transfer_url, headers=headers)
                    print(transfer_response)
                    if transfer_response.ok:
                        print("response ok")
                        try:
                            Ledger.externalTransfer(
                                amount=amount,
                                debit_account=account,
                                debit_text=debit_text,
                                credit_account=bank,
                                credit_text=credit_text,
                                transaction_id=transaction_id,
                            )
                        except Exception:
                            print("External transfer error")

                else:
                    print("Account not found")
    else:
        transfer_form = TransferForm()
        transfer_form.fields['debit_account'].queryset = Account.objects.filter(
            user=request.user, account_type='Savings account' or 'Debit card' or 'Credit card')

        # print(transfer_form.fields['debit_account'].queryset)
    context = {
        'transfer_form': transfer_form
    }
    return render(request, 'bank_app/transfer.html', context)


@login_required
def profile(request):
    user = request.user
    update_user_form = UpdateUserForm(instance=user)
    if request.method == "POST":
        update_user_form = UpdateUserForm(request.POST, instance=user)
        if update_user_form.is_valid:
            update_user_form.save()

    context = {
        'update_user_form': update_user_form,
        'user_id': user.id,
        'customers': Customer.objects.all()
    }
    return render(request, 'bank_app/profile.html', context)

# Stocks


@login_required
def stocks(request):
    user = request.user
    if request.method == 'POST':
        form = TickerForm(request.POST)
        if form.is_valid():
            ticker = request.POST['ticker']
            return HttpResponseRedirect(ticker)
    else:
        form = TickerForm()
        context = {
            'apple_price': get_apple_price(),
            'google_price': get_google_price(),
            'microsoft_price': get_microsoft_price(),
            'amazon_price': get_amazon_price(),
            'tesla_price': get_tesla_price(),
            'tesla_info': get_tesla_info(),
            'ticker_form': form,
            'stock_holdings': StockHoldings.objects.all()
        }

    return render(request, 'bank_app/stocks.html', context)


@login_required
def ticker(request, tid):
    price_data = get_price_data(tid)
    meta_data = get_meta_data(tid)
    holding_id = StockHoldings.objects.get(holding_id=5).shares
    print(holding_id)

    if request.method == "POST":
        buy_stock_form = StockForm(request.POST)
        sell_stock_form = SellStockForm(request.POST)
        sell_stock_form.fields['stock_holdings'].queryset = StockHoldings.objects.filter(
            user=request.user)
        sell_stock_form.fields['debit_account'].queryset = Account.objects.filter(
            user=request.user, account_type='Savings account' or 'Debit card' or 'Credit card')
        buy_stock_form.fields['debit_account'].queryset = Account.objects.filter(
            user=request.user, account_type='Savings account' or 'Debit card' or 'Credit card')

        if buy_stock_form.is_valid():
            stock_value = price_data['close']
            # company_name = meta_data['name']
            stock_amount = buy_stock_form.cleaned_data['stock_amount']
            amount_transfered = stock_value * stock_amount
            debit_account = buy_stock_form.cleaned_data['debit_account']
            credit_account = Account.objects.get(title='Bank Stock Account')
            text = "buy stocks"

            stock_holding = StockHoldings.objects.create(
                user=request.user, company="Apple Inc", ticker=tid, shares=stock_amount, bought_at=amount_transfered)

            transfer = Ledger.transfer(
                amount_transfered, debit_account, text, credit_account, text)
            print("AMOUNT", amount_transfered)
            print(stock_holding)
            print(transfer)
            return HttpResponseRedirect('/stocks')

        if sell_stock_form.is_valid():
            stock_value = price_data['close']

            holding_id = StockHoldings.objects.get(
                pk=sell_stock_form.cleaned_data['stock_holdings'].pk)
            print(holding_id.holding_id)
            print(holding_id)
            stock_amount = holding_id.shares
            amount_transfered = stock_value * stock_amount
            debit_account = Account.objects.get(title='Bank Stock Account')
            credit_account = sell_stock_form.cleaned_data['debit_account']
            text = "sell stocks"

            delete_stock_holding = StockHoldings.objects.filter(
                pk=holding_id.holding_id).delete()

            transfer = Ledger.transfer(
                amount_transfered, debit_account, text, credit_account, text)
            print(delete_stock_holding)
            print(transfer)
            return HttpResponseRedirect('/stocks')
    else:
        sell_stock_form = SellStockForm()
        buy_stock_form = StockForm()
        buy_stock_form.fields['debit_account'].queryset = Account.objects.filter(
            user=request.user, account_type='Savings account' or 'Debit card' or 'Credit card')
        sell_stock_form.fields['debit_account'].queryset = Account.objects.filter(
            user=request.user, account_type='Savings account' or 'Debit card' or 'Credit card')
        sell_stock_form.fields['stock_holdings'].queryset = StockHoldings.objects.filter(
            user=request.user)

    context = {
        'ticker': tid,
        'meta': meta_data,
        'price': price_data,
        'buy_stock_form': buy_stock_form,
        'sell_stock_form': sell_stock_form,
    }

    return render(request, 'bank_app/ticker.html', context)


# Admin
@login_required
def staff(request):
    assert request.user.is_staff, 'Not for regular customers, only for admin'
    context = {
        'customers': Customer.objects.all(),
    }
    return render(request, 'bank_app/staff.html', context)


@login_required
def staffCustomerView(request):
    user = request.user
    assert request.user.is_staff, 'Not for regular customers, only for admin'
    context = {
        'user_id': user.id,
        'customers': Customer.objects.all(),
    }
    return render(request, 'bank_app/staffCustomerView.html', context)


@login_required
def staff_customer_details(request, id):
    assert request.user.is_staff, 'Not for regular customers, only for admin'
    user = User.objects.get(pk=id)
    customer = Customer.objects.get(user_id=user.id)
    update_customer_form = UpdateCustomerForm(instance=customer)
    update_user_form = UpdateUserForm(instance=user)
    if request.method == "POST":
        update_customer_form = UpdateCustomerForm(
            request.POST, instance=customer)
        update_user_form = UpdateUserForm(request.POST, instance=user)
        if update_customer_form.is_valid:
            update_customer_form.save()
        if update_user_form.is_valid:
            update_user_form.save()
    context = {
        'customer': user,
        'update_customer_form': update_customer_form,
        'update_user_form': update_user_form,
    }
    return render(request, 'bank_app/staff_customer_details.html', context)


@login_required
def staffAccountView(request):
    assert request.user.is_staff, 'Not for regular customers, only for admin'
    context = {
        'accounts': Account.objects.all(),
    }
    return render(request, 'bank_app/staffAccountView.html', context)


@login_required
def staffNewCustomer(request):
    assert request.user.is_staff, 'Not for regular customers, only for admin'
    if request.method == "POST":
        customer_form = createCustomer(request.POST)
        user_form = createUser(request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            username = user_form.cleaned_data['username']
            first_name = user_form.cleaned_data['first_name']
            last_name = user_form.cleaned_data['last_name']
            email = user_form.cleaned_data['email']
            password = user_form.cleaned_data['password']
            phone_number = customer_form.cleaned_data['phone_number']
            customer_rank = customer_form.cleaned_data['customer_rank']
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password)
            print(f'New customer with username: {username} and email: {email}')
            Customer.objects.create(
                user=user, phone_number=phone_number, customer_rank=customer_rank)
    context = {
        'customer_form': createCustomer,
        'user_form': createUser,
        'customers': Customer.objects.all(),
    }
    return render(request, 'bank_app/staffNewCustomer.html', context)


@login_required
def staffNewAccount(request):
    assert request.user.is_staff, 'Not for regular customers, only for admin'
    user = request.user
    if request.method == "POST":
        account_form = createAccount(request.POST)
        if account_form.is_valid():
            Account.objects.create(
                user=account_form.cleaned_data['user'],
                title=account_form.cleaned_data['title'])
    context = {
        'account_form': createAccount,
        'accounts': Account.objects.all(),
        'user_id': user.id,
        'customers': Customer.objects.all(),
    }
    return render(request, 'bank_app/staffNewAccount.html', context)


@login_required
def staffTransfers(request):
    assert request.user.is_staff, 'Not for regular customers, only for admin'
    transfer_form = TransferForm()
    # transfer_form.fields['debit_account'].queryset = request.user.customer.accounts
    if request.method == "POST":
        transfer_form = TransferForm(request.POST)
        if transfer_form.is_valid():
            debit_account = Account.objects.get(
                pk=transfer_form.cleaned_data['debit_account'])
            credit_account = Account.objects.get(
                pk=transfer_form.cleaned_data['credit_account'])
            amount = transfer_form.cleaned_data['amount']
            transfer = Ledger.transfer(amount, debit_account, credit_account)
            print(transfer)
    else:
        transfer_form = TransferForm()
    context = {
        'transfer_form': TransferForm
    }

    return render(request, 'bank_app/staffTransfers.html', context)
