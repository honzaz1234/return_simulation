from abc import ABC, abstractmethod


class AccountRulesCreator(ABC):


    def execute_add_money_rules(self, amount):
        return True
        
        
    def execute_take_out_money_rules(self, amount):
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
                        "savings":{}}}