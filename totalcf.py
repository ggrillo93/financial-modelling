from itemizedcf import *

def singlepropcf(sdate, bcap, scap, emonth, fyrrent, rentinc, incperiod, ltv, lfee, r0, libor, acost, ecost, fyroexp, oexpinc, aperiod, aintrate, repprem):
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
    rent = rentcf(fyrrent, rentinc, incperiod, nperiods)

    sprice = rent[-2]*12/scap # Sell price

    # Property buy/sell cashflow
    prop = buysell(nperiods, pprice, sprice, ecost, acost)

    # Debt evolution and amortization cashflow
    debt0 = ltv*pprice
    amort, debt = debtcf(nperiods, debt0, aintrate, aperiod)

    # Operating expenses cash flow
    oexpenses = -rentcf(fyroexp, oexpinc, 1, nperiods) # same formula as rent

    # Loan cashflow
    loan = loancf(nperiods, debt0, lfee, repprem, np.sum(amort))

    # Interest cash flow
    interest = interestcf(debt, r0, dates, libor)

    return [dates, loan, prop, rent, oexpenses, interest, amort, debt, rent + prop + amort + oexpenses + loan + interest]

def portcf(sdate, bcaps, scaps, emonths, fyrrents, rentincs, incperiods, ltvs, lfee, r0, libor, acosts, ecosts, fyroexps, oexpincs, aperiod, aintrate, repprem):
    """ Returns the cashflow per month for a portfolio of properties.
    Inputs: sdate = date of first cashflow from portfolio
            bcaps = list/array with the buying cap rates for each of the properties
            scaps = list/array with the selling cap rates for each of the properties
            emonths = list/array with the exit months for each of the properties
            fyrrents = list/array with the first year rents for each of the properties
            rentincs = list/array with the percentage rent increase per period for each of the properties
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
            repprem = repayment premium """

    nprop = len(bcaps)
    totperiods = np.max(emonths) + 1
    alldates = pd.date_range(sdate, periods = totperiods, freq = 'M')
    allcf = np.zeros([nprop, totperiods])
    P0 = fyrrents/bcaps # Purchase price per property
    D0 = np.sum(P0*ltvs) # Initial loan amount
    print(D0)
    weights = P0/D0
    A0 = np.pmt(aintrate, aperiod, D0)
    D = np.zeros(totperiods)
    D[1] = D0
    for i in range(2, totperiods):
        if D[i-1] > 0:
            D[i] = (D[i-1] - A0)/(1 - aintrate) # debt evolution only taking into account amortization
    A = A0 - D*aintrate
    for i in range(nprop):
        emonth = emonths[i]
        cf = singlepropcf(alldates[0], bcaps[i], scaps[i], emonths[i], fyrrents[i], rentincs[i], incperiods[i], ltvs[i], lfee, r0, libor, acosts[i], ecosts[i], fyroexps[i], oexpincs[i], np.inf, 0., repprem)[1:-2]
        # cf = cf0[1:-2]
        Lrp = np.abs(cf[0][-1]) # tentative loan repayment for property
        if D[emonth] < Lrp:
            cf[0][-1] = -D[emonth]
            D[emonth:] = 0
        else:
            for j in range(emonth, totperiods):
                if D[j] > Lrp:
                    D[j] = D[j] - Lrp
                else:
                    D[j] = 0
        totcf = np.sum(cf, axis = 0)
        periods = len(totcf)
        if periods != totperiods:
            totcf = np.pad(totcf, ((0, totperiods - emonths[i] - 1)), 'constant')
        allcf[i] = totcf

    zerod = np.where(D == 0)
    if len(zerod) > 2:
        A[np.where(D == 0)[2]:] = 0

    return [alldates, -A, allcf, D, np.sum(allcf, axis = 0)]
