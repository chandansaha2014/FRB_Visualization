# -*- coding: utf-8 -*-

import pandas as pd
from flask import Flask
from flask import render_template



data_path = './input/'
n_samples = 5000


app = Flask(__name__)

def current_balance(transactions,opening_balance,available_sources):
    # balance variables
    opening_checking_balance = 20000.00
    opening_cash_balance = 50000.00
    opening_fedfunds_balance = 0.00
    opening_loan_balance = 100000.00
    opening_cds_balance = 55000.00
    opening_savings_balance = 75000.00

    # sources variable
    sources_fed_funds = round(float(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['available_amount']),2)
    sources_cd1_funds = round(float(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['available_amount']),2)
    sources_cd5_funds = round(float(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['available_amount']),2)
    sources_checking_funds = round(float(available_sources.loc[available_sources['type'] == 'Checking Deposits']['available_amount']),2)
    sources_savings_funds = round(float(available_sources.loc[available_sources['type'] == 'Savings']['available_amount']),2)
    result_list = []

    # update transactions
    for index,transaction in transactions.iterrows():
        result = {}
        timestamp , Amount , Type = transaction
        result['timestamp'] = timestamp
        temp_amount = round(float(Amount.replace(',', '')), 2)
        result['Amount'] = temp_amount
        result['Type'] = Type

        if Type == "Checking":
            if temp_amount < 0 : # debit- withdraw from bank
                temp_cash_balance = opening_cash_balance + temp_amount
                if temp_cash_balance <= 20000:
                   # try to borrow from Checking fund
                    if -temp_amount < sources_checking_funds:
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Checking Deposits']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Checking Deposits']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add checking's liability
                        opening_checking_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_checking_balance += borrowing_amount
                        # update sources
                        sources_checking_funds -= borrowing_amount
                    elif -temp_amount < sources_savings_funds: # try to borrow from Saving fund
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Savings']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Savings']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add Savings's liability
                        opening_checking_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_savings_balance += borrowing_amount
                        # update sources
                        sources_savings_funds -= borrowing_amount
                    elif -temp_amount < sources_cd1_funds: # borrow from CD1 year term
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add CDs's liability
                        opening_checking_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_cds_balance += borrowing_amount
                        # update sources
                        sources_cd1_funds -= borrowing_amount
                    elif -temp_amount < sources_cd5_funds: # cds 5 years term
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add CD's liability
                        opening_checking_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_cds_balance += borrowing_amount
                        # update sources
                        sources_cd5_funds -= borrowing_amount
                    else : # borrow from fed funds
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add fed fund's liability
                        opening_checking_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_fedfunds_balance += borrowing_amount
                        # update sources
                        sources_fed_funds -= borrowing_amount
                else:
                    opening_checking_balance += temp_amount
                    opening_cash_balance += temp_amount

            else:
                opening_checking_balance += temp_amount
                opening_cash_balance += temp_amount
        elif Type == "Savings":
            if temp_amount < 0:# debit - withdraw from bank
                # reduce cash balance
                temp_cash_balance = opening_cash_balance + temp_amount
                if temp_cash_balance <= 20000:
                    # try to borrow from Checking fund
                    if -temp_amount < sources_checking_funds:
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Checking Deposits']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Checking Deposits']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add checking's liability
                        opening_savings_balance -= temp_amount # serve loan by borrowing from  fed fund

                        opening_checking_balance += borrowing_amount
                        # update sources
                        sources_checking_funds -= borrowing_amount
                    elif -temp_amount < sources_savings_funds: # try to borrow from Saving fund
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Savings']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Savings']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add Savings's liability
                        opening_savings_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_savings_balance += borrowing_amount
                        # update sources
                        sources_savings_funds -= borrowing_amount
                    elif -temp_amount < sources_cd1_funds: # borrow from CD1 year term
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add CDs's liability
                        opening_savings_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_cds_balance += borrowing_amount
                        # update sources
                        sources_cd1_funds -= borrowing_amount
                    elif -temp_amount < sources_cd5_funds: # cds 5 years term
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add CD's liability
                        opening_savings_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_cds_balance += borrowing_amount
                        # update sources
                        sources_cd5_funds -= borrowing_amount
                    else : # borrow from fed funds
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add fed fund's liability
                        opening_savings_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_fedfunds_balance += borrowing_amount
                        # update sources
                        sources_fed_funds -= borrowing_amount

                else:
                    opening_savings_balance += temp_amount # reducing savings liability
                    opening_cash_balance += temp_amount # reducing cash asset
            else: # credit = depositing money to bank - increase liability - positive
                opening_savings_balance += temp_amount
                opening_cash_balance += temp_amount
        elif Type == "CDs":
            if temp_amount < 0: # debit - withdraw from bank
                temp_cash_balance = opening_cash_balance + temp_amount
                if temp_cash_balance < 20000:
                    # try to borrow from Checking fund
                    if -temp_amount < sources_checking_funds:
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Checking Deposits']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Checking Deposits']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add checking's liability
                        opening_cds_balance -= temp_amount # serve loan by borrowing from  fed fund

                        opening_checking_balance += borrowing_amount
                        # update sources
                        sources_checking_funds -= borrowing_amount
                    elif -temp_amount < sources_savings_funds: # try to borrow from Saving fund
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Savings']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Savings']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add Savings's liability
                        opening_cds_balance -= temp_amount # serve loan by borrowing from  fed fund

                        opening_savings_balance += borrowing_amount
                        # update sources
                        sources_savings_funds -= borrowing_amount
                    elif -temp_amount < sources_cd1_funds: # borrow from CD1 year term
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add CDs's liability
                        opening_cds_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_cds_balance += borrowing_amount
                        # update sources
                        sources_cd1_funds -= borrowing_amount
                    elif -temp_amount < sources_cd5_funds: # cds 5 years term
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add CD's liability
                        opening_cds_balance -= temp_amount # serve loan by borrowing from  fed fund

                        opening_cds_balance += borrowing_amount
                        # update sources
                        sources_cd5_funds -= borrowing_amount
                    else : # borrow from fed funds
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add fed fund's liability
                        opening_cds_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_fedfunds_balance += borrowing_amount
                        # update sources
                        sources_fed_funds -= borrowing_amount

                else:
                    opening_cds_balance += temp_amount
                    opening_cash_balance += temp_amount
            else: # credit - CD deposit to bank - increase liability - positive
                opening_cds_balance += temp_amount
                opening_cash_balance += temp_amount

        elif Type == "Loan Repayment" or Type == "Loan Funding" :
            if temp_amount > 0: # Loan Payment
                temp_cash_balance = opening_cash_balance + temp_amount
                opening_cash_balance = temp_cash_balance
                opening_loan_balance -= temp_amount # reduce loan asset
                if opening_loan_balance <= 0 :
                   # try to borrow from Checking fund
                    if -temp_amount < sources_checking_funds:
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Checking Deposits']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Checking Deposits']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add checking's liability
                        opening_loan_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_checking_balance += borrowing_amount
                        # update sources
                        sources_checking_funds -= borrowing_amount
                    elif -temp_amount < sources_savings_funds: # try to borrow from Saving fund
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Savings']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Savings']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add Savings's liability
                        opening_loan_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_savings_balance += borrowing_amount
                        # update sources
                        sources_savings_funds -= borrowing_amount
                    elif -temp_amount < sources_cd1_funds: # borrow from CD1 year term
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add CDs's liability
                        opening_loan_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_cds_balance += borrowing_amount
                        # update sources
                        sources_cd1_funds -= borrowing_amount
                    elif -temp_amount < sources_cd5_funds: # cds 5 years term
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add CD's liability
                        opening_loan_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_cds_balance += borrowing_amount
                        # update sources
                        sources_cd5_funds -= borrowing_amount
                    else : # borrow from fed funds
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add fed fund's liability
                        opening_loan_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_fedfunds_balance += borrowing_amount
                        # update sources
                        sources_fed_funds -= borrowing_amount

            else: # Loan funding - negative
                if -temp_amount < opening_cash_balance - 20000 : # decrease from cash and increase loan asset
                        opening_cash_balance += temp_amount
                        opening_loan_balance -= temp_amount # increase Loan Asset
                else:
                    # try to borrow from Checking fund
                    #print(sources_checking_funds)
                    if -temp_amount < sources_checking_funds:
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Checking Deposits']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Checking Deposits']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add checking's liability
                        opening_loan_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_checking_balance += borrowing_amount
                        # update sources
                        sources_checking_funds -= borrowing_amount
                    elif -temp_amount < sources_savings_funds: # try to borrow from Saving fund
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Savings']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Savings']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add Savings's liability
                        opening_loan_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_savings_balance += borrowing_amount
                        # update sources
                        sources_savings_funds -= borrowing_amount
                    elif -temp_amount < sources_cd1_funds: # borrow from CD1 year term
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'CDs - 1 year term']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add CDs's liability
                        opening_loan_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_cds_balance += borrowing_amount
                        # update sources
                        sources_cd1_funds -= borrowing_amount
                    elif -temp_amount < sources_cd5_funds: # cds 5 years term
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'CDs - 5 year term']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add CD's liability
                        opening_loan_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_cds_balance += borrowing_amount
                        # update sources
                        sources_cd5_funds -= borrowing_amount
                    else : # borrow from fed funds
                        funding_cost = float(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['funding_cost'])
                        increment_size = int(available_sources.loc[available_sources['type'] == 'Fed Funds Line']['increment_size'])
                        units_to_borrow = int(- temp_amount / increment_size) + 1 # borrow multiple of increment size
                        borrowing_amount = int(increment_size * units_to_borrow)

                        # increase Loan Balance and add fed fund's liability
                        opening_loan_balance -= temp_amount # serve loan by borrowing from  fed fund
                        opening_fedfunds_balance += borrowing_amount
                        # update sources
                        sources_fed_funds -= borrowing_amount


        result['current_checking_balance']= round(float(opening_checking_balance),2)
        result['current_cash_balance'] = round(float(opening_cash_balance),2)
        result['current_fedfunds_balance'] = round(float(opening_fedfunds_balance),2)
        result['current_loan_balance'] = round(float(opening_loan_balance),2)
        result['current_cds_balance'] = round(float(opening_cds_balance),2)
        result['current_savings_balance'] = round(float(opening_savings_balance),2)

        # update sources
        result['sources_checking_funds'] = round(float(sources_checking_funds),2)
        result['sources_savings_funds'] = round(float(sources_savings_funds),2)
        result['sources_cd1_funds'] = round(float(sources_cd1_funds),2)
        result['sources_cd5_funds'] = round(float(sources_cd5_funds),2)
        result['sources_fed_funds'] = round(float(sources_fed_funds),2)



        result_list.append(result)
    results = pd.DataFrame(result_list)
    return results


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    transactions_df = pd.read_csv(data_path + 'RealtimeData.csv')
    opening_balance_df = pd.read_csv(data_path + 'OpeningBalance.csv')
    available_sources_df = pd.read_csv(data_path + 'AvailableSources.csv')
    cols_to_keep = ['timestamp', 'Amount', 'Type']
    # Dropping NA values
    transactions_clean = transactions_df[cols_to_keep].dropna()

    # Calculate current balance
    current_balance_df = current_balance(transactions_df, opening_balance_df , available_sources_df)

    current_balance_df.to_csv('out.csv')

    # merge results to pass to app
    result = {'current_balance': current_balance_df, 'available_source':available_sources_df}
    result_df = pd.DataFrame(result.items())

    return  result_df.to_json(orient= 'records')

if __name__ == "__main__":
    app.run(host='localhost',port=5000,debug=True) # -*- coding: utf-8 -*-

