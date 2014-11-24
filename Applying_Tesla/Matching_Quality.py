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


f_input = R.TFile(local_dir + "/VerifiedTesla.root")
#tree_Tesla = f_input.TeslaTuple
t_Tesla = f_input.Get("DecayTree")



LowerLimit = 0
UpperLimit = 1000000
nBins = 100
hist  = R.TH1F("hist","hist",nBins, LowerLimit,UpperLimit)
hist.GetXaxis().SetTitle("Matching Parameter [MeV^{2}/c^{4}]")
hist.GetYaxis().SetTitle("Matched candidates")
t_Tesla.Project("hist","verified")


pt = R.TPaveText(100000,20,900000,300);
pt.AddText(str(int(float(t_Tesla.GetEntries("verified>0"))/t_Tesla.GetEntries()*100))+"% of Tesla candidates have Stripping candidates in the same event.")
pt.AddText("Matching parameter = #Sigma_{i=x,y,z; j = #mu^{+}, #mu^{-}}(P^{i,j}_{Tesla}-P^{i,j}_{Stripping})^{2}")


c_1 = R.TCanvas("c_1","c_1",600,400)
c_1.SetLogy(True)
hist.Draw()
pt.Draw("SAME")
c_1.SaveAs("Plots/MatchingParameter_Distr.pdf")
"""
eff  = R.TH1F("eff","eff",nBins, 0,UpperLimit**0.5)
upper_edge = 0
for i in range(1, nBins+1):
    #lower_edge = upper_edge    
    lower_edge = 0
    upper_edge = UpperLimit*i**2/nBins**2
    cut = "(verified<"+str(upper_edge)+")&&(verified>"+str(lower_edge)+")"
    eff.SetBinContent(i, float(t_Tesla.GetEntries(cut))/t_Tesla.GetEntries()*100)

c_2 = R.TCanvas("c_2","c_2",600,400)
eff.Draw()
"""

eff  = R.TH1F("eff","eff",nBins, 0,UpperLimit)
eff.GetXaxis().SetTitle("Matching Parameter [MeV^{2}/c^{4}]")
eff.GetYaxis().SetTitle("Matching rate, [%]")
upper_edge = 0
for i in range(1, nBins+1):
    #lower_edge = upper_edge
    lower_edge = 0
    upper_edge = UpperLimit*i/nBins
    cut = "(verified<"+str(upper_edge)+")&&(verified>"+str(lower_edge)+")"
    eff.SetBinContent(i, float(t_Tesla.GetEntries(cut))/t_Tesla.GetEntries()*100)

c_2 = R.TCanvas("c_2","c_2",600,400)
eff.Draw()
c_2.SaveAs("Plots/MatchingParameter_Cumulative.pdf")
