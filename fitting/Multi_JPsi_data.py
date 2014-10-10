import os
import inspect
from pprint import pprint
from itertools import product

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

def print_var(v):
    return "%s[%f]"%(v.GetName(), v.getVal())
R.RooAbsArg.__str__ = print_var
R.RooRealVar.__str__ = print_var

rc = R.RooCategory("rc","rc")


w = R.RooWorkspace("w", True)
w_import = getattr(w, "import")

# Invariant mass, pT and rapidity
w.factory("x_M[2.990,3.210]")
x_M = w.var("x_M")
w.factory("x_Y[2,5]")
x_Y = w.var("x_Y")
w.factory("x_PT[0,20]")
x_PT = w.var("x_PT")

w.defineSet("dataset_args",
            ",".join(x.GetName() for x in [x_M, x_Y, x_PT]))

f_input = R.TFile(local_dir + "/JPsi_data_sub.root")
tree = f_input.subTree

# Define all variables
variables = ['Signal_mean[3.09,2.990,3.210]',
             "Background_tau[-0.001,-0.5,0.5]", 
             "Nsig[1000,0,5000]",
             "Ncombi[100,0,4000]",
             ]
# as well as constants
constants = [#'Signal_mean[3.097545]',
             'Signal_sigma1[0.011866]',
             'Signal_alphaleft[1.822779]',
             'Signal_nleft[2.586874]',
             'Signal_sigma2[0.004062]',
             'Signal_alpharight[-0.405625]',
             'Signal_nright[4.394696]',
             'Signal_frac[0.856264]'
             ]
for v in variables + constants:
    w.factory(v)

sig_pdf = shapes.signal(w)
bg_pdf = shapes.background(w)


nBins_Y = 3
nBins_PT = 3

m.keepalive = list()
ds = []
sample = []
pdf = []
k=0
for i, j in product(range(nBins_Y), range(nBins_PT)):
    
    cut = "("+\
      str(x_Y.getMin()+(x_Y.getMax()-x_Y.getMin())/nBins_Y*i)+\
      "<x_Y)&&("+\
      str(x_Y.getMin()+(x_Y.getMax()-x_Y.getMin())/nBins_Y*(i+1))+\
      ">x_Y)&&("+\
      str(x_PT.getMin()+(x_PT.getMax()-x_PT.getMin())/nBins_PT*j)+\
      "<x_PT)&&("+\
      str(x_PT.getMin()+(x_PT.getMax()-x_PT.getMin())/nBins_PT*(j+1))+\
      ">x_PT)"
    print cut

    sample.append(str(i) + "_bin_in_Y__" + str(j) + "_bin_in_PT")

    rc.defineType(sample[k])

    # data set to insert
    ds.append(R.RooDataSet("SignalDataSet", "SignalDataSet", tree, w.set("dataset_args"), cut))
    ds[k].Print()
    # make sure a reference count is kept
    
    m.keepalive.append(ds[k])
    
    # actual insertion into the map, 
    m.insert(m.begin(), R.std.pair('string, RooDataSet*')(sample[k], ds[k]))

    w.factory("Nsig"+sample[k]+"[1000,0,5000]")
    w.factory("Ncombi"+sample[k]+"[100,0,4000]")

    pdf.append(w.factory("SUM:total(Nsig"+sample[k]+"*Signal, Ncombi"+sample[k]+"*Background)"))

    k+=1

dataset = R.RooDataSet("SignalDataSet",\
                        "SignalDataSet",\
                        w.set("dataset_args"),\
                        RF.Index(rc),\
                        RF.Import(m))


w_import(dataset)
w_import(rc)

sim_pdf = R.RooSimultaneous("sim_pdf","simultaneous pdf",rc) ;

k = 0
for i, j in product(range(nBins_Y), range(nBins_PT)):
    sim_pdf.addPdf(pdf[k], sample[k])
    k+=1


w_import(sim_pdf)



r = sim_pdf.fitTo(dataset,
              RF.Save(True),
              RF.Minimizer("Minuit2", "Migrad"),
              RF.NumCPU(1),
              #RF.Offset(True)
              )

components = {"Signal": (RF.kSolid, R.kRed),
              "Background": (RF.kDashed, R.kOrange),
              }

k = 0
for i, j in product(range(nBins_Y), range(nBins_PT)):

    utils.plot_inv_mass(pdf[k],
                        ds[k],
                        x_M,
                        components,
                        "MCDataFit-"+sample[k])
    k+=1


#components = {"Signal": (RF.kSolid, R.kRed),
#              "Background": (RF.kDashed, R.kOrange),
#              }
#utils.plot_inv_mass(pdf,
#                    dataset,
#                    x_M,
#                    components,
#                    "MCDataFit-")