from utilfuncs import *
import pandas as pd

def rentcf(fyrrent, rentinc, incperiod, nperiods):
    """ Returns the cash flow for the rent of a single property.
    Inputs: fyrrent = First year rent
            rentinc = Percentage rent increase per period
            incperiod = Rent increase period
            nperiods = Number of periods the property is owned (in months) """

    # TO DO: - Add months for forward rent

    rent = np.zeros(nperiods)
    for i in range(1, nperiods):
        rent[i] = fyrrent*(1 + rentinc)**np.floor((i - 1)/(12.*incperiod))/12.
    return rent

def buysell(nperiods, pprice, sprice, ecost, acost):
    """ Returns the cash flow for buying/selling a single property.
    Inputs: nperiods = Number of periods the property is owned (in months)
            pprice = Property purchase price
            sprice = Propertly selling price
            ecosts = Exit costs (as fraction of selling price)
            acosts = Acquisition costs (as fraction of  purchase price) """

    # TO DO: Add selling at close

    prop = np.zeros(nperiods)
    prop[0] = -pprice*(1 - acost)
    prop[-1] = sprice*(1 - ecost)
    return prop

def debtcf(nperiods, debt0, lfee):
    """ Returns the cash flow related to the debt/loan incurred to buy a single property.
    Inputs: debt0 = starting loan/debt
            pprice = Property purchase price
            lfee = Loan fee (as fraction of loan) """

    # TO DO: - Add repayment premium/principal pay upon sale

    cf = np.zeros(nperiods)
    cf[0] = debt0*(1 - lfee)
    cf[-1] = -debt0
    return cf

def amortcf(debt0, intrate, dates, aperiod):
    """ Returns the cashflow related to the interest payments from a single property.
    Inputs: debt0 = starting/principal debt/loan
            intrate = annual interest rate
            dates = date range the property is owned """

    # TO DO: - Add floating interest rates based on Libor curve
    #        - Add loan term

    nperiods = len(dates)
    amort = np.zeros(nperiods)
    if aperiod == None:
        for i in range(1, nperiods):
            amort[i] = -debt0*intrate*(dates[i] - dates[i-1]).days/360.
    else:
        for i in range(1, nperiods):
            amort[i] = intrate*debt0/(1 - (1./(1 + intrate))**aperiod)/12.
    return amort
