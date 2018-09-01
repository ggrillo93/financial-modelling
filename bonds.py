import numpy as np
import pandas as pd
from moneyed import Money
from moneyed.localization import format_money
import scipy.optimize as op
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

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

def schedule(Ptot0, tau0, tsh, rsh, tlong, rlong, tfees, D0, rinc, incper, nper, peryr):
    """ Returns the debt evolution per period after number of periods nper starting with an initial balance D0,
        initial payment Ptot0, and annual interest rate r0. Ptot0 increases after a number of periods incper by a rate rinc.
        tfees are the trustee fees paid each year. The number of periods per year is peryr. """

    Ptot, I, Di, Df = np.zeros([4, nper])
    Di[0] = D0
    r0 = (tau0 - tsh)*(rlong - rsh)/(tlong - tsh) + rsh
    I[0] = np.around(D0*r0/peryr,2)
    Ptot[0] = np.around(Ptot0,2)
    tf = np.around(tfees/peryr, 2)*np.ones(nper)
    Df[0] = D0 + I[0] - Ptot[0] + tf[0]
    for i in range(1, nper):
        Di[i] = Df[i-1]
        I[i] = np.around(Di[i]*r0/peryr,2)
        pos = Di[i] + I[i] + tf[i]
        if i%incper == 0:
            Ptot[i] = np.around(Ptot[i-1]*(1 + rinc), 2)
        else:
            Ptot[i] = Ptot[i-1]
        Df[i] = pos - Ptot[i]
    Pp = Ptot - I
    periods = np.arange(1, nper + 1)
    tauav = np.dot(Pp, periods)/(D0*peryr)
    print(tauav)
    values = np.array([Di, I, Pp, tf, Ptot, Df])
    tab = pd.DataFrame(convtomoney(values.T), index = periods, columns = ['Initial balance', 'Interest paid', 'Principal paid', 'Trustee fees',
                                                                              'Total paid', 'Final Balance'])
    tab.columns.names = ['Period']
    return tab

def backschedule(Ptot0, tau0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball):

    Ptot, I, Di, Df = np.zeros([4, nper])
    r0 = intrate(tau0, tsh, rsh, tlong, rlong, spread, peryr)
    Ptot[-1] = np.around((1 + rinc)**(np.floor(nper/incper) - 1)*np.around(Ptot0,2),2)
    tf = np.around(tfees/peryr, 2)*np.ones(nper)
    Df[-1] = Dball
    Di[-1] = np.around((Ptot[-1] + Dball - tf[0])/(1 + r0/peryr),2)
    I[-1] = np.around(Di[-1]*r0/peryr, 2)
    for i in np.flipud(range(nper - 1)):
        if (i+1)%incper == 0:
            Ptot[i] = np.around(Ptot[i+1]/(1+rinc), 2)
        else:
            Ptot[i] = Ptot[i+1]
        Df[i] = Di[i+1]
        Di[i] = np.around((Df[i] + Ptot[i] - tf[i])/(1 + r0/peryr), 2)
        I[i] = np.around(Di[i]*r0/peryr, 2)
    Pp = Ptot - I - tf
    periods = np.linspace(1, nper, nper).astype(int)
    tauarr = Pp*periods/peryr
    D0 = Di[0]
    tauav = np.sum(tauarr)/(D0*peryr)
    values = np.array([Di, I, Pp, tf, Ptot, Df, tauarr])
    tab = pd.DataFrame(convtomoney(values.T), index = periods, columns = ['Initial balance', 'Interest paid', 'Principal paid', 'Trustee fees',
                                                                              'Total paid', 'Final Balance', 'Pp*period'])
    tab.columns.names = ['Period']
    return tab

