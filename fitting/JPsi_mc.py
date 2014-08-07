import os
import inspect
from pprint import pprint

import ROOT as R
from ROOT import RooFit as RF

import shapes
import utils
utils.pimp_my_roofit()


local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
R.RooRandom.randomGenerator().SetSeed(54321)

def print_var(v):
    return "%s[%f]"%(v.GetName(), v.getVal())
R.RooAbsArg.__str__ = print_var
R.RooRealVar.__str__ = print_var

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

f_input = R.TFile(local_dir + "/JPsi_mc_sub.root")
tree = f_input.subTree
dataset = R.RooDataSet("SignalDataSet",
                       "SignalDataSet",
                       tree,
                       w.set("dataset_args"),
                       "1")
w_import(dataset)

# Define all variables
variables = ["Signal_mean[2.999,2.990,3.210]",
             "Signal_sigma1[0.1,0,0.2]",
             "Signal_alphaleft[0.5,0,3]",
             "Signal_nleft[2,0,10]",
             "Signal_sigma2[0.012,0,0.2]",
             "Signal_alpharight[-0.5,-3,0]",
             "Signal_nright[2,0,10]",
             "Signal_frac[0.5,0,1]",
             ]
# as well as all constants
constants = []
for v in variables + constants:
    w.factory(v)

name = "Signal"
sig_pdf = shapes.signal(w, name)

r = sig_pdf.fitTo(dataset, RF.Save(True),
                  RF.Minimizer("Minuit2", "Migrad"),
                  RF.NumCPU(1))

components = {name+"1": (RF.kSolid, R.kRed),
              name+"2": (RF.kDashed, R.kOrange),
              }
utils.plot_inv_mass(sig_pdf, dataset,
                    x_M, components,
                    "SigOnlyFit-")

#utils.draw_likelihood_curves(sig_pdf, dataset, r)

var_names = [v.split("[")[0] for v in variables]
pprint([str(getattr(R.w, v)) for v in var_names])
