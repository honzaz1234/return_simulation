import math
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class DataPlotting():

    PERSON_COLUMNS = ['person', 't', 'type', 'account_name', 'inst',  'balance']

    def __init__(self, reality, ):
        self.reality = reality
        self.index_df = pd.DataFrame()
        self.people_df = pd.DataFrame()

    def set_people_df(self):
        dc = DFCreator()
        self.people_df = dc.get_people_df(
            people_dict=self.reality.person_data)
        
    def set_index_df(self):
        dc = DFCreator()
        self.index_df = dc.create_index_df(
            ins_dict=self.reality.instrument_data,
            inst_list=self.reality.instrument_list
        )

    def plot_all_indexes_separatedly(
            self, n_cols=3, plot_width=None, plot_height=None):
        p = Plots()
        p.plot_vals_separately(df=self.index_df,
                               filter_col='name', 
                               col_x='t', 
                               col_y='price',
                               n_cols=n_cols)
        
    def plot_all_indexes_for_person_one_plot(
            self, person, plot_width=None, plot_height=None):
        df_person = self.people_df[self.people_df['person'] == person]
        sns.lineplot(data=df_person, x="t", y="balance", hue="inst")

    def plot_all_indexes_for_person_separate_plots(
            self, person, n_cols=3, plot_width=None, plot_heigth=None):
        df_person = self.people_df[self.people_df['person'] == person]
        p = Plots()
        p.plot_vals_separately(df=df_person,
                               filter_col='inst', 
                               col_x='t', 
                               col_y='balance',
                               n_cols=n_cols,
                               plot_height=plot_heigth,
                               plot_width=plot_width)

    def plot_all_indexes_for_all_people(
            self, n_cols=3, plot_width=None, plot_height=None):
        p = Plots()
        plot = p.plot_vals_separately(df=self.people_df,
                               filter_col='person', 
                               col_x='t', 
                               col_y='balance',
                               hue_col='inst',
                               n_cols=n_cols,
                               plot_height=plot_height,
                               plot_width=plot_width
                                )
        return plot

class DFCreator():

    def __init__(self):
        pass

    def get_account_df(self, account_dict):
        dict_to_df = dict()
        dict_to_df['account_balance'] = account_dict['amount']
        for inst in account_dict['instruments']:
            dict_to_df[inst] = account_dict['instruments'][inst]
        account_df = pd.DataFrame.from_dict(
            dict_to_df, 
            orient='index', 
            columns=['balance'])
        account_df.reset_index(inplace=True)
        account_df.rename(columns={'index': 'inst'}, inplace=True)
        return account_df
    
    def get_period_df(self, period_dict):
        df_period = pd.DataFrame(
            columns=DataPlotting.PERSON_COLUMNS)
        row_income = pd.DataFrame(
            {'type': ['income'], 
             'account_name': [None], 
             'inst': [None], 
             'balance': [period_dict['income']]})
        row_amount = pd.DataFrame(
            {'type': ['cash_balance'],
             'account_name': [None],
             'inst': [None],
             'balance': [period_dict['amount']]})
        df_period = pd.concat([df_period, row_income, row_amount])
        for account in period_dict['accounts']:
            account_df = self.get_account_df(
                account_dict=period_dict['accounts'][account])
            account_df['account_name'] = account
            account_df['type'] = 'acount_info'
            df_period = pd.concat([df_period, account_df])
        return df_period
    
    def get_person_df(self, person_dict):
        person_df = pd.DataFrame(
            columns=DataPlotting.PERSON_COLUMNS)
        for t in person_dict:
            period_df = self.get_period_df(period_dict=person_dict[t])
            period_df['t'] = t
            person_df = pd.concat([person_df, period_df])
        return person_df
    
    def get_people_df(self, people_dict):
        people_df = pd.DataFrame(
            columns=DataPlotting.PERSON_COLUMNS)
        for person in people_dict:
            person_df = self.get_person_df(person_dict=people_dict[person])
            person_df['person'] = person
            people_df = pd.concat([people_df, person_df])
        people_df.reset_index(inplace=True)
        return people_df
    
    def create_index_df(self, ins_dict, inst_list):
        index_list = self.get_index_list(inst_list=inst_list)
        indexes = ['t', 'name', 'price']
        indexes_df = pd.DataFrame(columns=indexes)
        for index_name in index_list:
            price_dict = ins_dict[index_name]
            index_df = pd.DataFrame(list(price_dict.items()),
                                    columns = ['t', 'price'])
            index_df['name'] = index_name
            index_df = index_df[indexes] 
            indexes_df = pd.concat([indexes_df, index_df])
        return indexes_df

    def get_index_list(self, inst_list):
        index_list = []
        for inst in inst_list:
            if inst.type == 'index':
                index_list.append(inst.name)
        return index_list
          
class Plots():


    def __init__(self):
        pass

    def plot(self, df, col_x, col_y, ax, hue_col, title=None):
        if ax is None:
            fig, ax = plt.subplot()
        plot = sns.lineplot(data=df, x=col_x, y=col_y, ax=ax, hue=hue_col)
        self.set_plot_attributes(
            ax=ax, xlabel=col_x, ylabel=col_y, title=title)
        return plot

    def set_plot_attributes(self, ax, xlabel, ylabel, title):
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    def plot_wrapper(
        self, n_rows, n_cols, axes, row_n, col_n, df, col_x, col_y, hue_col=None, title=None):
        if n_rows == 1 and n_cols == 1:
            ax_1 = axes
        elif n_rows == 1:
            ax_1 = axes[col_n]
        elif n_cols == 1:
            ax_1 = axes[row_n]
        else: 
            ax_1 = axes[row_n, col_n]
        plot = self.plot(
            df=df, col_x=col_x, col_y=col_y, ax=ax_1, hue_col=hue_col, title=title)
        return plot

    def plot_vals_separately(
            self, df, filter_col, col_x, col_y, names_list=None,  n_cols=3, hue_col=None, plot_width=8, plot_height=6):
        if names_list is None:
            names_list = df[filter_col].unique()
        if len(names_list) < n_cols:
            n_cols = len(names_list)
        n_rows = math.ceil(len(names_list) / n_cols)
        if plot_width == None:
            plot_width, plot_height = 8, 6
        fig, axes = plt.subplots(ncols=n_cols, nrows=n_rows,
                                 figsize=(plot_width, plot_height))
        col_n = -1
        for ind in range(len(names_list)):
            print(ind)
            row_n = ind // n_cols
            col_n += 1
            sub_df = df[df[filter_col] == names_list[ind]]
            print('n_rows: ' + str(n_rows))
            print('n_cols: ' + str(n_cols))
            print('col_n: ' + str(col_n))
            print('row_n: ' + str(row_n))

            plot = self.plot_wrapper(
                n_rows=n_rows, n_cols=n_cols, axes=axes, df=sub_df, col_x=col_x, col_y=col_y, row_n=row_n, col_n=col_n, hue_col=hue_col, title=names_list[ind])
            if (col_n - 1) == n_cols:
                col_n = -1
        return fig