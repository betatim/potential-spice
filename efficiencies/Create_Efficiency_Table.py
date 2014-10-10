import os
import sys
sys.path.append('../config')
import inspect
from pprint import pprint
from itertools import product
from config import *

import ROOT as R
from ROOT import RooFit as RF
import utils
utils.pimp_my_roofit()

local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


R.RooAbsArg.__str__ = utils.print_var
R.RooRealVar.__str__ = utils.print_var


w = R.RooWorkspace("w", True)
w_import = getattr(w, "import")


w.factory("x_M[%f,%f]"%(x_M_LL, x_M_UL))
x_M = w.var("x_M")
w.factory("x_Y[%f,%f]"%(x_Y_LL, x_Y_UL))
x_Y = w.var("x_Y")
w.factory("x_PT[%f,%f]"%(x_PT_LL, x_PT_UL))
x_PT = w.var("x_PT")


f_input = R.TFile(local_dir + "/JPsi_mc_sub.root")
sel_tree = f_input.subTree
mc_tree = f_input.MCTree

sel_cut = ""

bin_cut = utils.define_cuts(nBins_Y, nBins_PT, x_Y, x_PT)
sample = utils.define_samples(nBins_Y, nBins_PT)
efficiency = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
efficiency_err = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 

for i, j in product(range(nBins_Y), range(nBins_PT)):
    cut = sel_cut + bin_cut[i][j]
    N_sel = sel_tree.GetEntries(cut)
    N_init = mc_tree.GetEntries(bin_cut[i][j])
    efficiency[i][j] = float(N_sel)/float(N_init)
    efficiency_err[i][j] = efficiency[i][j]*R.TMath.sqrt(1./N_sel+1./N_init)

utils.create_table(efficiency, efficiency_err, "Efficiency.txt",nBins_Y, nBins_PT)
