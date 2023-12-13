


def account_factory(company_name):
    if company_name == "xtb""


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
        print(instrument_name)
        print(self.owner.reality.instrument_data[instrument_name])
        curr_price = self.owner.reality.instrument_data[instrument_name][-1]
        prev_price = self.owner.reality.instrument_data[instrument_name][-2]
        print(instrument_name)
        print('curr_price')
        print(str(curr_price))
        print('previous_price')
        print(str(prev_price))
        multip = (curr_price) / (prev_price)
        print('multip')
        print(type(multip))
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


class XTB(Account):

    def __init__(
            self, owner, broker_name, starting_instrument_dict,
            starting_amount):
        super().__init__(
            owner=owner, broker_name=broker_name, starting_instrument_dict=starting_instrument_dict,
            starting_amount=starting_amount)
            

