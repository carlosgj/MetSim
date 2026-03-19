import logging
import os
import numpy as np
from matplotlib import pyplot as plt
from Glass import parseAGF, getGlassFromCatalog

def calcdOPLdT(glass, l0, wl=1.550):
    if glass.refTemp is None:
        return None
    n0 = glass.getN(wl, 20.)
    if n0 is None:
        return None
    OPL0 = n0*l0
    dT = 1.
    n = glass.getN(wl, 20+dT)
    cte = glass.TCEn30to70
    if cte == 0:
        cte = glass.TCE100to300
    if cte == 0:
        print(f"No CTE for {glass.name}")
        return None
    dl = dT * cte * 1.e-6 * l0
    l = l0 + dl
    OPL = n * l
    OPD = OPL - OPL0
    return OPD


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('matplotlib.font_manager').disabled=True
    logging.getLogger('PIL.PngImagePlugin').disabled=True

    database = []
    schott = parseAGF('./data/Zemax/schott.agf', logLevel=logging.WARNING)
    database.extend(schott)

    corning = parseAGF('./data/Zemax/corning.agf', logLevel=logging.WARNING)
    database.extend(corning)

    ohara = parseAGF('./data/Zemax/ohara.agf', logLevel=logging.WARNING)
    database.extend(ohara)

    bk7 = getGlassFromCatalog(database, 'BK7G18')
    k5 = getGlassFromCatalog(database, 'K5G20')

    lims = (1e-3, 6e-3)

    space = np.zeros((50, 50), dtype='double')

    for i, lbk7 in enumerate(np.linspace(lims[0], lims[1], num=50)):
        for j, lk5 in enumerate(np.linspace(lims[0], lims[1], num=50)):
            opdbk7 = calcdOPLdT(bk7, lbk7, wl=1.550)
            opdk5 = calcdOPLdT(k5, lk5, wl=1.550)
            combined = opdbk7 + opdk5
            space[i][j] = combined
            print(lbk7, lk5, opdbk7, opdk5)

    #plt.imshow(space, origin='lower', extent=(lims[0], lims[1], lims[0], lims[1]))
    #plt.show()
    #assert False

    #l0 = 3.e-3
    #n0 = bk7.getN(1.550, 20)
    #OPL0 = n0*l0
    #T = np.linspace(10, 30, num=100)
    #dT = T-20
    #n = bk7.getN(1.550, T)
    #dl = dT * bk7.TCEn30to70 * 1.e-6 * l0
    #l = l0 + dl

    #OPLdndt = n*l0
    #OPLcte = n0*l
    #OPLboth = n * l
    #plt.plot(T, OPLdndt-OPL0, label="dndT Only")
    #plt.plot(T, OPLcte-OPL0, label="CTE Only")
    #plt.plot(T, OPLboth-OPL0, label="Both")
    #plt.legend()

    for g in database:
        n = g.getN(1.550, 20)
        #n1 = g.getN(1.550, 21)
        #dndt = n1-n
        #cte = g.TCEn30to70

        tempco = calcdOPLdT(g, 3e-3)
        if tempco is None:
            continue
        if g.catalog == 'schott':
            plt.plot(n, tempco, 'bo')
        elif g.catalog == 'corning':
            plt.plot(n, tempco, 'ro')
        elif g.catalog == 'ohara':
            plt.plot(n, tempco, 'go')
        else:
            continue
        plt.text(n, tempco, g.name)

    plt.xlabel('Index of Refraction')
    plt.ylabel('Temp Coefficient (m/C)')

    plt.show()
