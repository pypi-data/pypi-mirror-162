"""
This is a test file for functions
"""
from src import conversion as C

dpath = "QiuDan_3.ebf"
# col_list = ['px', 'py', 'pz', 'vx', 'vy', 'vz', 'feh', 'alpha', 'smass', 'age', \
#             'rad', 'mag0', 'mag1', 'mag2', 'popid', 'satid', 'fieldid', 'partid', \
#             'lum', 'teff', 'grav', 'mact', 'mtip', 'dcmc_i', 'dcmc_j', \
#             'dcmc_h', 'dcmc_ks', 'exbv_schlegel', 'exbv_solar', 'exbv_schlegel_inf', 'glon', 'glat']
C.ebf_to_fits(dpath,output_columelist=None)

import src.constants as C
print(C.U_sun)