import numpy as np
import scipy.optimize as op
from moneyed.localization import format_money
from moneyed import Money

def xnpv(rate, cash, time):
    """ Calculates the net present value of a sequence of (possibly) unevenly spaced cashflows.
        rate = interest/discount rate
        cash = sequence of cashflows
        time = array of times at which the cashflows occur (in days) starting at t0 = 0 """

    pvlist = cash/(1 + rate)**time
    return np.sum(pvlist)

def xirr(dates, cf):
    """ Calculates the internal rate of return for (possibly) unevenly spaced cash flows. Equivalent to the Excel function.
        Inputs: dates = array of dates at which the flows are calculated in Datetime format
                cf = array of respective cashflows """

    t0 = dates[0]
    t = np.array([(dates[i] - t0).days/365. for i in range(len(dates))])
    irr = op.newton(xnpv, 0.1, args = (cf, t))
    return irr

def convtomoney(arr):
    """ Converts array of floats/integers into an array of formatted money objects. """
    monarr = []
    for amount in arr:
        monarr.append(format_money(Money(amount = str(amount), currency = 'USD'), locale = 'en_US'))
    return monarr
