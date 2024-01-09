import calendar
from accounts import *
from instruments import *
from scipy.stats import beta

class Reality():


    def __init__(
            self, person_list=[], broker_list=[], instrument_list=[], starting_time_period=0, starting_date = [1, 2024]):
        self.person_list = person_list
        self.broker_list = broker_list
        self.instrument_list = instrument_list
        self.person_data = {}
        self.instrument_data = {}
        self.t = starting_time_period
        self.month_year = starting_date
        self.days_year = self.calculate_days_year(year=self.month_year[1])
        self.beta_d = []
        self.repo_ts = []
        self.repo_lag = -4

    def change_period(self):
        if self.month_year[0] < 12:
            self.month_year[0] += 1
        else:
            self.month_year[0] = 1
            self.month_year[1] += 1
        self.t += 1

    def calculate_days_year(self, year):
        if calendar.isleap(year):
            return 366
        else:
            return 365
        
    def set_days_year(self, year):
        self.days_year = self.calculate_days_year(year=year)

    def add_person(self, person):
        if person in self.person_list:
            print('person already included')
            return
        self.person_list.append(person)

    def add_instrument(self, instrument):
        for inst in self.instrument_list:
            if inst.name == instrument.name:
                print('instrument already included')
                return
        self.instrument_list.append(instrument)
        self.instrument_data[instrument.name] = {}
        self.instrument_data[instrument.name][0] = instrument.price_ts[-1]

    def execute_person_behaviour(self, person, behaviour_dict,
                                  income_change=0, acc_dict=[], acc_instrument_dict={}):
        """Investing behaviour of person is always executed at the beginning of the period
        """

        person.change_monthly_income(income_change=income_change)
        person.receive_monthly_income()
        for id_ in acc_dict:
            person.add_account(id_=id_,
                               company_name=acc_dict['company_name'],
                               type_=acc_dict['type_'],
                               account_type=acc_dict['account_type'])
        for id_ in acc_instrument_dict:
            for instrument_name in acc_instrument_dict[id_]:
                person.add_instrument_to_account(
                    id_=id_, instrument_name=instrument_name)
        person.execute_behaviour(behaviour_dict=behaviour_dict)

    def calculate_accs_totals(self, person):
        """Account totals of the person are calculated at the end of the period
        """

        for account in person.account_list:
            account.calculate_balances(t=self.t)

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
        print('time period executed')
        print(instrument.current_price)
        rcd = RealityDataCollect(t=self.t)
        self.instrument_data = rcd.save_instrument_data(
            instrument=instrument,
            instrument_data=self.instrument_data,
            t=self.t)

    def execute_people_behaviour(self, behaviour_dict):
        for person in self.person_list:
            self.execute_person_behaviour(person=person,
                                           behaviour_dict=behaviour_dict[person.name])
    def reset_person_tax_base(self, person):
        if person.tax_rules.PAYMENT_MONTH != self.month_year[0]:
            return
        person.tax_base['current'] = person.tax_base['next']
        person.tax_base['next'] = 0

    def reset_tax_bases(self):
        for person in self.person_list:
            self.reset_person_tax_base(person=person)

    def set_repo_distribution(self):
        df_all = pd.read_csv('repo.csv', index_col=0)
        df_all["Datum"] = pd.to_datetime(df_all["Datum"])
        df_all.set_index("Datum", inplace=True)
        repo_pct =  df_all[df_all.index > '2012-11-01']['1 měsíc'].dropna()
        a, b, loc, scale = beta.fit(np.array(repo_pct, dtype=float))
        self.beta_d = [a, b, loc, scale]
        print(self.beta_d)
        self.repo_ts = repo_pct[self.repo_lag:]

    def generate_repo_rate(self, coeff=0.6):
        repo_rate = beta.rvs(a=self.beta_d[0],
                       b=self.beta_d[1],
                       loc=self.beta_d[2], 
                        scale=self.beta_d[3], 
                        size=1)
        calc_list = self.repo_ts[self.repo_lag:] + repo_rate
        final_price = (sum(calc_list)/len(calc_list)) * coeff
        self.repo_ts.append(final_price)

        
    def execute_period(self, behaviour_dict):
        """changes to the accounts/indexes employed and adding money to accounts are decided at the beginning of the period
        calculation of account balances then happens at the end of the period"""

        print('time_period: ' )
        self.change_period()
        print(str(self.t))
        self.generate_repo_rate()
        self.reset_tax_bases()
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
        for account in person.account_list:
            accs_dict[account.company_name] = self.save_person_account_data(account=account)
        return accs_dict

    def save_person_account_data(self, account):
        account_dict = {}
        account_dict['amount'] = account.account_balance
        account_dict['instruments'] = self.save_account_instrument_data(
            account=account)
        return account_dict

    def save_account_instrument_data(self, account):
        instrument_dict = {}
        for instrument in account.instrument_dict:
            instrument_dict[instrument] = account.instrument_dict[instrument]
        return instrument_dict
    
    def save_instrument_data(self, instrument, instrument_data, t):
        instrument_data[instrument.name][t] = instrument.current_price
        return instrument_data


