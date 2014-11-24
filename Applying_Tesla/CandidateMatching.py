import os
import inspect
from pprint import pprint
from itertools import product
import math
import numpy as n
import sys

import ROOT as R
from ROOT import gStyle
gStyle.SetOptStat(False)
#from ROOT import RooFit as RF

local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


f_input = R.TFile(local_dir + "/TutorialTuple.root")
tree_Tesla = f_input.TeslaTuple
tree_Stripping = f_input.StrippingTuple

#f_input_2 = R.TFile(local_dir + "/TutorialTuple_Stripping.root")
#tree_Stripping = f_input_2.StrippingTuple

t_Tesla = tree_Tesla.Get("DecayTree")
t_Stripping = tree_Stripping.Get("DecayTree")

nEntries = t_Tesla.GetEntries() 

t_events = []
detailed_events = {}
common_events = []
verified = []
list_of_differences = {}


NumOfOverlap = 0

for i,s in enumerate(t_Stripping):
    if [s.runNumber, s.eventNumber] not in t_events:
        t_events.append([s.runNumber, s.eventNumber])
        detailed_events[str(s.runNumber)+str(s.eventNumber)]=[]
    detailed_events[str(s.runNumber)+str(s.eventNumber)].append({'muplus':[s.muplus_PX,s.muplus_PY,s.muplus_PZ],'muminus':[s.muminus_PX,s.muminus_PY,s.muminus_PZ]})
    sys.stdout.flush()
    sys.stdout.write('Stripping candidates :'+str(i+1)+'/'+ str(t_Stripping.GetEntries())+'\r')
print ""
print 'Striping candidates done'
for i, s in enumerate(t_Tesla):
    if [s.runNumber, s.eventNumber] in t_events:
        #NumOfOverlap - dummy counter
        NumOfOverlap+=1
        index = 0
        #Here can be several candidates in the same event, so we want to find the most similar Stripping candidate for each Tesla candidte
        for d in detailed_events[str(s.runNumber)+str(s.eventNumber)]:
            difference = (s.muplus_PX-d['muplus'][0])**2+ (s.muplus_PY-d['muplus'][1])**2+(s.muplus_PZ-d['muplus'][2])**2 + (s.muminus_PX-d['muminus'][0])**2+ (s.muminus_PY-d['muminus'][1])**2+(s.muminus_PZ-d['muminus'][2])**2
            if index == 0:
                min_difference = difference
            index +=1
            if difference<min_difference:
                min_difference = difference
        list_of_differences[str(s.runNumber)+str(s.eventNumber)+str(s.J_psi_1S_M)] = min_difference

    sys.stdout.flush()
    sys.stdout.write('Tesla candidates :'+str(i+1)+'/'+ str(t_Tesla.GetEntries())+'\r')

print ""
print 'Tesla candidates done'
print "Dummy matching counting:  "+str(NumOfOverlap)+" Advanced matching counting:  "+str(len(list_of_differences.keys()))



new_f = R.TFile("VerifiedTesla.root", "RECREATE")
t = t_Tesla.CloneTree(0)


for i in range(nEntries): 
    t_Tesla.GetEntry(i) 
    t.Fill() 


#print 'Filling nTuple'
verified = n.zeros(1, dtype=float)
br = t.Branch('verified', verified, 'verified/D')

for t in t:
    #print "Filling event " + str(t.runNumber) + "  " + str(t.eventNumber)
    if str(t.runNumber)+str(t.eventNumber)+str(t.J_psi_1S_M) in list_of_differences:
        verified[0] = list_of_differences[str(t.runNumber)+str(t.eventNumber)+str(t.J_psi_1S_M)]
    else:
        verified[0] = -1000
    br.Fill()

new_f.Write()
new_f.Close()
