from totalcf import *
from returns import *

def viewret(inflow, outflow, profit, moic, irr):
    """ Returns dataframe object with calculated returns for a single property or a portfolio.
        Inputs: inflow = total cash inflow
                outflow = total cash outflow
                profit = inflow + outflow
                moic = Multiple On Investment Capital
                irr = Internal Rate of Return """

    monarrs = [inflow, -outflow, profit]
    resultarr = convtomoney(monarrs) + [moic, irr] # Correctly format money numbers
    resultlab = ['Inflow', 'Outflow', 'Profit', 'MOIC', 'IRR']
    results = pd.DataFrame(resultarr, index = resultlab, columns = ['Value'])
    results.columns.name = 'Returns'
    return results

def viewsinglecf(name, dates, loan, prop, rent, oexpenses, interest, amort, debt, totflow):
    """ Returns a dataframe object with the monthly stratified inflow/outflow of a single property.
    Inputs: dates = Dates during which the cashflow is calculated
            rent = Rent cashflow for the property
            prop = Buy/sell cashflow for the property
            debt = Cashflow related to the property's principal loan payments
            interest = Cashflow related to the property's interest payments """

    monarrs = [debt, loan, prop, rent, oexpenses, interest, amort, np.roll(debt, -1), totflow]
    row = [np.arange(len(debt)), dates.date]
    for arr in monarrs:
        row.append(convtomoney(arr)) # convert floats to money objects
    rowlabels = ['Month #', 'Dates', 'Starting debt', 'Loan', 'Property buy/sell', 'Rent', 'Operating expenses', 'Interest', 'Amortization', 'Final debt', 'Total cash flow']
    df = pd.DataFrame(row, index = rowlabels, columns = ['']*len(debt))
    df.columns.name = name
    return df

def viewportcf(names, alldates, amort, propcf, interest, loanpay, debt):
    """ Returns a dataframe object with the cashflow per period for the individual properties in a portfolio, as well
        as the total cashflow per period.
    Inputs: names = list/array containing the identifying name for each of the properties
            allcf = individual cashflow per period for each of the properties
            alldates = all dates at which portfolio cashflows take place """


    row = [np.arange(len(debt)), alldates.date]
    totpropcf = np.sum(propcf, axis = 0)
    totcf = totpropcf + amort + interest
    Df = debt + amort + loanpay
    Df[0] = debt[1]
    row.append(convtomoney(debt))
    row.append(convtomoney(amort))
    for arr in propcf:
        row.append(convtomoney(arr))
    row.append(convtomoney(interest))
    row.append(convtomoney(loanpay))
    row.append(convtomoney(Df))
    row.append(convtomoney(totcf))
    rowlabels = ['Month #', 'Dates', 'Starting debt', 'Amortization'] + names + ['Interest payment', 'Loan cashflow from buy/sell', 'Final debt', 'Total cash flow']
    df = pd.DataFrame(row, index = rowlabels, columns = ['']*len(debt))
    # df.columns.name = 'Month #'
    return df
