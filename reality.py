from abc import ABC, abstractmethod

class Reality():


    def __init__(
            self, person_list=[], broker_list=[], instrument_list=[], starting_time_period=0):
        self.person_list = person_list
        self.broker_list = broker_list
        self.instrument_list = instrument_list
        self.person_data = {}
        self.instrument_data = {}
        self.t = starting_time_period

    def add_person(self, person):
        if person in self.person_list:
            print('person already included')
            return
        self.person_list.append(person)

    def add_instrument(self, instrument):
        if instrument in self.instrument_list:
            print('instrument already included')
            return
        self.instrument_list.append(instrument)

    def execute_person_behaviour(self, person, behaviour_dict,
                                  income_change=0, acc_list=[], acc_instrument_dict={}):
        """Investing behaviour of person is always executed at the beginning of the period
        """

        person.change_monthly_income(income_change=income_change)
        person.receive_monthly_income()
        for acc in acc_list:
            person.add_account(booker_account=acc)
        for acc in acc_instrument_dict:
            for instrument_name in acc_instrument_dict[acc]:
                person.add_instrument_to_account(
                    account_name=acc, instrument_name=instrument_name)
        person.execute_investing_behaviour(behaviour_dict=behaviour_dict)

    def calculate_accs_totals(self, person):
        """Account totals of the person are calculated at the end of the period
        """

        for account in person.broker_accs:
            account.calculate_inst_amount_wraper()

    def calculate_all_peeople_accs_totals(self):
        rcd = RealityDataCollect(t=self.t)
        for person in self.person_list:
            self.calculate_accs_totals(person=person)
            self.person_data = rcd.save_person_data(
                person=person,
                person_data=self.person_data)

    def execute_instruments_period(self):
        for instrument in self.instrument_list:
            self.execute_instrument_period(instrument=instrument)

    def execute_instrument_period(self, instrument):
        instrument.execute_time_period(t=self.t)
        rcd = RealityDataCollect(t=self.t)
        self.instrument_data = rcd.save_instrument_data(
            instrument=instrument,
            instrument_data=self.instrument_data)

    def execute_people_behaviour(self, behaviour_dict):
        for person in self.person_list:
            self.execute_person_behaviour(person=person,
                                           behaviour_dict=behaviour_dict[person.name])
        
    def execute_period(self, behaviour_dict):
        """changes to the accounts/indexes employed and adding money to accounts are decided at the beginning of the period
        calculation of account balances then happens at the end of the period"""

        self.t += 1
        self.execute_people_behaviour(behaviour_dict=behaviour_dict)
        self.execute_instruments_period()
        self.calculate_all_peeople_accs_totals()



class RealityDataCollect():


    def __init__(self, t):
        self.t = t

    def save_person_data(self, person, person_data):
        if person.name not in person_data:
              person_data[person.name] = {}
        person_data[person.name][self.t] = self.save_person_period(      
            person=person)
        return person_data
        
    def save_person_period(self, person):
        data_dict = {}
        data_dict['amount'] = person.money
        data_dict['income'] = person.current_monthly_income
        data_dict['age'] = person.age
        data_dict['accounts'] = self.save_person_accounts_data(person=person)
        return data_dict

    def save_person_accounts_data(self, person):
        accs_dict = {}
        for account in person.broker_accs:
            accs_dict[account.broker_name] = self.save_person_account_data(account=account)
        return accs_dict

    def save_person_account_data(self, account):
        account_dict = {}
        account_dict['amount'] = account.account_amount
        account_dict['instruments'] = self.save_account_instrument_data(
            account=account)
        return account_dict

    def save_account_instrument_data(self, account):
        instrument_dict = {}
        for instrument in account.instrument_dict:
            instrument_dict[instrument] = account.instrument_dict[instrument]
        return instrument_dict
    
    def save_instrument_data(self, instrument, instrument_data):
        if instrument.name not in instrument_data:
            instrument_data[instrument.name] = [instrument.price_ts[-1]]
            print(instrument_data)
        instrument_data[instrument.name].append(instrument.current_price)
        return instrument_data


