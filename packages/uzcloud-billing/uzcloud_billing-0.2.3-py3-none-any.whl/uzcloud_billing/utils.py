import requests
import jwt
import json

from django.conf import settings
import uzcloud_billing.models as billing_models

from uzcloud_billing.services import update_account_balance

from .decorators import auth_required


class Singleton(type):
    _instances = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]


class UzcloudBilling(metaclass=Singleton):
    AUTH_URL = settings.UZCLOUD_BILLING["AUTH_URL"]
    BILLING_BASE_URL = settings.UZCLOUD_BILLING["BASE_URL"]
    ADD_ACCOUNT_URL = f"{BILLING_BASE_URL}/api/Account/AddAccount"
    GET_BALANCE_URL = f"{BILLING_BASE_URL}/api/Balance/GetBalance"
    MAKE_INVOICE_URL = f"{BILLING_BASE_URL}/api/Invoice/MakeInvoice"

    AUTH_TOKEN = None
    REQUEST_CONFIG = {"verify": False}

    def __init__(self) -> None:
        self.authorize()

    def authorize(self):
        response = requests.post(
            url=self.AUTH_URL,
            data={"grant_type": "client_credentials"},
            auth=(
                settings.UZCLOUD_BILLING["CLIENT_ID"],
                settings.UZCLOUD_BILLING["CLIENT_SECRET"],
            ),
            **self.REQUEST_CONFIG,
        )
        if response.status_code != 200:
            raise ValueError(response.content)
        self.AUTH_TOKEN = response.json()["access_token"]
        self.DECODED = jwt.decode(self.AUTH_TOKEN, options={"verify_signature": False})

    @auth_required
    def add_account(self):
        payload = {"personType": 1}
        response = requests.post(
            url=self.ADD_ACCOUNT_URL,
            data=json.dumps(payload),
            headers=self.get_headers(),
            **self.REQUEST_CONFIG,
        )
        if response.status_code != 200:
            raise ValueError(response.content)
        return response.json()

    @auth_required
    def get_balance(self, account_number):
        response = requests.get(
            url=self.GET_BALANCE_URL,
            params={"accountNumber": account_number},
            headers=self.get_headers(),
            **self.REQUEST_CONFIG,
        )
        if response.status_code != 200:
            raise ValueError(response.content)
        update_account_balance(
            billing_account=billing_models.BillingAccount.objects.get(
                account_number=account_number
            ),
            balance=response["Amount"],
        )
        return response.json()

    @auth_required
    def make_invoice(self, account_number: str, amount: float, reason: str):
        payload = {
            "AccountNumber": account_number,
            "Amount": amount,
            "Reason": reason,
        }
        response = requests.post(
            self.MAKE_INVOICE_URL,
            data=json.dumps(payload),
            headers=self.get_headers(),
            **self.REQUEST_CONFIG,
        )
        if response.status_code != 200:
            raise ValueError(response.json())
        response = response.json()
        update_account_balance(
            billing_account=billing_models.BillingAccount.objects.get(
                account_number=account_number
            ),
            balance=response["Balance"],
        )
        return response

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.AUTH_TOKEN}",
            "Content-Type": "application/json",
        }


uzcloud_service = UzcloudBilling()


def generate_account_number():
    account = uzcloud_service.add_account()
    return account["AccountNumber"]
