#from abaqus import *
#from abaqusConstants import *
#from caeModules import visualization

from Script_Summe_RF_module_active_all import *
from Script_Summe_RF_module_active_current import *


def doit(
kw_frame=None,
kw_region=None,
kw_nodeset=None):
    
    #print '\n++++++++++++'
    #print kw_frame
    #print kw_region
    #print kw_nodeset

    if kw_region == 'All active (non-hidden) nodes':
        kw_nodeset = None


    if kw_frame == 'Current':
        SumRF_active_current(xset=kw_nodeset)

    #elif kw_frame == 'All from general steps':
    else:
        SumRF_active_all(xset=kw_nodeset)        