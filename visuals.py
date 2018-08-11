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

def viewsinglecf(dates, rent, prop, debt, amort, oexpenses):
    """ Returns a dataframe object with the monthly stratified inflow/outflow of a single property.
    Inputs: dates = Dates during which the cashflow is calculated
            rent = Rent cashflow for the property
            prop = Buy/sell cashflow for the property
            debt = Cashflow related to the property's principal loan payments
            interest = Cashflow related to the property's interest payments """

    totflow = rent + prop + amort + debt + oexpenses
    monarrs = [rent, oexpenses, prop, amort, debt, totflow]
    row = [dates.date]
    for arr in monarrs:
        row.append(convtomoney(arr)) # convert floats to money objects
    rowlabels = ['Dates', 'Rent', 'Operating expenses', 'Property buy/sell', 'Amortization', 'Debt', 'Total cash flow']
    df = pd.DataFrame(row, index = rowlabels)
    df.columns.name = 'Month #'
    return df

def viewportcf(names, allcf, alldates):
    """ Returns a dataframe object with the cashflow per period for the individual properties in a portfolio, as well
        as the total cashflow per period.
    Inputs: names = list/array containing the identifying name for each of the properties
            allcf = individual cashflow per period for each of the properties
            alldates = all dates at which portfolio cashflows take place """

    row = [alldates.date]
    for arr in allcf:
        row.append(convtomoney(arr)) # convert floats to money objects
    rowlabels = ['Dates'] + names + ['Total cash flow']
    df = pd.DataFrame(row, index = rowlabels)
    df.columns.name = 'Month #'
    return df
