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

    def __init__(self, company_name, owner, type_, account_type, 
                 account_balance=0, instrument_dict={}):
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
        self.instrument_dict[instrument.name] = 0
    
    def delete_instrument(self, instrument):
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
        self.account_balance -= amount

    @abstractmethod 
    def calculate_balances(self):
        pass


class TransactionAccount(Account):


    def __init__(self, owner, company_name, account_type, account_balance=0,
                  period_interest=None, interest=1):
        super().__init__(owner=owner,
                        company_name=company_name,
                        type_="transaction",
                        account_type=account_type,
                        account_balance = account_balance)
        self.period_interest = period_interest
        self.interest = interest
        self.instrument_dict = {}
    
    def send_money(self, person, account_name, amount):
        allowed = self.rules.execute_send_money_rules(self.account_balance)
        if allowed == False:
            print('Money can not be sent')
            return
        self.account_balance -= amount
        account = person.get_account_by_name(account_name=account_name)
        account.account_balance += amount

    def calculate_balances(self, t):
        if self.period_interest % t == 0:
            self.account_balance = self.account_balance * self.interest


class SavingsAccount(Account):

    def __init__(self, owner, company_name, account_type,
                account_balance=0, period_interest=None, 
                interest=0):
        super().__init__(owner=owner,
                        company_name=company_name,
                        type_="savings",
                        starting_amount = account_balance,
                        account_type=account_type)
        self.period_interest = period_interest
        self.interest = interest

    @abstractmethod 
    def calculate_balances(self):
        pass

class BrokerAccount(Account):
        
        def __init__(self, owner, company_name,  
                     instrument_dict={}, starting_amount=0, available_instruments=[]):
            super().__init__(owner=owner,                  
                            company_name=company_name,
                            account_type="broker",
                            instrument_dict=instrument_dict,
                            starting_amount = starting_amount)
            self.available_instruments = available_instruments

        def calculate_instrument_amount(self, instrument_name):
            if instrument_name not in self.instrument_dict:
                print('Instrument is not active in current account')
                return
            curr_price = self.owner.reality.instrument_data[instrument_name][-1]
            prev_price = self.owner.reality.instrument_data[instrument_name][-2]
            multip = (curr_price) / (prev_price)
            self.instrument_dict[instrument_name] = self.instrument_dict[instrument_name] * multip

        def calculate_balances(self):
            for instrument_name in self.instrument_dict:
                self.calculate_instrument_amount(instrument_name=instrument_name)

        def transfer_money_to_instrument(self, instrument_name, money):
            if money > self.account_amount:
                print('Not enough money for the transaction')
                return
            self.account_amount = self.account_amount - money
            self.instrument_dict[instrument_name] = (self.instrument_dict[instrument_name] + money)
            print('money')
            print(money)
            print('instrument ' + instrument_name  + ": ")
            print(self.instrument_dict[instrument_name])


class XTB(Account):

    def __init__(
            self, owner, broker_name, starting_instrument_dict,
            starting_amount):
        super().__init__(
            owner=owner, broker_name=broker_name, starting_instrument_dict=starting_instrument_dict,
            starting_amount=starting_amount)
            


def account_factory(type_, **kwargs):
    if type_ == "broker":
        return BrokerAccount(**kwargs)
    elif type_ == "savings":
        return SavingsAccount(**kwargs)
    elif type_ == "transaction":
        return TransactionAccount(**kwargs)
