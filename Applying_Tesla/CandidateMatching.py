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


f_input = R.TFile(local_dir + "/TutorialTuple.root","update")
tree_Tesla = f_input.TeslaTuple
tree_Stripping = f_input.StrippingTuple
tree_MC = f_input.MCTeslaTuple


t_Tesla = tree_Tesla.Get("DecayTree")
t_Stripping = tree_Stripping.Get("DecayTree")
t_MC = tree_MC.Get("MCDecayTree")

t_events = []
detailed_events = []
common_events = []
verified = []

#Difference in components of a momentum. MeV
diff = 200

for s in t_Stripping:
    if [s.runNumber, s.eventNumber] not in t_events:
        t_events.append([s.runNumber, s.eventNumber])
    detailed_events.append({'ID':[s.runNumber, s.eventNumber], 'muplus':[s.muplus_PX,s.muplus_PY,s.muplus_PZ],'muminus':[s.muminus_PX,s.muminus_PY,s.muminus_PZ]})
for s in t_Tesla:
    if [s.runNumber, s.eventNumber] in t_events:
        print "checking "+str(s.runNumber)+"  "+str(s.eventNumber)
        muplus_check = 0
        muminus_check = 0
        for d in detailed_events:
            if d['ID']== [s.runNumber, s.eventNumber]:
                if (s.muplus_PX-d['muplus'][0])**2+ (s.muplus_PY-d['muplus'][1])**2+(s.muplus_PZ-d['muplus'][2])**2<diff**2:
                    muplus_check=1
                if (s.muminus_PX-d['muminus'][0])**2+ (s.muminus_PY-d['muminus'][1])**2+(s.muminus_PZ-d['muminus'][2])**2<diff**2:
                    muminus_check=1
                if (muplus_check==1) and (muminus_check==1):
                    #verified.append({'ID':[s.runNumber, s.eventNumber],"muplus_check":muplus_check,"muminus_check":muminus_check})
                    verified.append([s.runNumber, s.eventNumber])
                    continue
                muplus_check == 0
                muminus_check == 0

print 'Filling nTuple'
verified = n.zeros(1, dtype=float)
br = t_Tesla.Branch('verified', verified, 'verified/D')

for t in t_Tesla:
    print "Filling event " + str(t.runNumber) + "  " + str(t.eventNumber)
    if [t.runNumber, t.eventNumber] in verified:
        verified[0] = 1
    else:
        verified[0] = 1
    br.Fill()


#TTree *T = new TTree(...)
#TFile *f = new TFile(...)


f_input.Write()
f_input.Close()