class Person():

    def __init__(
            self, name, starting_age, starting_money, current_monthly_income, reality, account_list=[], tax_base={'current': 0, 'next': 0}, nationality='czech'):
        self.name = name
        self.age = starting_age
        self.nationality = nationality
        self.money = starting_money
        self.tax_base = tax_base
        self.current_monthly_income = current_monthly_income 
        self.account_list = account_list
        self.investing_behaviour = {}
        self.reality = reality
        self.tax_rules = tax_rules_factory(nationality=self.nationality)

    def add_account(self, id_, company_name, type_, account_type):
        if company_name not in self.reality.broker_list:
            print("Broker does not exist in this reality")
            return
        account = account_factory(owner=self,
                                  id_=id_, 
                                  type_ = type_, 
                                  company_name=company_name, 
                                  account_type=account_type)
        self.account_list.append(account)

    def delete_account(self, account):
        self.account_list.remove(account)

    def add_instrument_to_account(self, id_, instrument_name):
        acc = self.get_account_by_id(id_=id_)
        if acc is None:
            print('Account does not belong to the person - add inst')
            return
        acc_index =  self.account_list.index(acc)
        self.account_list[acc_index].instrument_dict[instrument_name] = 0

    def add_money_to_account(self, id_, money):
        acc = self.get_account_by_id(id_=id_)
        if acc is None:
            print('Account does not belong to this person- add money acc')
            return
        acc_index =  self.account_list.index(acc)
        self.money -= money
        self.account_list[acc_index].add_money(amount=money)
        print('account balanace after adding money: ')
        print(self.account_list[acc_index].account_balance)

    def take_money_from_account(self, id_, money):
        acc = self.get_account_by_id(id_=id_)
        if acc is None:
            print('Account does not belong to this person-take money acc')
            return
        acc_index =  self.account_list.index(acc)
        self.account_list[acc_index].take_out_money(money=money)

    def add_money_to_instrument(self, account, instrument_name, money):
        account.transfer_money_to_instrument(
            instrument_name=instrument_name, money=money)
        
    def receive_monthly_income(self):
        self.money = self.money + self.current_monthly_income

    def change_monthly_income(self, income_change):
        self.current_monthly_income = (self.current_monthly_income  
                                       + income_change)
                
    def execute_behaviour(self, behaviour_dict):
        for id_ in behaviour_dict:
            account_total = sum(behaviour_dict[id_].values())
            self.add_money_to_account(id_=id_,
                                       money=account_total
                                       *self.current_monthly_income)
            acc = self.get_account_by_id(id_=id_)
            for instrument_name in behaviour_dict[id_]:
                print('reality_index_dict')
                print(behaviour_dict[id_][instrument_name])
                self.add_money_to_instrument(
                    account=acc, instrument_name=instrument_name, 
                    money=(self.current_monthly_income
                          * behaviour_dict[id_][instrument_name]))
        self.pay_taxes()
        
    def spend_money(self, amount, id_):
        if account==None:
            self.money = self.money - amount
            return
        account = self.get_account_by_id(id_=id_)
        if account is None:
            print(
                self.name + ' person does not have an activa account with broker with id ' + id_)
        else:
            pass

    def add_money_to_tax_base(self, month,  money):
        period = self.tax_rules.add_to_tax_base(month=month)
        self.tax_base[period] += money

    def pay_taxes(self):
        if self.reality.month_year[0] != self.tax_rules.PAYMENT_MONTH - 1:
            return
        tax_amount = self.tax_rules.get_income_tax_amount(
            tax_base=self.tax_base['current'])
        self.spend_money(amount=tax_amount)

    def get_account_by_id(self, id_):
        for account in  self.account_list:
            if account.id == id_:
                return account
            
     






        



 