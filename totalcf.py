from itemizedcf import *

def singlepropcf(sdate, bcap, scap, emonth, fyrrent, rentinc, ltv, lfee, intrate, incperiod, acost, ecost, fyroexp, oexpinc, aperiod):
    """ Returns the relevant cashflows for a single property.
        Inputs: sdate = Date of purchase
                bcap = Buy cap rate
                scap = Sell cap rate
                emonth = Exit month
                fyrrent = First year rent
                ltv = LTV
                lfee = Loan fee
                intrate = Interest rate
                incperiod =  Rent increase period
                rentinc = Percentage rent increase per period
                acost = Acquisition cost (as fraction of purchase price)
                ecost = Exit cost (as fraction of sell price)
                fyroexp = First year operating expenses
                oexpinc = Percentage increase in annual operating expenses
                aperiod = Amortization period
                """

    nperiods = emonth + 1

    # Dates
    dates = pd.date_range(sdate, periods = nperiods, freq = 'M')

    pprice = fyrrent/bcap # Purchase price

    # Rent cash flow
    rent = rentcf(fyrrent, rentinc, incperiod, nperiods)

    sprice = rent[-1]*12/scap # Sell price

    # Property buy/sell cashflow
    prop = buysell(nperiods, pprice, sprice, ecost, acost)

    # Debt cashflow
    debt0 = ltv*pprice
    debt = debtcf(nperiods, debt0, lfee)

    # Operating expenses cash flow
    oexpenses = rentcf(fyroexp, oexpinc, 1, nperiods) # same formula as rent

    # Interest cash flow
    amort = amortcf(debt0, intrate, dates, aperiod)

    return [dates, rent, prop, debt, amort, oexpenses, rent + prop + debt + amort + oexpenses]

def portcf(sdate, pmonths, bcaps, scaps, emonths, fyrrents, rentincs, ltvs, lfee, intrate, incperiods, acosts, ecosts, fyropexps, oexpincs, aperiods):
    """ Returns the cashflow per month for a portfolio of properties.
    Inputs: sdate = date at which first property is acquired
            pmonths = list/array containing the months from sdate at which each of the properties is acquired
            bcaps = list/array with the buying cap rates for each of the properties
            scaps = list/array with the selling cap rates for each of the properties
            emonths = list/array with the exit months for each of the properties
            fyrrents = list/array with the first year rents for each of the properties
            rentincs = list/array with the percentage rent increase per period for each of the properties
            ltvs = list/array with the leverage for each of the properties
            lfee = loan fee as a percentage of the initial loan
            intrate = annual interest rate of the loan
            incperiods = list/array with the rent increase period for each of the properties
            acosts = list/array with the acquisition costs for each of the properties as a fraction of the sale price
            ecosts = list/array with the exit costs for each of the properties as a fraction of the sale price
            fyropexp = list/array with the first year operating expenses for each of the properties
            oexpincs = list/array with the percentage annual increase of the operating expenses
            aperiods = amortization periods for each of the properties """

    nprop = len(bcaps)
    totperiods = np.max(emonths) + 1
    alldates = pd.date_range(sdate, periods = totperiods, freq = 'M')
    allcf = np.zeros([nprop + 1, totperiods])

    for i in range(nprop):
        cf = singlepropcf(alldates[pmonths[i]], bcaps[i], scaps[i], emonths[i] - pmonths[i], fyrrents[i], rentincs[i], ltvs[i], lfee/nprop, intrate, incperiods[i], ecosts[i])[-1]
        periods = len(cf)
        if periods != totperiods:
            cf = np.pad(cf, ((pmonths[i], totperiods - emonths[i] - 1)), 'constant')
        allcf[i] = cf

    allcf[-1] = np.sum(allcf, axis = 0)

    return [alldates, allcf]
