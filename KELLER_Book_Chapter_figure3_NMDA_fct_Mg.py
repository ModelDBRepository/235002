
import roadrunner, time
from roadrunner import *
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pylab
import os
import sys
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter

mpl.rcParams.update({'font.size': 10})

#======================================================================
# SIMULATION PARAMETERS
#======================================================================

model = 'NMDA8_v6_2L3.xml'

Mg = 0   # to vary from 0 to 0.200 (unit is microm)

# SIMULATION OPTIONS
ptsPerMs = 50    # Nb of points saved per ms. 5 is enough for most simulations. 400 necessary for glutamate concentration profile
simDuration = 300  # Simulation duration
sim_stiffSolver = True  # Simulation solver
sim_varTimeStep = True  # Simulation at var. time step
plotRawResults = True #Plot raw results in subplots (right after simulation)
saveResultsToFile = True #Save results to file

baseLine = 0#50e-6
pulseValue = 8e-3 # 0.008 mM = 8 microM
begPulse = 20#60e3
endPulse =  21#50e3+begPulse # 22 min = 20 x 60 = 1200e3 + 120e3
endSim = 300#3e6


def simulate(Mg):
    '''SIMULATION ROUTINE'''
    loadingTime = time.time()
    # This is the line that loads the model
    r = RoadRunner(model)
    loadTimeEnd = time.time() - loadingTime
    print 'model loaded with loading time: ' , loadTimeEnd
    # modify the distance
    r.model["Mg"]= Mg + 0.000001     # Add 1 nM to avoid convergence errors
    print '... for Mg = ' , r.model["Mg"] , ' mM'


    # record time
    s = time.time()
    # DEFINE RESULTS TO BE STORED/DISPLAYED
    resSelected = ['Vm', 'I']

    # SPECIFY SIMULATION PARAMETERS
    try:
        r.selections = ['time'] + resSelected
    except RuntimeError:
#        print "VARIABLES AVAILABLE:"
#        print "==================="
#        variousScripts.printModelParameters.printModelParameters(model)
#        #printModelParameters.printModelParameters(model)
        print "ERROR: One or more results selected does not exist. Double check results selected. ", sys.exc_info()[0]
        exit(0)

    # SIMULATE
    #    t = r.simulate(o)
    r.model["Glu"] = baseLine
    t = r.simulate(0, begPulse, 200)
    
    
    print " t = " , t
    r.model["Glu"] = pulseValue
    print '... Glu = ', r.model["Glu"]
    
    t = np.vstack ((t, r.simulate(begPulse, endPulse, 1000)))
    
    r.model["Glu"] = baseLine
    print '... Glu = ', r.model["Glu"]
    t = np.vstack ((t, r.simulate(endPulse, endSim, 10000)))

    total_time = time.time() - s
    print "\nSimulation lasted ", total_time , 'sec.'

    #PLOTS
    if plotRawResults:
        # Interactive mode ON
        plt.ion()
        f, axarr = plt.subplots(len(resSelected), sharex=True)
        for i in xrange(len(resSelected)):
            axarr[i].plot(t[:,0], t[:,i+1])
            axarr[i].set_title(resSelected[i])
        plt.draw()
        # Interactive mode OFF
        plt.ioff()
        #resize and save raw data
        figure = plt.gcf()
        figure.set_size_inches(11,8)
        plt.savefig('rawResults_'+str(Mg)+'microM.pdf', dpi=300)

        plt.close()

    #TO SAVE FILE IN TXT (IN ROWS)
    #Save all results
    for i in xrange(len(resSelected)):
        formatted_Mg = "{:0>3d}".format(int(Mg*1000))
        np.savetxt(resSelected[i]+'_'+ formatted_Mg +'mM.txt',np.vstack( (t[:,0], t[:,i+1]) ).T )
        
        list_of_I_files.append(('I_'+ formatted_Mg +'mM.txt' , 'I_'+ formatted_Mg +'mM'))


def plot3dResults (datalist, title):
    ''' PLOT ALL PROFILES IN 3D '''

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    verts = []
    dist = list()
    currentDistance=2000
    for data, label in datalist:
        verts.append(list(zip(data[:,0], -data[:,1])))
        dist.append(currentDistance)
        currentDistance = currentDistance - 100

    poly = PolyCollection(verts, facecolors = [cc('r'), cc('g'), cc('b'),
                                           cc('y')])
    poly.set_alpha(0.4)
    ax.add_collection3d(poly, zs=dist, zdir='y')

    ax.set_xlabel('Time (ms)')
    ax.set_xlim3d(0, 300)
    ax.set_ylabel('[Mg] (microM)')
    ax.set_ylim3d(-1, 2000)
    ax.set_zlabel( title)
    ax.set_zlim3d(0, 0.12)

    plt.draw()
    # Interactive mode OFF
    plt.ioff()
    plt.savefig(title+'_all_Mg_concentrations.pdf', dpi=300)
    print "NEW FILE: " + title+'_all_Mg_concentrations.pdf saved to disk'


#================================================================================
#MAIN
#================================================================================
#Create empty list
list_of_I_files = list()

#initialize color converter
cc = lambda arg: colorConverter.to_rgba(arg, alpha=0.6)

#  LOOP ON THE DISTANCE
for i in range(0, 11):
    # increment distance
    Mg_concentration = 0.02 * i
    # simulate
    simulate(Mg_concentration)

# Gather data from the list of files
datalist = [ ( pylab.loadtxt(filename), label ) for filename, label in list_of_I_files ]
# ... and plot
plot3dResults(datalist, 'NMDA-R Current (pA)')


print "SIMULATIONS FINISHED. CHECK RESULTS ON CURRENT ACTIVE DIRECTORY"

