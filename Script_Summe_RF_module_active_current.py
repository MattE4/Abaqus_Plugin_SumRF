from abaqus import *
from abaqusConstants import *
from caeModules import visualization
import displayGroupOdbToolset as dgo
from numpy import concatenate
from itertools import izip
from timeit import default_timer


def SumRF_active_current(xset):
    start = default_timer()

    # get current viewport and odb
    vps = session.viewports.values()[0]
    odbName = vps.displayedObject.name
    odb = session.odbs[odbName]
    odbName_short = odbName.split('/')[-1]

    # get current step and frame
    current_step_number = vps.odbDisplay.fieldFrame[0]
    current_step_name = odb.steps.keys()[current_step_number]
    current_frame_number = vps.odbDisplay.fieldFrame[1]
    current_frame = odb.steps[current_step_name].frames[current_frame_number]
    current_steptime = odb.steps[current_step_name].frames[current_frame_number].frameValue
    

    # display only set when set was used
    if xset != None:
        leaf = dgo.LeafFromNodeSets(nodeSets=(xset, ))
        vps.odbDisplay.displayGroup.replace(leaf=leaf)
    
    # query nodes in viewport
    nodelist=vps.getActiveNodeLabels()

    # show initial regions again
    if xset != None:
        vps.odbDisplay.displayGroup.undoLast()
        print '\nInfo: Sound may have appeared, since node set was shortly displayed at contour plot mode. Ignore it.'

    
    print '\n*********************************************'
    print 'Odb name: ', odbName_short
    if xset != None:
        print 'Node set name: ', xset

    # get number of active nodes
    numnodes = 0
    for i in nodelist.keys():
        numnodes = numnodes + len(nodelist[i])
    if numnodes == 0:
        print 'Error: No active nodes'
        return
    else:
        print 'Number of active nodes: ', numnodes
    

    f = current_frame
    try:
        rforce = f.fieldOutputs['RF']
    except:
        print 'No RF data available in this frame'
        return

    sumrf1 = sumrf2 = sumrf3 = sumrfmag = sumrfmag_n = 0

    instdict = {}
    for j,x in enumerate(rforce.bulkDataBlocks):
        if x.instance == None:
            myname = 'ASSEMBLY'
        else:
            myname = x.instance.name
        instdict[j] = myname

    # loop over instances with active nodes
    for inst in nodelist.keys():

        # get bulkDataBlock indices for current instance
        list_indexes = []
        for r,y in enumerate(instdict.values()):
            if y == inst:
                list_indexes.append(instdict.keys()[r])
        
        # combine data of multiple bulkDataBlocks
        for r,y in enumerate(list_indexes):
            if r == 0:
                nlabels = rforce.bulkDataBlocks[y].nodeLabels
                rfdata = rforce.bulkDataBlocks[y].data
            else:
                nlabels = concatenate((nlabels, rforce.bulkDataBlocks[y].nodeLabels))
                rfdata = concatenate((rfdata, rforce.bulkDataBlocks[y].data))
        
        # use nodelabels and rfdata to create dictionary
        # labels are the keys, rfdata the value
        zip_iterator = izip(nlabels.tolist(), rfdata.tolist())
        rfdict = dict(zip_iterator)

        # loop over displayed nodes of instance and get node data from dictionary
        for n in nodelist[inst]:
            try:
                sumrf1 = sumrf1 + rfdict[n][0]
                sumrf2 = sumrf2 + rfdict[n][1]
            except:
                print 'No RF data at node', n
            try:
                sumrf3 = sumrf3 + rfdict[n][2]
                sumrfmag_n = sumrfmag_n + sqrt(rfdict[n][0]**2 + rfdict[n][1]**2 + rfdict[n][2]**2)
            except:
                sumrfmag_n = sumrfmag_n + sqrt(rfdict[n][0]**2 + rfdict[n][1]**2)
                #print 'No RF3 data at node', n

    # calculate magnitude
    sumrfmag = sqrt(sumrf1**2+sumrf2**2+sumrf3**2)


    # Output results in Message Area of CAE/Viewer
    print '\nReaction forces for step '+current_step_name+' at step time = '+str(current_steptime)+':'
    print 'Sum RF1: ',  sumrf1
    print 'Sum RF2: ',  sumrf2
    print 'Sum RF3: ',  sumrf3
    print 'RF-Mag from sums: ', sumrfmag
    print 'RF-Mag: ', sumrfmag_n


    stop = default_timer()
    print '\nRuntime [s]: ', stop - start
    print '\n'


#############################################################

if __name__ == '__main__':
    
    SumRF_active_current()