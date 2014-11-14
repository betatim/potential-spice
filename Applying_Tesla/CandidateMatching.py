import os
import inspect
from pprint import pprint
from itertools import product
import math
import numpy as n

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
detailed_events = []
common_events = []
verified = []
list_of_differences = {}

#Difference in components of a momentum. MeV
diff = 0
verified_mup = 0
verified_mum = 0
for s in t_Stripping:
    if [s.runNumber, s.eventNumber] not in t_events:
        t_events.append([s.runNumber, s.eventNumber])
    detailed_events.append({'ID':[s.runNumber, s.eventNumber], 'muplus':[s.muplus_PX,s.muplus_PY,s.muplus_PZ],'muminus':[s.muminus_PX,s.muminus_PY,s.muminus_PZ]})
for s in t_Tesla:
    if [s.runNumber, s.eventNumber] in t_events:
        #print "checking "+str(s.runNumber)+"  "+str(s.eventNumber)
        muplus_check = 0
        muminus_check = 0
        index = 0
        for d in detailed_events:
            if d['ID']== [s.runNumber, s.eventNumber]:
                difference = (s.muplus_PX-d['muplus'][0])**2+ (s.muplus_PY-d['muplus'][1])**2+(s.muplus_PZ-d['muplus'][2])**2 + (s.muminus_PX-d['muminus'][0])**2+ (s.muminus_PY-d['muminus'][1])**2+(s.muminus_PZ-d['muminus'][2])**2
                #Find for pair for mu+ and mu-
                if (s.muplus_PX-d['muplus'][0])**2+ (s.muplus_PY-d['muplus'][1])**2+(s.muplus_PZ-d['muplus'][2])**2<=diff**2:
                    muplus_check=1
                    verified_mup +=1
                if (s.muminus_PX-d['muminus'][0])**2+ (s.muminus_PY-d['muminus'][1])**2+(s.muminus_PZ-d['muminus'][2])**2<=diff**2:
                    muminus_check=1
                    verified_mum +=1
                #Find most similar candidate
                if index == 0:
                    min_difference = difference
                index +=1
                if difference<min_difference:
                    min_difference = difference
                #Check if identical candidate found
                if (muplus_check==1) and (muminus_check==1):
                    #verified.append({'ID':[s.runNumber, s.eventNumber],"muplus_check":muplus_check,"muminus_check":muminus_check})
                    verified.append([s.runNumber, s.eventNumber])
                    continue
                muplus_check == 0
                muminus_check == 0
        list_of_differences[str(s.runNumber)+str(s.eventNumber)] = min_difference

print str(int(100*len(verified)/nEntries))+"% of Tesla candidates have stripping partner"
print str(int(100*verified_mup/nEntries))+"% of mu+ have stripping partner"
print str(int(100*verified_mum/nEntries))+"% of mu- candidates have stripping partner"



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
    if str(t.runNumber)+str(t.eventNumber) in list_of_differences:
        verified[0] = list_of_differences[str(t.runNumber)+str(t.eventNumber)]
    else:
        verified[0] = -1000
    br.Fill()


#TTree *T = new TTree(...)
#TFile *f = new TFile(...)


new_f.Write()
new_f.Close()
