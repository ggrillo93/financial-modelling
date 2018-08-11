import numpy as np
from utilfuncs import *

def returns(totflow, dates):
    """ Returns a dataframe object with the inflow, outflow, profit, MOIC, and IRR of a single property or a portfolio.
    Inputs: totflow = Time series containing the total cashflow for a single property or portfolio
            dates = Dates during which the cashflow is recorded """

    # TO DO: Add cash on cash

    # Cash inflow/outflow
    inflow = np.sum(totflow[totflow > 0])
    outflow = np.sum(totflow[totflow < 0])

    # Returns
    profit = np.sum(totflow)
    moic = -profit/outflow + 1
    irr = xirr(dates, totflow)

    return [inflow, outflow, profit, moic, irr]
