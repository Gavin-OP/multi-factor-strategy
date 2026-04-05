"""
Alpha101 Factors - WorldQuant 101 Formulaic Alphas

基于 "101 Formulaic Alphas" by Zura Kakushadze
实现来源: https://github.com/yli188/WorldQuant_alpha101_code

注意: 部分因子需要 IndNeutralize 函数(行业中性化)，这些因子未实现
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


class Alpha101Factor(Factor):
    """Alpha101 因子基类"""
    category = "alpha101"
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]


from .alpha_001 import Alpha001
from .alpha_002 import Alpha002
from .alpha_003 import Alpha003
from .alpha_004 import Alpha004
from .alpha_005 import Alpha005
from .alpha_006 import Alpha006
from .alpha_007 import Alpha007
from .alpha_008 import Alpha008
from .alpha_009 import Alpha009
from .alpha_010 import Alpha010
from .alpha_011 import Alpha011
from .alpha_012 import Alpha012
from .alpha_013 import Alpha013
from .alpha_014 import Alpha014
from .alpha_015 import Alpha015
from .alpha_016 import Alpha016
from .alpha_017 import Alpha017
from .alpha_018 import Alpha018
from .alpha_019 import Alpha019
from .alpha_020 import Alpha020
from .alpha_021 import Alpha021
from .alpha_022 import Alpha022
from .alpha_023 import Alpha023
from .alpha_024 import Alpha024
from .alpha_025 import Alpha025
from .alpha_026 import Alpha026
from .alpha_027 import Alpha027
from .alpha_028 import Alpha028
from .alpha_029 import Alpha029
from .alpha_030 import Alpha030
from .alpha_031 import Alpha031
from .alpha_032 import Alpha032
from .alpha_033 import Alpha033
from .alpha_034 import Alpha034
from .alpha_035 import Alpha035
from .alpha_036 import Alpha036
from .alpha_037 import Alpha037
from .alpha_038 import Alpha038
from .alpha_039 import Alpha039
from .alpha_040 import Alpha040
from .alpha_041 import Alpha041
from .alpha_042 import Alpha042
from .alpha_043 import Alpha043
from .alpha_044 import Alpha044
from .alpha_045 import Alpha045
from .alpha_046 import Alpha046
from .alpha_047 import Alpha047
from .alpha_049 import Alpha049
from .alpha_050 import Alpha050
from .alpha_051 import Alpha051
from .alpha_052 import Alpha052
from .alpha_053 import Alpha053
from .alpha_054 import Alpha054
from .alpha_055 import Alpha055
from .alpha_057 import Alpha057
from .alpha_060 import Alpha060
from .alpha_061 import Alpha061
from .alpha_062 import Alpha062
from .alpha_064 import Alpha064
from .alpha_065 import Alpha065
from .alpha_066 import Alpha066
from .alpha_068 import Alpha068
from .alpha_071 import Alpha071
from .alpha_072 import Alpha072
from .alpha_073 import Alpha073
from .alpha_074 import Alpha074
from .alpha_075 import Alpha075
from .alpha_076 import Alpha076
from .alpha_077 import Alpha077
from .alpha_078 import Alpha078
from .alpha_081 import Alpha081
from .alpha_083 import Alpha083
from .alpha_084 import Alpha084
from .alpha_085 import Alpha085
from .alpha_086 import Alpha086
from .alpha_088 import Alpha088
from .alpha_092 import Alpha092
from .alpha_094 import Alpha094
from .alpha_095 import Alpha095
from .alpha_096 import Alpha096
from .alpha_098 import Alpha098
from .alpha_101 import Alpha101


__all__ = [
    'Alpha001',
    'Alpha002',
    'Alpha003',
    'Alpha004',
    'Alpha005',
    'Alpha006',
    'Alpha007',
    'Alpha008',
    'Alpha009',
    'Alpha010',
    'Alpha011',
    'Alpha012',
    'Alpha013',
    'Alpha014',
    'Alpha015',
    'Alpha016',
    'Alpha017',
    'Alpha018',
    'Alpha019',
    'Alpha020',
    'Alpha021',
    'Alpha022',
    'Alpha023',
    'Alpha024',
    'Alpha025',
    'Alpha026',
    'Alpha027',
    'Alpha028',
    'Alpha029',
    'Alpha030',
    'Alpha031',
    'Alpha032',
    'Alpha033',
    'Alpha034',
    'Alpha035',
    'Alpha036',
    'Alpha037',
    'Alpha038',
    'Alpha039',
    'Alpha040',
    'Alpha041',
    'Alpha042',
    'Alpha043',
    'Alpha044',
    'Alpha045',
    'Alpha046',
    'Alpha047',
    'Alpha049',
    'Alpha050',
    'Alpha051',
    'Alpha052',
    'Alpha053',
    'Alpha054',
    'Alpha055',
    'Alpha057',
    'Alpha060',
    'Alpha061',
    'Alpha062',
    'Alpha064',
    'Alpha065',
    'Alpha066',
    'Alpha068',
    'Alpha071',
    'Alpha072',
    'Alpha073',
    'Alpha074',
    'Alpha075',
    'Alpha076',
    'Alpha077',
    'Alpha078',
    'Alpha081',
    'Alpha083',
    'Alpha084',
    'Alpha085',
    'Alpha086',
    'Alpha088',
    'Alpha092',
    'Alpha094',
    'Alpha095',
    'Alpha096',
    'Alpha098',
    'Alpha101',
]
