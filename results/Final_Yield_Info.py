import os
import sys
sys.path.append('../config')
import inspect
from pprint import pprint
from itertools import product
from config import *

import ROOT as R
from ROOT import RooFit as RF
R.RooRandom.randomGenerator().SetSeed(54321)

import shapes
import utils

local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


efficiencies = utils.parse_table("../efficiencies/Efficiencies.txt",nBins_Y, nBins_PT)[0]
efficiencies_err = utils.parse_table("../efficiencies/Efficiencies.txt",nBins_Y, nBins_PT)[1]
yields = utils.parse_table("../fitting/Signal_Yields.txt",nBins_Y, nBins_PT)[0]
yields_err = utils.parse_table("../fitting/Signal_Yields.txt",nBins_Y, nBins_PT)[1]

yield_distr = R.TH2F("yield_distr", "Yield distribution", nBins_Y, x_Y_LL , x_Y_UL , nBins_PT, x_PT_LL , x_PT_UL )
yield_distr.GetXaxis().SetTitle("#eta")
yield_distr.GetYaxis().SetTitle("P^{T} [GeV/c]")

yield_distr_table = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
yield_distr_table_err = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 

for i, j in product(range(nBins_Y), range(nBins_PT)):
    yield_distr_table[i][j]=float(yields[i][j])/float(efficiencies[i][j])
    yield_distr_table_err[i][j] = float(yields[i][j])/float(efficiencies[i][j])*R.TMath.sqrt((float(efficiencies_err[i][j])/float(efficiencies[i][j]))**2+(float(yields_err[i][j])/float(yields[i][j]))**2)
    yield_distr.SetBinContent(i+1, j+1, yield_distr_table[i][j])
    yield_distr.SetBinError(i+1, j+1, yield_distr_table_err[i][j])


txt = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 

c = R.TCanvas()
R.gStyle.SetOptStat(0)
yield_distr.Draw("COLZ")
for i, j in product(range(nBins_Y), range(nBins_PT)):
    txt[i][j] = R.TText(yield_distr.GetXaxis().GetBinLowEdge(i+1), yield_distr.GetYaxis().GetBinCenter(j+1), "%d +/- %d"%(yield_distr.GetBinContent(i+1,j+1), yield_distr.GetBinError(i+1,j+1)))
    txt[i][j].Draw("SAME")
    c.Update()
c.SaveAs("Yield_distr.pdf")


utils.create_table(yield_distr_table, yield_distr_table_err, "Final_Yield_Distr.txt",nBins_Y, nBins_PT)
