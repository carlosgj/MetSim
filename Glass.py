import logging
import os

class Glass(object):
    def __init__(self, catalog, name):
        self.catalog = catalog
        self.name = name

        #NM items
        self.dispersionFormulaIdx = None
        self.Nd587 = None
        self.Vd587 = None

        #ED items
        self.TCEn30to70 = None
        self.TCE100to300 = None
        self.density = None
        self.dPgF = None
        self.ignoreTCE = None

        self.coeffs = None

        #OD items
        self.relCost = None
        self.climateRes = None
        self.stainRes = None
        self.acidRes = None
        self.alkaliRes = None
        self.phosRes = None

        self.dispersionLimits = None

        #TD items
        self.D0 = None
        self.D1 = None
        self.D2 = None
        self.E0 = None
        self.E1 = None
        self.Ltk = None
        self.refTemp = None

    def __str__(self):
        return f"<{self.catalog} {self.name}>"

def _parseNumberWithQuirks(string):
    if string == '':
        return None
    if string == '-':
        return None
    try:
        return int(string)
    except ValueError:
        return float(string)

def getGlassFromCatalog(cat, name):
    ret = None
    for glass in cat:
        if glass.name == name:
            if ret is None:
                ret = glass
            else:
                logging.warning(f'Multiple glasses called "{name}" found')
    if ret is None:
        logging.error(f"Glass {name} not found")
    return ret

def parseAGF(agfPath, logLevel=logging.DEBUG):
    logger = logging.getLogger("AGFParse")
    logger.setLevel(logLevel)
    glasses = []
    bn = os.path.basename(agfPath)
    catName = bn.split('.')[0]
    logger.info(f"Parsing catalog: {catName}")
    with open(agfPath, 'r') as fob:
        thisGlass = None
        for i, line in enumerate(fob.readlines()):
            line = line.strip()
            if line == '':
                continue
            recType = line[:2]
            lineData = line[3:]
            if recType == 'CC':
                logger.debug("Comment: "+lineData)
            elif recType == 'NM':
                #We're starting a new glass
                chunks = lineData.split(' ')
                name = chunks[0].strip()
                assert name != ''
                thisGlass = Glass(catName, name)
                glasses.append(thisGlass)
                logger.info(f"New glass: {name}")

                dispFuncNo = int(chunks[1])
                thisGlass.dispersionFunctionIndex = dispFuncNo

                #Ignore Mil #

                try:
                    Nd = float(chunks[2])
                    thisGlass.Nd587 = Nd
                except:
                    self.logger.warning(f"Could not interpret Nd '{chunks[2]}', but it's not needed")

                try:
                    Vd = float(chunks[3])
                    thisGlass.Vd587 = Vd
                except:
                    self.logger.warning(f"Could not interpret Vd '{chunks[2]}', but it's not needed")

                #Ignore exclude sub
                #Ignore status
                #Ignore melt freq

            elif recType == 'GC':
                logger.debug("Glass comment: " + lineData)

            elif recType == 'ED':
                chunks = lineData.split(' ')
                try:
                    thisGlass.TCEn30to70 = float(chunks[0])
                except:
                    logger.error("Could not parse -30 to 70 TCE")
                    print(lineData)

                if chunks[1] != '-':
                    try:
                        thisGlass.TCE100to300 = float(chunks[1])
                    except:
                        logger.warning("Could not parse 100 to 300 TCE")
                        print(lineData)

                thisGlass.density = float(chunks[2])
                thisGlass.dPgF = float(chunks[3])
                thisGlass.ignoreTCE = bool(int(chunks[4]))

            elif recType == 'CD':
                chunks = lineData.split(' ')
                coeffs = [float(x) for x in chunks]
                assert len(coeffs) <= 10
                thisGlass.coeffs = coeffs

            elif recType == 'OD':
                chunks = lineData.split(' ')
                vals = [_parseNumberWithQuirks(x) for x in chunks]
                if len(vals) < 6:
                    logger.warning(f"Only got {len(vals)} values in OD line")
                    shortfall = 6 - len(vals)
                    filler = [None] * shortfall
                    vals.extend(filler)
                thisGlass.relCost = vals[0]
                thisGlass.climateRes = vals[1]
                thisGlass.stainRes = vals[2]
                thisGlass.acidRes = vals[3]
                thisGlass.alkaliRes = vals[4]
                thisGlass.phosRes = vals[5]

            elif recType == 'LD':
                chunks = lineData.split(' ')
                limits = [float(x) for x in chunks]
                thisGlass.dispersionLimits = limits

            elif recType == 'MD':
                pass #TODO

            elif recType == 'TD':
                if lineData == '':
                    logger.warning(f"No thermal data for {name}")
                    continue
                chunks = lineData.split(' ')
                vals = [float(x) for x in chunks]
                thisGlass.D0 = vals[0]
                thisGlass.D1 = vals[1]
                thisGlass.D2 = vals[2]
                thisGlass.E0 = vals[3]
                thisGlass.E1 = vals[4]
                thisGlass.Ltk = vals[5]
                thisGlass.refTemp = vals[6]

            elif recType == 'IT':
                pass #TODO

            elif recType == 'BD':
                pass #TODO

            else:
                logger.warning(f"Unknown record type: {recType}")
                print(repr(line))

    return glasses


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    glasses = parseAGF('./data/Zemax/schott.agf', logLevel=logging.INFO)
    bk7 = getGlassFromCatalog(glasses, 'N-BK7')
    print(bk7)
