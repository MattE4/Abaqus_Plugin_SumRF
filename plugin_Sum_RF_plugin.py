from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Tools ME|Sum Reaction Forces', 
    object=Activator(os.path.join(thisDir, 'plugin_Sum_RFDB.py')),
    kernelInitString='import Script_Summe_RF_v10',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    applicableModules=['Visualization'],
    version='1.0',
    author='Matthias Ernst',
    description='This Plug-in calculates the sum of reaction forces coming from many nodes. '\
                 '\nIt takes either all displayed nodes or one set. When used with displayed nodes - hide irrelevant elements/nodes to improve runtime.'\
                 '\nIt uses either only the currently displayed frame or each frame of all active general steps. '\
                 'Deactivate steps to ignore them. Individual frames are not checked regarding active/inactive.'\
                 '\n\nResults are xy-data in A/CAE or just a printout when used on a single frame. Check always notes in Message Area. '\
                 'Be aware that the xy-data are overwritten when the Plug-in is used multiple times in one session. Rename the curves in between to keep them. '\
                 'Use "Copy to ODB" in XY Data Manager to save them. '\
                 '\n\nAlternative ways to get sum of reaction forces:'\
                '\n    1. Use coupling with field and/or history output request'\
                '\n    2. Use Report > Field Output... in postprocessing'\
                '\n    3. For a small number of nodes use Create XY Data -> ODB Field Output ... -> Save and use the Sum operation'\
                 '\n\nThis Plug-In is not an official Dassault Systemes product.',
    helpUrl='N/A'
)
