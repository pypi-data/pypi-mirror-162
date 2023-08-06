"""
This is the file including calculators for different quantities

"""
def get_extinction(l,b,d,bayestar=None):
    """
    The input should be
    :param l: galactic longitude in degree
    :param b: galactic latitude in degree
    :param d: distance in kpc
    :return: the extinction E(B-V)
    """
    from astropy.coordinates import SkyCoord
    if bayestar == None:
        from dustmaps.bayestar import BayestarQuery
        bayestar = BayestarQuery(version='bayestar2019')
    import astropy.units as units
    coords = SkyCoord(l*units.deg, b*units.deg, distance=d*units.kpc, frame="galactic")
    return bayestar(coords, mode='median')

def DM_to_Distance(DM=1):
    """
    convert the distance module to distance in kpc
    :param DM: distance module
    :return: distance in kpc
    """
    return 10**(DM/5)/100

def Distance_to_DM(Dist=10):
    """
    convert distance to distance module
    :param Dist: distance in kpc
    :return: distance module
    """
    import numpy as np
    return 5*np.log10(Dist*100)


