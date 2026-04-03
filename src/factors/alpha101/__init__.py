"""
Alpha101 Factors - WorldQuant 101 Formulaic Alphas

基于 "101 Formulaic Alphas" by Zura Kakushadze
实现来源: https://github.com/yli188/WorldQuant_alpha101_code

注意: 部分因子需要 IndNeutralize 函数(行业中性化)，这些因子未实现
"""

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

__all__ = [
    'Alpha001', 'Alpha002', 'Alpha003', 'Alpha004', 'Alpha005',
    'Alpha006', 'Alpha007', 'Alpha008', 'Alpha009', 'Alpha010',
]
