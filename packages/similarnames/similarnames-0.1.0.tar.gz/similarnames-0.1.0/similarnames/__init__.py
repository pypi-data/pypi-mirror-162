__version__ = '0.1.0'

from .similarnames import SimilarNames

def closeMatches(obj, names, method = 'explode', sep = ','):
    sn = SimilarNames()
    return sn.closeMatches(obj, names, method, sep)