from itemizedcf import *
from IPython.display import display

def singlepropcf(sdate, bcap, scap, emonth, fyrrent, rentinc, incperiod, ltv, lfee, r0, libor, acost, ecost, fyroexp, oexpinc, aperiod, aintrate, repprem, expdate):
    """ Returns the relevant cashflows for a single property.
        Inputs: sdate = Date of purchase
                bcap = Buy cap rate
                scap = Sell cap rate
                emonth = Exit month
                fyrrent = First year rent
                ltv = LTV
                lfee = Loan fee
                r0 = Base interest rate
                incperiod =  Rent increase period
                rentinc = Percentage rent increase per period
                libor = LIBOR curve
                acost = Acquisition cost (as fraction of purchase price)
                ecost = Exit cost (as fraction of sell price)
                fyroexp = First year operating expenses
                oexpinc = Percentage increase in annual operating expenses
                aperiod = Amortization period
                aintrate = Amortization interest rate
                repprem = repayment premium
                """

    nperiods = emonth + 1

    # Dates
    dates = pd.date_range(sdate, periods = nperiods, freq = 'M')

    pprice = fyrrent/bcap # Purchase price

    # Rent cash flow
    rent = rentcf(fyrrent, rentinc, incperiod, dates, expdate.month)

    sprice = rent[-2]*12/scap # Sell price

    # Property buy/sell cashflow
    prop = buysell(nperiods, pprice, sprice, ecost, acost)

    # Debt evolution and amortization cashflow
    debt0 = ltv*pprice
    amort, debt = debtcf(nperiods, aintrate, debt0, r0, aperiod)

    # Operating expenses cash flow
    oexpenses = -rentcf(fyroexp, oexpinc, 1, nperiods) # same formula as rent

    # Loan cashflow
    loan = loancf(nperiods, debt0, lfee, repprem, np.sum(amort))

    # Interest cash flow
    interest = interestcf(debt, r0, dates, libor)

    return [dates, loan, prop, rent, oexpenses, interest, amort, debt, rent + prop + amort + oexpenses + loan + interest]

def portcf(names, sdate, bcaps, scaps, emonths, fyrrents, rentincs, incperiods, fyrincs, ltvs, lfee, r0, libor, acosts, ecosts, fyroexps, oexpincs, aperiod, aintrate, repprem, expdates, show = True):
    """ Returns the cashflow per month for a portfolio of properties.
    Inputs: sdate = date of first cashflow from portfolio
            bcaps = list/array with the buying cap rates for each of the properties
            scaps = list/array with the selling cap rates for each of the properties
            emonths = list/array with the exit months for each of the properties
            fyrrents = list/array with the first year rents for each of the properties
            rentincs = list/array with the percentage rent increase per period for each of the properties
            fyrinc = number of years after acquisition for first rent increase
            ltvs = list/array with the leverage for each of the properties
            lfee = loan fee as a percentage of the initial loan
            r0 = fixed annual interest rate of the loan
            libor = LIBOR curve for floating interest rate
            incperiods = list/array with the rent increase period for each of the properties
            acosts = list/array with the acquisition costs for each of the properties as a fraction of the sale price
            ecosts = list/array with the exit costs for each of the properties as a fraction of the sale price
            fyropexp = list/array with the first year operating expenses for each of the properties
            oexpincs = list/array with the percentage annual increase of the operating expenses
            aperiod = loan amortization period
            aintrate = amortization interest rate
            repprem = repayment premium
            expdates = lease expiration dates for each of the properties """

    nprop = len(bcaps)
    totperiods = np.max(emonths) + 1
    alldates = pd.date_range(sdate, periods = totperiods, freq = 'M')
    propcf = np.zeros([nprop, totperiods])
    loanpay = np.zeros(totperiods)
    P0 = fyrrents/bcaps # Purchase price per property
    alD0 = P0*ltvs
    D0 = np.sum(alD0) # Initial loan amount
    A0 = np.pmt(aintrate, aperiod, D0)
    D = np.zeros(totperiods)
    D[1] = D0
    for i in range(1, totperiods-1):
        D[i + 1] = D[i]*(1 - aintrate) - A0 # debt evolution only taking into account amortization
    A = A0 - D*aintrate
    for i in range(nprop):
        emonth = emonths[i]
        nperiods = emonth + 1
        dates = alldates[:nperiods]
        rent = rentcf(fyrrents[i], fyrincs[i], rentincs[i], incperiods[i], dates, expdates[i].month)
        sprice = rent[-1]*12/scaps[i]
        # rent[-1] = 0
        prop = buysell(nperiods, P0[i], sprice, ecosts[i], acosts[i])
        oexpenses = -rentcf(fyroexps[i], 1, oexpincs[i], 1, dates, expdates[i].month)

        # Create dataframe for single property
        spitemcf = [prop, rent, oexpenses]
        totcf = np.sum(spitemcf, axis = 0)
        if show:
            display(viewsinglecfport(names[i], dates, prop, rent, oexpenses, totcf))

        if nperiods != totperiods:
            totcf = np.pad(totcf, ((0, totperiods - nperiods)), 'constant')
        propcf[i] = totcf

    loanpay, D = portloancf(emonths, alD0, lfee, repprem, D)
    interest = interestcf(D, r0, alldates, libor)

    return [alldates, -A, propcf, interest, loanpay, D]

def viewsinglecfport(name, dates, prop, rent, oexpenses, totflow):
    """ Returns a dataframe object with the monthly stratified inflow/outflow of a single property in a portfolio.
    Inputs: dates = Dates during which the cashflow is calculated
            rent = Rent cashflow for the property
            prop = Buy/sell cashflow for the property
            oexpenses = Cashflow related to the property's operating expenses """

    monarrs = [prop, rent, oexpenses, totflow]
    row = [np.arange(len(prop)), dates.date]
    for arr in monarrs:
        row.append(convtomoney(arr)) # convert floats to money objects
    rowlabels = ['Month #', 'Dates', 'Property buy/sell', 'Rent', 'Operating expenses', 'Total cash flow']
    df = pd.DataFrame(row, index = rowlabels, columns = ['']*len(prop))
    df.columns.name = name
    return df