def proceeds(tau0, Ptot0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball):
    r0 = intrate(tau0, tsh, rsh, tlong, rlong, spread, peryr)
    Ptot = np.around((1 + rinc)**(np.floor(nper/incper) - 1)*np.around(Ptot0,2),2)
    tf = np.around(tfees/peryr, 2)
    Df = Dball
    Di = np.around((Ptot + Dball - tf)/(1 + r0/peryr),2)
    I = np.around(Di*r0/peryr, 2)
    tauav = nper*(Ptot - I)
    for i in np.flipud(range(nper - 1)):
        if (i+1)%incper == 0:
            Ptot = np.around(Ptot/(1+rinc), 2)
        Df = Di
        Di = np.around((Df + Ptot - tf)/(1 + r0/peryr), 2)
        I = np.around(Di*r0/peryr, 2)
        Pp = Ptot - I - tf
        tauav = tauav + Pp*(i + 1)
    Di = np.around(Di, 2)
    tauav = tauav/(Di*peryr)
    return np.array([Di, tauav - tau0])

def findtau(Ptot0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball):

    def f1(tau0):
        r = proceeds(tau0, Ptot0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball)[1]
        return r

    root = op.brentq(f1, 0.25*nper/peryr, nper/peryr)

    return root

def findPtot0(D0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball):

    def f1(Ptot0):
        Ptot0 = np.around(Ptot0, 2)
        tau0 = findtau(Ptot0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball)
        r = proceeds(tau0, Ptot0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball)[0] - D0
        return r

    r00 = intrate(nper/peryr, tsh, rsh, tlong, rlong, spread, peryr)
    a = -np.pmt(r00/peryr, nper, D0, fv = Dball)/2.
    b = a*4
    root = op.brentq(f1, a, b)
    return root

def buildschedule(D0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball):
    Ptot0 = findPtot0(D0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball)
    tau0 = findtau(Ptot0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball)
    r0 = intrate(tau0, tsh, rsh, tlong, rlong, spread, peryr)*100
    print["Average life = " + str(np.around(tau0, 2)) + ' years', "Interest rate = " + str(r0) + '%']
    return backschedule(Ptot0, tau0, tsh, rsh, tlong, rlong, spread, tfees, rinc, incper, nper, peryr, Dball)

def intrate(tau0, tsh, rsh, tlong, rlong, spread, peryr):
    tsh, tlong = tsh*12, tlong*12
    r0 = (tau0*peryr - tsh)*(rlong - rsh)/(tlong - tsh) + rsh + spread/100.
    return np.around(peryr*(((1. + r0/2.)**(2./peryr))-1.), 4)

def partable():
    parameter = ['Shorter Treasury Yield', 'Shorter Treasury Term (Years)', 'Longer Treasury Yield', 'Longer Treasury Term (Years)', 'Spread of CTL (bps)',
            'Notes issued', 'Annual Trustee Fees', 'Lease % Step-Up', 'Step-Up Period', 'Lease Term (Periods)', 'Balloon Dollar Amount', 'Periods per Year']
    values = [" "]*len(parameter)
    intab = pd.DataFrame(np.array([parameter, values]).T, columns = ['Parameter', 'Value'])
    return intab

def plotDf(tfees, D0, r0, rinc, incper, nper, peryr, Dball, margin = 0.5):

    def thousands(x, pos):
        return '$%1.1f' % (x*1e-4)

    formatter = FuncFormatter(thousands)

    Ptot00 = -np.pmt(r0/peryr, nper, D0, fv = Dball)
    Ptot0vec = np.linspace(margin*Ptot00, Ptot00*(1+margin), 1000)
    fig, ax = plt.subplots(figsize = (10, 5), dpi = 100)
    ax.yaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_formatter(formatter)
    Df = [(debtmis(Ptot0, tfees, D0, r0, rinc, incper, nper, peryr, Dball) + Dball) for Ptot0 in Ptot0vec]
    ax.plot(Ptot0vec, Df)
    ax.set_title('Final debt vs Initial Payment')
    ax.set_xlabel(r'$P_{tot}^0$')
    ax.set_ylabel(r'$D_f$')
    ax.axhline(y = Dball, ls = 'dashed', color = 'black')
    ax.grid()
    plt.show()
    return
