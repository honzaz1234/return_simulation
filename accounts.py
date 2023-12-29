import calendar
from accounts_rules import *
from abc import ABC, abstractmethod
            
     

class AccountFactory(ABC):

    @abstractmethod
    def create_transaction_account():
        pass

    @abstractmethod
    def create_savings_account():
        pass

    
class Account(ABC):

    def __init__(self, id_, company_name, owner, type_, account_type, 
                 account_balance=0, instrument_dict={}):
        self.id = id_
        self.company_name = company_name
        self.owner = owner
        self.type = type_
        self.account_type = account_type
        self.instrument_dict = instrument_dict
        self.account_balance  = account_balance
        self.rules = account_rules_factory(company=company_name,
                                           type=self.type, 
                                           account_type=self.account_type)

    def add_instrument(self, instrument):
        allowed = self.rules.execute_add_instrument_rules()
        if allowed == False:
            print('Instrument can not be added to the account')
            return
        self.instrument_dict[instrument.name] = 0
    
    def delete_instrument(self, instrument):
        allowed = self.rules.execute_delete_instrument_rules()
        if allowed == False:
            print('Instrument can not be deleted from the account')
            return
        if self.instrument_dict[instrument.name] != 0:
            print('can delete account, there are still money in it')
            return
        del self.instrument_dict[instrument.name]

    def add_money(self, amount):
         allowed = self.rules.execute_add_money_rules(self.account_balance)
         if allowed == False:
            print('money can not be added')
            return
         self.account_balance += amount

    def take_out_money(self, amount):
        allowed = self.rules.execute_take_out_money_rules(self.account_balance)
        if allowed == False:
            print('money can not be taken out')
            return
        self.account_balance -= amount

    @abstractmethod 
    def calculate_balances(self, t):
        self.rules.execute_account_management_payment_rules()

class TransactionAccount(Account):


    def __init__(self, id_, owner, company_name, account_type,
                 account_balance=0, period_interest=1, interest=1):
        super().__init__(id_=id_,
                        owner=owner,
                        company_name=company_name,
                        type_="transaction",
                        account_type=account_type,
                        account_balance = account_balance)
        self.period_interest = period_interest
        self.interest = interest
    
    def send_money(self, person, id_, amount):
        allowed = self.rules.execute_send_money_rules(self.account_balance)
        if allowed == False:
            print('Money can not be sent')
            return
        self.account_balance -= amount
        account = person.get_account_by_id(id_=id_)
        account.account_balance += amount

    def calculate_balances(self, t):
        super().calculate_balances(t=t)
        if self.period_interest % t == 0:
            self.account_balance = self.account_balance * self.interest


class SavingsAccount(Account):

    def __init__(self, id_, owner, company_name, account_type,
                account_balance=0, period_interest=None, 
                interest=0):
        super().__init__(id_=id_,
                        owner=owner,
                        company_name=company_name,
                        type_="savings",
                        account_balance = account_balance,
                        account_type=account_type)
        self.period_interest = period_interest
        self.interest = interest

    def calculate_interest(self):
        curr_month = self.owner.reality.month_year[0]
        curr_year = self.owner.reality.month_year[1]
        n_days = self.owner.reality.days_year
        n_days = calendar.monthrange(curr_year, curr_month)[1]
        interest = self.account_balance * ((self.interest * (n_days / 36600)))
        return interest

    def set_interest(self):
        pass

    @abstractmethod 
    def calculate_balances(self, t):
        interest = self.calculate_interest()
        self.account_balance += interest
        self.owner_add_money_to_tax_base(money=interest)
        super().calculate_balances()

class BrokerAccount(Account):
        
        def __init__(self, id_, owner, company_name, account_type, 
                    account_balance=0, available_instruments=[],instrument_dict = {}):
            super().__init__(id_=id_,
                            owner=owner,                  
                            company_name=company_name,
                            type_="broker",
                            account_balance = account_balance,
                            account_type=account_type,
                            instrument_dict=instrument_dict)
            self.available_instruments = available_instruments

        def calculate_instrument_amount(self, instrument_name, t):
            if instrument_name not in self.instrument_dict:
                print('Instrument is not active in current account')
                return
            curr_price = self.owner.reality.instrument_data[instrument_name][t]
            prev_price = self.owner.reality.instrument_data[instrument_name][t-1]
            multip = (curr_price) / (prev_price)
            self.instrument_dict[instrument_name] = self.instrument_dict[instrument_name] * multip

        def calculate_balances(self, t):
            for instrument_name in self.instrument_dict:
                self.calculate_instrument_amount(
                    instrument_name=instrument_name, 
                    t=t)

        def transfer_money_to_instrument(self, instrument_name, money):
            if money > self.account_balance:
                print('Not enough money for the transaction')
                return
            self.account_balance = self.account_balance - money
            self.instrument_dict[instrument_name] = (self.instrument_dict[instrument_name] + money)



        
def account_factory(type_, **kwargs):
    if type_ == "broker":
        return BrokerAccount(**kwargs)
    elif type_ == "savings":
        return SavingsAccount(**kwargs)
    elif type_ == "transaction":
        return TransactionAccount(**kwargs)
