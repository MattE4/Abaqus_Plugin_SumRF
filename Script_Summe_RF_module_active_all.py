from abaqus import *
from abaqusConstants import *
from caeModules import visualization
import displayGroupOdbToolset as dgo
from numpy import concatenate
from itertools import izip
from timeit import default_timer


def SumRF_active_all(xset):
    start = default_timer()
    
    # get current viewport and odb
    vps = session.viewports.values()[0]
    odbName = vps.displayedObject.name
    odb = session.odbs[odbName]
    odbName_short = odbName.split('/')[-1]
    
    # initiate empty curve lists
    curverf1 = []
    curverf2 = []
    curverf3 = []
    curverfmag = []
    curverfmag_n = []

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
    
    # get active steps
    active_steps = []
    for i in session.odbData[odbName].activeFrames:
        active_steps.append(i[0])
    
    # find valid steps: active and nonlinear in time domain
    use_steps = []
    for i in odb.steps.keys():
        if odb.steps[i].name not in active_steps:
            print odb.steps[i].name+': Ignored. Step is inactive'
            continue
        if odb.steps[i].procedure.find('PERTURBATION') > -1:
            print odb.steps[i].name+': Perturbation steps are ignored'
            continue
        if odb.steps[i].procedure.find('MODAL') > -1:
            print odb.steps[i].name+': Perturbation steps are ignored'
            continue
        if odb.steps[i].domain <> TIME:
            print odb.steps[i].name+': Ignored. Only time domain is supported'
            continue
        if odb.steps[i].domain == TIME:
            use_steps.append(i)
    if len(use_steps) == 0:
        print 'Found no valid steps'
        return
    
    # get step time of valid steps
    step_times = []
    for i in use_steps:
        step_times.append(odb.steps[i].frames[-1].frameValue)
    
    total_times = [sum(step_times[:(i+1)]) for i,j in enumerate(step_times)]
    
    
    # loop over valid steps
    for c,s in enumerate(use_steps):
    
        #loop over frames of step   
        for f in odb.steps[s].frames:
            try:
                rforce = f.fieldOutputs['RF']
            except:
                print 'No RF data available in this frame'
                #return

            sumrf1 = sumrf2 = sumrf3 = sumrfmag = sumrfmag_n = 0
    
            # dictionary with instance indexes from BulkDataBlocks
            if f.frameId == 0:
                instdict = {}
                for j,x in enumerate(rforce.bulkDataBlocks):
                    if x.instance == None:
                        myname = 'ASSEMBLY'
                    else:
                        myname = x.instance.name
                    instdict[j] = myname
    
            # ignore first frame of later steps
            if c > 0 and f.frameId == 0:
                continue
    
            # calculate current total time
            frame_time = f.frameValue
            if c == 0:
                total_time = frame_time
            else:
                total_time = total_times[c-1] + frame_time
            
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
    
            # collect frame results into curves
            sumrfmag = sqrt(sumrf1**2+sumrf2**2+sumrf3**2)
            curverfmag.append((total_time, round(sumrfmag, 7)))
            curverfmag_n.append((total_time, round(sumrfmag_n, 7)))
            curverf1.append((total_time, round(sumrf1, 7)))
            curverf2.append((total_time, round(sumrf2, 7)))
            curverf3.append((total_time, round(sumrf3, 7)))
    
    
    # generate xy data
    if len(curverf1) > 0:
        xQuantity = visualization.QuantityType(type=TIME)
        yQuantity = visualization.QuantityType(type=FORCE)
        session.XYData(name='Sum-RF1', data=curverf1, sourceDescription='from SumRF-Plugin for '+str(odbName_short), 
            axis1QuantityType=xQuantity, axis2QuantityType=yQuantity, )
        session.XYData(name='Sum-RF2', data=curverf2, sourceDescription='from SumRF-Plugin for '+str(odbName_short), 
            axis1QuantityType=xQuantity, axis2QuantityType=yQuantity, )
        session.XYData(name='Sum-RF3', data=curverf3, sourceDescription='from SumRF-Plugin for '+str(odbName_short), 
            axis1QuantityType=xQuantity, axis2QuantityType=yQuantity, )
        session.XYData(name='RF-Mag from sums', data=curverfmag, sourceDescription='from SumRF-Plugin for '+str(odbName_short), 
            axis1QuantityType=xQuantity, axis2QuantityType=yQuantity, )
        session.XYData(name='RF-Mag', data=curverfmag_n, sourceDescription='from SumRF-Plugin for '+str(odbName_short), 
            axis1QuantityType=xQuantity, axis2QuantityType=yQuantity, )        
        print '\nGenerated xy data. See XY Data Manager.'
    else:
        print '\nNo xy data were generated. Check previous warnings or errors.'
    
    stop = default_timer()
    print '\nRuntime [s]: ', stop - start
    print '\n'
    
    
#############################################################

if __name__ == '__main__':
    
    SumRF_active_all()