import ROOT as R
import ROOT.RooFit as RF

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
