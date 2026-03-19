import logging
import os
import numpy as np
from matplotlib import pyplot as plt
from Glass import parseAGF, getGlassFromCatalog

def calcdOPLdT(glass, l0, wl=1.550):
    if glass.refTemp is None:
        return None
    n0 = glass.getN(wl, 20.)
    OPL0 = n0*l0
    dT = 1.
    n = glass.getN(wl, 20+dT)
    dl = dT * glass.TCEn30to70 * 1.e-6 * l0
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

    rh = parseAGF('./data/Zemax/rad_hard.agf', logLevel=logging.WARNING)
    database.extend(rh)

    rh = [g.name for g in rh]
    print(rh)

    for g in database:
        n = g.getN(1.550, 20)
        n1 = g.getN(1.550, 21)
        if n is None or n1 is None:
            print(f"Skipping {g.name}")
            continue
        dndt = n1-n
        cte = g.TCEn30to70
        if cte == 0:
            cte = g.TCE100to300
        if cte == 0:
            print(f"{g.name} CTE is zero. Probably untrustworthy.")
            continue

        #if g.name not in rh:
        #    continue

        if g.catalog == 'schott':
            pass
            plt.plot(dndt, cte, 'bo')
        elif g.catalog == 'corning':
            plt.plot(dndt, cte, 'ro')
            #plt.text(dndt, cte, g.name)
        elif g.catalog == 'ohara':
            plt.plot(dndt, cte, 'go')
        else:
            continue
        plt.text(dndt, cte, g.name)

    plt.show()