class Person():

    def __init__(
            self, name, starting_age, starting_money, current_monthly_income, reality, broker_acounts=[]):
        self.name = name
        self.age = starting_age
        self.money = starting_money
        self.current_monthly_income = current_monthly_income 
        self.broker_accs = broker_acounts
        self.investing_behaviour = {}
        self.reality = reality

    def add_account(self, broker_name):
        if broker_name not in self.reality.broker_list:
            print("Broker does not exist in this reality")
            return
        account = Account(owner=self, broker_name=broker_name)
        self.broker_accs.append(account)

    def delete_account(self, account):
        self.broker_accs.remove(account)

    def add_instrument_to_account(self, account_name, instrument_name):
        acc = self.get_account_by_name(account_name=account_name)
        if acc is None:
            print('Account does not belong to the person - add inst')
            return
        acc_index =  self.broker_accs.index(acc)
        print(acc_index) 
        self.broker_accs[acc_index].instrument_dict[instrument_name] = 0
        print('instrument dict')
        print(self.broker_accs[acc_index].instrument_dict)

    def add_money_to_account(self, account_name, money):
        acc = self.get_account_by_name(account_name=account_name)
        if acc is None:
            print('Account does not belong to this person- add money acc')
            return
        acc_index =  self.broker_accs.index(acc)
        self.money -= money
        self.broker_accs[acc_index].add_money(money=money)
        print(self.broker_accs[acc_index].account_amount)

    def take_money_from_account(self, account_name, money):
        acc = self.get_account_by_name(account_name=account_name)
        if acc is None:
            print('Account does not belong to this person-take money acc')
            return
        acc_index =  self.broker_accs.index(acc)
        self.broker_accs[acc_index].take_out_money(money=money)

    def add_money_to_instrument(self, account, instrument_name, money):
        account.transfer_money_to_instrument(
            instrument_name=instrument_name, money=money)
        
    def receive_monthly_income(self):
        self.money = self.money + self.current_monthly_income

    def change_monthly_income(self, income_change):
        self.current_monthly_income = (self.current_monthly_income  
                                       + income_change)
                
    def execute_investing_behaviour(self, behaviour_dict):
        for account_name in behaviour_dict:
            account_total = sum(behaviour_dict[account_name].values())
            print('account_total: ' + str(account_total))
            self.add_money_to_account(account_name=account_name,
                                       money=account_total
                                       *self.current_monthly_income)
            acc = self.get_account_by_name(account_name=account_name)
            for instrument_name in behaviour_dict[account_name]:
                print('reality_index_dict')
                print(behaviour_dict[account_name][instrument_name])
                self.add_money_to_instrument(
                    account=acc, instrument_name=instrument_name, 
                    money=(self.current_monthly_income
                          * behaviour_dict[account_name][instrument_name]))
                
    def get_account_by_name(self, account_name):
        print(account_name)
        for account in  self.broker_accs:
            print(account.broker_name)
            if account.broker_name == account_name:
                print('yes')
                return account
            
     
class Account():

    def __init__(self, owner, broker_name, starting_instrument_dict={}, starting_amount=0):
        self.broker_name = broker_name
        self.owner = owner
        self.instrument_dict = starting_instrument_dict
        self.account_amount  = starting_amount

    def add_money(self, money):
        self.account_amount += money

    def take_out_money(self, money):
        self.account_amount -= money

    def add_instrument(self, instrument):
        self.instrument_dict[instrument.name] = 0
    
    def delete_instrument(self, instrument):
        if self.instrument_dict[instrument.name] != 0:
            print('can delete account, there are still money in it')
            return
        del self.instrument_dict[instrument.name]

    def calculate_instrument_amount(self, instrument_name):
        if instrument_name not in self.instrument_dict:
            print('Instrument is not active in current account')
            return
        curr_price = self.owner.reality.instrument_data[instrument_name][-1]
        prev_price = self.owner.reality.instrument_data[instrument_name][-2]
        multip = (curr_price) / (prev_price)
        print('multip')
        print(multip)
        self.instrument_dict[instrument_name] = self.instrument_dict[instrument_name] * multip
        print(self.instrument_dict[instrument_name])

    def calculate_inst_amount_wraper(self):
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


class  Instrument(ABC):

    def __init__(self, name, type_):
        self.name = name
        self.type = type_
        self.multip = 1

    @abstractmethod
    def execute_time_period(self):
        pass


class Index(Instrument):

    def __init__(
            self, name, reality, type_='index', price_ts=[], current_price=None):
        super().__init__(name, type_)
        self.current_price = current_price
        self.price_ts = price_ts
        self.reality = reality

    def calculate_current_price(self, t, mma_length):
        self.current_price = self.ts_calc(mma_length)
        self.price_ts.append(self.current_price)
        print('Current Price: ')
        print(self.current_price)

    def ts_calc(self, mma_length):
        if len(self.price_ts) < mma_length:
            print('We need at least ' 
                  + str(mma_length) 
                  + " previous observations")
            return
        print(self.price_ts[len(self.price_ts) - (mma_length): ])
        current_price = ((sum(self.price_ts[len(self.price_ts) - (mma_length): ]))  / (mma_length))
        return current_price
            
    def execute_time_period(self, t):
        self.calculate_current_price(t=t, mma_length=20)


class TransactionAccount(Instrument):

    def __init__(self, name, type_='trans_account'):
        super().__init__(type_, name)

    def execute_time_period(self):
        pass




        



 