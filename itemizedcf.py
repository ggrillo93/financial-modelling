from utilfuncs import *
import pandas as pd

def rentcf(fyrrent, fincyr, rentinc, incperiod, dates, expmonth):
    """ Returns the cash flow for the rent of a single property.
    Inputs: fyrrent = First year rent
            rentinc = Percentage rent increase per period
            incperiod = Rent increase period (in years)
            nperiods = Number of cashflow periods (in months) """

    # TO DO: - Add months for forward rent

    nperiods = len(dates)
    rent = np.zeros(nperiods)
    styear = dates[0].year + fincyr
    # print(styear)
    rent[1] = fyrrent/12.
    for i in range(1, nperiods - 1):
        if expmonth == dates[i].month +1 and (dates[i].year - styear)%incperiod == 0 and (dates[i].year - styear) >= 0:
            rent[i+1] = rent[i]*(1+rentinc)
        else:
            rent[i+1] = rent[i]
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
    return cf

def debtcf(nperiods, aintrate, debt0, r0, aperiod):
    """ Returns the cashflow related to the debt repayment of the loan and the evolution of the debt balance as a function of time
    Inputs: nperiods = number of cashflow periods (in months)
            debt0 = starting loan/debt
            aintrate = amortization interest rate
            aperiod = amortization period in months """

    D = np.zeros(nperiods) # Debt balance
    A0 = np.pmt(aintrate, aperiod, debt0) # Base amortization payment per period
    D[1] = debt0 # D[0] = 0 because no debt balance at month 0
    for i in range(2, nperiods):
        D[i] = (D[i-1] - A0)/(1 - r0)
    A = np.zeros(nperiods)
    for i in range(1, nperiods):
        A[i] = A0 - D[i]*r0 # could be A = A0 + D*aintrate too
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

def portloancf(emonths, alD0, lfee, repprem, D):
    """ Returns the cashflow related to the loan payments of a portfolio.
    Inputs: emonths = exit month of each of the portfolio's properties.
            alD0 = allocated loan amount for each of the portfolio's properties.
            lfee = loan fee as a percentage
            repprem = repayment premium
            D = amortized debt """

    totperiods = np.max(emonths) + 1
    cf = np.zeros(totperiods)
    cf[0] = D[1]*(1 - lfee)
    for i in range(totperiods):
        w = np.where(np.asarray(emonths) == i)[0]
        if len(w) != 0:
            tentcf = np.sum([repprem*alD0[j] for j in w])
            if i != totperiods - 1:
                if tentcf < D[i]:
                    D[i + 1:] = D[i] - tentcf
                    cf[i] = -tentcf
                else:
                    cf[i] = -D[i]
                    D[i + 1:] = 0
            else:
                if tentcf > D[i]:
                    cf[i] = -D[i]
                else:
                    print('Error')
    return [cf, D]
