# -*- coding: utf-8 -*-
import os
import yaml
import inspect

from .WaporAPI import WaPOR_API_class
# from .AET_dekadal import main as AET_dekadal
# from .NPP_dekadal import main as NPP_dekadal
# from .LCC_yearly import main as LCC_yearly

# __all__ = ['AET_dekadal','NPP_dekadal','LCC_yearly']
__doc__ = """module for FAO WAPOR API"""
__version__ = '0.1'
__location__ = os.path.join(
    os.getcwd(),
    os.path.dirname(
        inspect.getfile(
            inspect.currentframe())))


file = os.path.join(__location__, 'token.yml')

# print_job = True
print_job = False
if os.path.exists(file):
    WaPOR_Token = yaml.load(open(file, 'r'), Loader=yaml.FullLoader)
else:
    # WaPOR_Token = input('Insert WAPOR API Token: ')

    file_ex = os.path.join(__location__, 'token-example.yml')
    if os.path.exists(file_ex):
        WaPOR_Token = yaml.load(open(file_ex, 'r'), Loader=yaml.FullLoader)
    else:
        raise FileNotFoundError('ERROR: "{f}" not found.'.format(f=file))

API = WaPOR_API_class(APIToken=WaPOR_Token, print_job=print_job)
