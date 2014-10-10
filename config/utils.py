import ROOT as R
import ROOT.RooFit as RF
from itertools import product
from config import *


def pimp_my_roofit():
    def argset__iter__(self):
        start = self.fwdIterator()
        for i in xrange(len(self)):
            yield start.next()
        
    def argset__len__(self):
        return self.getSize()
    R.RooArgSet.__iter__ = argset__iter__
    R.RooArgSet.__len__ = argset__len__

def plot_inv_mass(pdf, dataset, var, components, base_name="InvMass-"):
    c = R.TCanvas()
    plot1 = var.frame(RF.Title(var.GetName()),
                      RF.Name("J/Psi Mass [GeV]"))
    dataset.plotOn(plot1)
    pdf.plotOn(plot1)
    for component,(style,colour) in components.iteritems():
        pdf.plotOn(plot1,
                   RF.Components(component),
                   RF.LineStyle(style),
                   RF.LineColor(colour))

    plot1.Draw()
    c.Update()
    c.SaveAs(base_name + var.GetName() +".pdf")
    
def draw_likelihood_curves(pdf, dataset, fit_result, base_name="NLL-"):
    """Draw likelihood curve for all variables"""
    c = R.TCanvas("likelihood","")

    for n,var in enumerate(pdf.getParameters(dataset)):
        if var.isConstant():
            continue
        print var.GetName(), "now."
    
        nll = pdf.createNLL(dataset)

        fitted_var = fit_result.floatParsFinal().find(var.GetName())
        delta = 4 * fitted_var.getError()
        assert(fitted_var == var)
    
        for x_range in (None, (fitted_var.getVal()-delta, fitted_var.getVal()+delta)):
            if x_range is None:
                f = var.frame()
                nll.plotOn(f, RF.ShiftToZero())
                fname = base_name + var.GetName()
                
            else:
                low = max(var.getMin(), x_range[0])
                up = min(var.getMax(), x_range[1])
                f = var.frame(RF.Range(low, up))
            
                nll.plotOn(f, RF.ShiftToZero())
                fname = base_name + var.GetName() + "-zoomed"
        
            f.Draw()
            c.SaveAs(fname + ".pdf")
            #c.SetLogy(True)
            #c.SaveAs(fname + "-log.pdf")
            #c.SetLogy(False)
            c.Clear()

def define_cuts(nBins_Y, nBins_PT, x_Y, x_PT):
    cut = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
    for i, j in product(range(nBins_Y), range(nBins_PT)):
    #First, we define cut, which will extract data for besired bin
        cut[i][j] = "("+\
          str(x_Y.getMin()+(x_Y.getMax()-x_Y.getMin())/nBins_Y*i)+\
          "<x_Y)&&("+\
          str(x_Y.getMin()+(x_Y.getMax()-x_Y.getMin())/nBins_Y*(i+1))+\
          ">x_Y)&&("+\
          str(x_PT.getMin()+(x_PT.getMax()-x_PT.getMin())/nBins_PT*j)+\
          "<x_PT)&&("+\
          str(x_PT.getMin()+(x_PT.getMax()-x_PT.getMin())/nBins_PT*(j+1))+\
          ">x_PT)"
    return cut

def define_samples(nBins_Y, nBins_PT):
    sample = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
    for i, j in product(range(nBins_Y), range(nBins_PT)):
        sample[i][j] = "_"+str(i) + "_bin_in_Y__" + str(j) + "_bin_in_PT"
    return sample

def print_var(v):
    return "%40s   [%10s  +/-  %10s]  ||| limits: [%10s %10s]"%(v.GetName(),\
            str("%4.4f"%(v.getVal())), str("%4.4f"%(v.getError())),\
            str("%4.4f"%(v.getMin())), str("%4.4f"%(v.getMax())))

def create_table(table, table_err, name,nBins_Y, nBins_PT):
    f_eff = open(name, "w")
    for i in range(nBins_Y):
        for j in range(nBins_PT):
             f_eff.write("  %10s  +/-  %10s  |"%(str("%4.8f"%(table[i][j])),str("%4.8f"%(table_err[i][j]))))
             #print "  %10s  +/-  %10s  |"%(str("%4.8f"%(table[i][j])),str("%4.8f"%(table_err[i][j]))),
        f_eff.write("\n")
        #print "\n",
    f_eff.close()

def print_table(table, nBins_Y, nBins_PT):
    for i in range(nBins_Y):
        for j in range(nBins_PT):
             print "  %10s  |"%(str("%4.8f"%(table[i][j]))),
        print "\n",

def parse_table(name,nBins_Y, nBins_PT):
    line = open(name).readlines()
    table = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
    table_err = [[0 for x in xrange(nBins_Y)] for x in xrange(nBins_PT)] 
    for i in range(nBins_Y):
        for j in range(nBins_PT):
            table[i][j] = float(line[i].split("|")[j].split("+/-")[0])
            table_err[i][j] = float(line[i].split("|")[j].split("+/-")[1])
    return [table, table_err]