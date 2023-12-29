from abc import ABC, abstractmethod


class AccountRulesCreator(ABC):


    def execute_add_money_rules(self, amount):
        return True
        
        
    def execute_take_out_money_rules(self, amount):
        return True
    
    def execute_add_instrument_rules(self):
        return True
    
    def execute_delete_instrument_rules(self):
        return True

    @abstractmethod
    def execute_account_management_payment_rules(self):
        pass


class TransactionAccountRules(AccountRulesCreator):


    def execute_send_money_rules(self):
        return True
    
    def set_interest_rate(self):
        return 1.0

    
class  KBMujUcetGold(TransactionAccountRules):

    def execute_send_money_rules(self, account_balance):
        pass

    def execute_account_management_payment_rules(self, account_balance):
        account_balance -= 169

class KBMujUcetPlus(TransactionAccountRules):

    def execute_send_money_rules(self, account_balance):
        pass    

    def execute_account_management_payment_rules(self, account_balance):
        account_balance -= 169

class KBStudentskyUcetG2(TransactionAccountRules):

        def execute_send_money_rules(self, account_balance):
            pass 
        
        def execute_account_management_payment_rules(self):
            pass

class KBMujUcet(TransactionAccountRules):

        def execute_send_money_rules(self, account_balance):
            if account_balance < 6:
                print('Cannot perform the transaction, too low account balance')
                return False
            account_balance -= 6
            return True
        
        def execute_account_management_payment_rules(self):
            pass

        def set_interest_rate(self):
            return 1.05

class KBUcetJunior(TransactionAccountRules):

        def execute_send_money_rules(self, account_balance):
            pass 
        
        def execute_account_management_payment_rules(self):
            pass


def account_rules_factory(company, type, account_type):
    return ACCOUNT_RULES_DICT[company][type][account_type]


ACCOUNT_RULES_DICT = {'kb': 
                      {"transaction": 
                       {'kbmug': KBMujUcetGold(),
                        'kbmup': KBMujUcetPlus(),
                        'kbsucg': KBStudentskyUcetG2(),
                        'kbmu': KBMujUcet(),
                        'kbuj': KBUcetJunior()
                        }, 
                        "savings":{},
                        'broker': 
                        {'kbmu': KBMujUcet()
                         }
                         }
}

class CountryRules(ABC):

    @abstractmethod
    def set_capital_gains_tax(self):
        pass

class CzechRules(CountryRules):
    PAYMENT_MONTH = 4

    def add_to_tax_base(self, month):
        if month < CzechRules.PAYMENT_MONTH:
            return 'next'
        else:
            return 'current'

    def get_income_tax_amount(self, tax_base):
        if tax_base <= 1935552:
            return 0.15 * tax_base
        else:
            return 0.15 * 1935552 + 0.23 * (tax_base - 1935552)

TAX_RULES_DICT = {'czech': CzechRules()}

def tax_rules_factory(nationality):
    return TAX_RULES_DICT[nationality]