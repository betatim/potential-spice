import os
import inspect
from pprint import pprint

import ROOT as R
from ROOT import RooFit as RF
R.RooRandom.randomGenerator().SetSeed(54321)

import shapes
import utils
utils.pimp_my_roofit()


local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

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

f_input = R.TFile(local_dir + "/JPsi_data_sub.root")
tree = f_input.subTree
dataset = R.RooDataSet("SignalDataSet",
                       "SignalDataSet",
                       tree,
                       w.set("dataset_args"),
                       "1")
w_import(dataset)

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

pdf = w.factory("SUM:total(Nsig*Signal, Ncombi*Background)")

r = pdf.fitTo(dataset,
              RF.Save(True),
              RF.Minimizer("Minuit2", "Migrad"),
              RF.NumCPU(1),
              #RF.Offset(True)
              )

components = {"Signal": (RF.kSolid, R.kRed),
              "Background": (RF.kDashed, R.kOrange),
              }
utils.plot_inv_mass(pdf,
                    dataset,
                    x_M,
                    components,
                    "MCDataFit-")
