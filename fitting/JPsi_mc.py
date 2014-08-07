import os
import inspect
from pprint import pprint

import ROOT as R
from ROOT import RooFit as RF

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
             ]
# as well as all constants
constants = []
for v in variables + constants:
    w.factory(v)

name = "Signal"
var = "x_M"
cb_one = ("CBShape:{name}{name}1({var},"
          " {name}_mean, {name}_sigma1, {name}_alphaleft,"
          " {name}_nleft)".format(name=name, var=var))
w.factory(cb_one)
cb_two = ("CBShape:{name}{name}2({var},"
          " {name}_mean, {name}_sigma2, {name}_alpharight,"
          " {name}_nright)".format(name=name, var=var))
w.factory(cb_two)

sig_pdf = w.factory("SUM:{name}{name}({name}{name}_frac[0.5,0,1]*{name}{name}1,"
                    "{name}{name}2)".format(name=name))

r = sig_pdf.fitTo(dataset, RF.Save(True),
                  RF.Minimizer("Minuit2", "Migrad"),
                  RF.NumCPU(1))

components = {"{name}{name}1".format(name=name): (RF.kSolid, R.kRed),
              "{name}{name}2".format(name=name): (RF.kDashed, R.kOrange),
              }

c = R.TCanvas()
plot1 = x_M.frame(RF.Title("x_M"),
                   RF.Name("J/Psi Mass [GeV]"))
dataset.plotOn(plot1)
sig_pdf.plotOn(plot1)
for component,(style,colour) in components.iteritems():
    sig_pdf.plotOn(plot1,
                   RF.Components(component),
                   RF.LineStyle(style),
                   RF.LineColor(colour))

plot1.Draw()
c.Update()

#utils.draw_likelihood_curves(sig_pdf, dataset, r)

var_names = [v.split("[")[0] for v in variables]
pprint([str(getattr(R.w, v)) for v in var_names])
