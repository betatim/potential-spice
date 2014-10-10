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
utils.pimp_my_roofit()


R.gInterpreter.GenerateDictionary("std::pair<std::string, RooDataSet*>", "map;string;RooDataSet.h")
R.gInterpreter.GenerateDictionary("std::map<std::string, RooDataSet*>", "map;string;RooDataSet.h")
m = R.std.map('string, RooDataSet*')()

local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

R.RooAbsArg.__str__ = utils.print_var
R.RooRealVar.__str__ = utils.print_var

rc = R.RooCategory("rc","rc")


w = R.RooWorkspace("w", True)
w_import = getattr(w, "import")

# Invariant mass, pT and rapidity
w.factory("x_M[%f,%f]"%(x_M_LL, x_M_UL))
x_M = w.var("x_M")
w.factory("x_Y[%f,%f]"%(x_Y_LL, x_Y_UL))
x_Y = w.var("x_Y")
w.factory("x_PT[%f,%f]"%(x_PT_LL, x_PT_UL))
x_PT = w.var("x_PT")

w.defineSet("dataset_args",
            ",".join(x.GetName() for x in [x_M, x_Y, x_PT]))

f_input = R.TFile(local_dir + "/JPsi_data_sub.root")
tree = f_input.subTree


#Here starts some multibin magic
#m - is a map between category name and statset (category - data from bin)
m.keepalive = list()
#ds - arrray of datasets, one dataset for each bin
ds = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
#sample - array of category names 
sample = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
#pdf - array of pdfs for each sample
pdf = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
sig_pdf = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
bg_pdf = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
Sig_Yields = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
Sig_Yields_err = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
Bgr_Yields = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
Bgr_Yields_err = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 

cut = utils.define_cuts(nBins_Y, nBins_PT, x_Y, x_PT)
sample = utils.define_samples(nBins_Y, nBins_PT)

for i, j in product(range(nBins_Y), range(nBins_PT)):

    #Here we create a map of sample-dataset
    rc.defineType(sample[i][j])
    # data set to insert
    ds[i][j] = R.RooDataSet("SignalDataSet", "SignalDataSet", tree, w.set("dataset_args"), cut[i][j])
    ds[i][j].Print()
    # make sure a reference count is kept
    m.keepalive.append(ds[i][j])
    # actual insertion into the map, 
    m.insert(m.begin(), R.std.pair('string, RooDataSet*')(sample[i][j], ds[i][j]))

    #Here we define pdf for selected sample
    variables = ['Signal'+sample[i][j]+'_mean[3.09,2.990,3.210]',
                 "Background"+sample[i][j]+"_tau[-0.001,-0.5,0.5]", 
                 "Nsig"+sample[i][j]+"[1000,0,5000]",
                 "Ncombi"+sample[i][j]+"[100,0,4000]",
                 ]
    # as well as constants
    #If you want to have every bin its own individual variables - you can add them later
    constants = [#'Signal_mean[3.097545]',
                 'Signal'+sample[i][j]+'_sigma1[0.011866]',
                 'Signal'+sample[i][j]+'_alphaleft[1.822779]',
                 'Signal'+sample[i][j]+'_nleft[2.586874]',
                 'Signal'+sample[i][j]+'_sigma2[0.004062]',
                 'Signal'+sample[i][j]+'_alpharight[-0.405625]',
                 'Signal'+sample[i][j]+'_nright[4.394696]',
                 'Signal'+sample[i][j]+'_frac[0.856264]'
                 ]
    for v in variables + constants:
        w.factory(v)

    sig_pdf[i][j] = shapes.signal(w, name = "Signal"+sample[i][j])
    bg_pdf[i][j] = shapes.background(w, name = "Background"+sample[i][j])

    #To fit all bins with the same fit
    #pdf[i][j] = w.factory("SUM:total(Nsig"+sample[i][j]+"*Signal, Ncombi"+sample[i][j]+"*Background)")
    #Individual pdf for each bin
    pdf[i][j] = w.factory("SUM:total"+sample[i][j]+"(Nsig"+sample[i][j]+"*Signal"+sample[i][j]+", Ncombi"+sample[i][j]+"*Background"+sample[i][j]+")")

#Here we define combined dataset
dataset = R.RooDataSet("SignalDataSet",\
                        "SignalDataSet",\
                        w.set("dataset_args"),\
                        RF.Index(rc),\
                        RF.Import(m))



#Here we define simultaneous PDF
sim_pdf = R.RooSimultaneous("sim_pdf","simultaneous pdf",rc) ;

for i, j in product(range(nBins_Y), range(nBins_PT)):
    sim_pdf.addPdf(pdf[i][j], sample[i][j])


w_import(dataset)
w_import(rc)
w_import(sim_pdf)



r = sim_pdf.fitTo(dataset,
              RF.Save(True),
              RF.Minimizer("Minuit2", "Migrad"),
              RF.NumCPU(1),
              #RF.PrintLevel(3),
              #RF.Offset(True)
              )

for i, j in product(range(nBins_Y), range(nBins_PT)):
    Sig_Yields[i][j] = w.var("Nsig"+sample[i][j]).getVal()
    Sig_Yields_err[i][j] = w.var("Nsig"+sample[i][j]).getError()
    Bgr_Yields[i][j] = w.var("Ncombi"+sample[i][j]).getVal()
    Bgr_Yields_err[i][j] = w.var("Ncombi"+sample[i][j]).getError()

utils.create_table(Sig_Yields, Sig_Yields_err, "Signal_Yields.txt",nBins_Y, nBins_PT)

f_res = open("Fit_Result.txt", "w")
for k in range(len(r.floatParsFinal())-1):
    f_res.write(str(r.floatParsFinal()[k])+"\n")

f_res.write("\n")
f_res.write("Fit status: "+str(r.covQual())+"\n")
f_res.close()

components = {"Signal": (RF.kSolid, R.kRed),
              "Background": (RF.kDashed, R.kOrange),
              }

for i, j in product(range(nBins_Y), range(nBins_PT)):
    components = {"Signal"+sample[i][j]: (RF.kSolid, R.kRed),
              "Background"+sample[i][j]: (RF.kDashed, R.kOrange),
              }
    utils.plot_inv_mass(pdf[i][j],
                        ds[i][j],
                        x_M,
                        components,
                        "Plots/MCDataFit-"+sample[i][j])
