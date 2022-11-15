# Do not edit this file or it may not load correctly
# if you try to open it with the RSG Dialog Builder.

# Note: thisDir is defined by the Activator class when
#       this file gets executed

from rsg.rsgGui import *
from abaqusConstants import *
from abaqusGui import *

###########################################################
vps = session.viewports.values()[0]
odbName = vps.displayedObject.name
odb = session.odbs[odbName]
#odbName_short = odbName.split('/')[-1]

nsets = odb.rootAssembly.nodeSets.keys()
insts = odb.rootAssembly.instances.keys()

if insts > 0:
    for i in insts:
        insets = odb.rootAssembly.instances[i].nodeSets.keys()
        if insets > 0:
            for n in insets:
                inset_name = str(i)+'.'+str(n)
                nsets.append(inset_name)


if len(nsets)<1:
    defaultnset = ''
else:
    defaultnset = nsets[0]
###########################################################

execDir = os.path.split(thisDir)[1]
dialogBox = RsgDialog(title='Sum RF', kernelModule='Script_Summe_RF_v10', kernelFunction='doit', includeApplyBtn=True, includeSeparator=True, okBtnText='OK', applyBtnText='Apply', execDir=execDir)
RsgHorizontalFrame(name='HFrame_2', p='DialogBox', layout='0', pl=250, pr=0, pt=0, pb=0)
RsgGroupBox(name='GroupBox_1', p='DialogBox', text='Frame(s)', layout='LAYOUT_FILL_X')
RsgRadioButton(p='GroupBox_1', text='Current', keyword='kw_frame', default=True)
RsgRadioButton(p='GroupBox_1', text='All from general steps', keyword='kw_frame', default=False)
RsgGroupBox(name='GroupBox_2', p='DialogBox', text='Region', layout='LAYOUT_FILL_X')
RsgRadioButton(p='GroupBox_2', text='All active (non-hidden) nodes', keyword='kw_region', default=True)
#RsgHorizontalFrame(name='HFrame_1', p='GroupBox_2', layout='0', pl=0, pr=0, pt=0, pb=0)
#RsgRadioButton(p='HFrame_1', text='Selected', keyword='kw_region', default=False)
#RsgPickButton(p='HFrame_1', text='Pick', keyword='kw_picked', prompt='Pick nodes', entitiesToPick='ODB_ALL|NODES', numberToPick='MANY')
RsgRadioButton(p='GroupBox_2', text='Node Set', keyword='kw_region', default=False)
#RsgComboBox(name='ComboBox_1', p='GroupBox_2', text='Node set:', keyword='kw_nodeset', default='', comboType='STANDARD', repository='', rootText='', rootKeyword=None, layout='')

RsgComboBox(name='ComboBox_1', p='GroupBox_2', text='Node set:', keyword='kw_nodeset', default=defaultnset, comboType='STANDARD', repository='', rootText='', rootKeyword=None, layout='')
for x in nsets:
    RsgListItem(p='ComboBox_1', text=x)

dialogBox.show()