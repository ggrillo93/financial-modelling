from utilfuncs import *
import pandas as pd

def rentcf(fyrrent, rentinc, incperiod, nperiods):
    """ Returns the cash flow for the rent of a single property.
    Inputs: fyrrent = First year rent
            rentinc = Percentage rent increase per period
            incperiod = Rent increase period (in years)
            nperiods = Number of cashflow periods (in months) """

    # TO DO: - Add months for forward rent

    rent = np.zeros(nperiods)
    for i in range(1, nperiods - 1):
        rent[i] = fyrrent*(1 + rentinc)**np.floor((i - 1)/(12.*incperiod))/12.
    return rent

def buysell(nperiods, pprice, sprice, ecost, acost):
    """ Returns the cash flow for buying/selling a single property.
    Inputs: nperiods = Number of cashflow periods (in months)
            pprice = Property purchase price
            sprice = Propertly selling price
            ecosts = Exit costs (as fraction of selling price)
            acosts = Acquisition costs (as fraction of  purchase price) """

    # TO DO: Add selling at close

    prop = np.zeros(nperiods)
    prop[0] = -pprice*(1 + acost)
    prop[-1] = sprice*(1 - ecost)
    return prop

def loancf(nperiods, debt0, lfee, repprem, totamort):
    """ Returns the initial inflow and final outflow of the loan.
    Inputs: nperiods = number of cashflow periods (in months)
            debt0 = starting loan/debt
            lfee = Loan fee (as fraction of loan)
            totamort = sum of amortization payments made (negative)
            repprem = repayment premium """

    # TO DO: -

    cf = np.zeros(nperiods)
    cf[0] = debt0*(1 - lfee)
    cf[-1] = -(debt0*repprem + totamort)
    print(debt0*repprem)
    return cf

def debtcf(nperiods, debt0, aintrate, aperiod):
    """ Returns the cashflow related to the debt repayment of the loan and the evolution of the debt balance as a function of time
    Inputs: nperiods = number of cashflow periods (in months)
            debt0 = starting loan/debt
            aintrate = amortization interest rate
            aperiod = amortization period in months """

    D = np.zeros(nperiods) # Debt balance
    A0 = np.pmt(aintrate, aperiod, debt0) # Base amortization payment per period
    D[1] = debt0 # D[0] = 0 because no debt balance at month 0
    for i in range(2, nperiods):
        D[i] = (D[i-1] - A0)/(1 - aintrate)
    A = np.zeros(nperiods)
    for i in range(1, nperiods):
        A[i] = A0 - D[i]*aintrate # could be A = A0 + D*aintrate too
    return [-A, D]

def interestcf(D, r0, dates, libor):
    """ Returns the cashflow related to the loan payments from a single property.
    Inputs: D = evolution of debt balance as a function of time
            r0 = annual fixed interest rate of loan
            dates = date range of cashflow
            libor = monthly libor curve  """

    # TO DO: - Add loan term

    nperiods = len(dates)
    interest = np.zeros(nperiods)
    for i in range(1, nperiods):
        dt = (dates[i] - dates[i-1]).days
        interest[i] = D[i]*dt*(r0 + libor[i])/360.
    return -interest
