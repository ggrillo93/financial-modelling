import numpy as np
import scipy.optimize as op
from moneyed.localization import format_money
from moneyed import Money
from re import sub

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
    floatarr = np.array(arr)
    flat = floatarr.flatten()
    nelem = len(flat)
    dim = floatarr.shape
    monarr = np.zeros(nelem, dtype = object)
    for i in range(nelem):
        monarr[i] = format_money(Money(amount = str(flat[i]), currency = 'USD'), locale = 'en_US')
    return monarr.reshape(dim)

def convtofloat(arr):
    """ Converts array of money objects into array of floats. """
    monarr = np.array(arr)
    flat = monarr.flatten()
    nelem = len(flat)
    dim = monarr.shape
    floatarr = np.zeros(nelem, dtype = object)
    for i in range(nelem):
        if flat[i][0] == '-':
            floatarr[i] = -float(sub(r'[^\d.]', '', flat[i]))
        else:
            floatarr[i] = float(sub(r'[^\d.]', '', flat[i]))
    return floatarr.reshape(dim)
