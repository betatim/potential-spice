import ROOT as R
from ROOT import RooFit as R


def signal(workspace, name="Signal",
            shared=None, unique="", var="x_M"):
    """Double Crystal Ball pdf for the signal"""
    if shared is None:
        shared = []

    def _build_params(names):
        params = []
        for p in names:
            if p in shared:
                s = "{name}_{p}"
            
            else:
                s = "{name}{unique}_{p}"
            
            params.append(s.format(name=name,
                                   var=var,
                                   unique=unique,
                                   p=p))
        return ", ".join(params)

    
    params = _build_params(("mean", "sigma1", "alphaleft", "nleft"))
    cb_one = ("CBShape:{name}{unique}1({var},{par})".format(name=name,
                                                    var=var,
                                                    par=params,
                                                    unique=unique))
    params = _build_params(("mean", "sigma2", "alpharight", "nright"))
    cb_two = ("CBShape:{name}{unique}2({var},{par})".format(name=name,
                                                    var=var,
                                                    par=params,
                                                    unique=unique))
    workspace.factory(cb_one)
    workspace.factory(cb_two)
    return workspace.factory("SUM:{name}{unique}({name}{unique}_frac*{name}{unique}1,"
                             "{name}{unique}2)".format(name=name,
                                                       unique=unique))
    
def signal_(workspace, name="Signal", var="x_M"):
    """Double Crystal Ball pdf for the signal"""
    cb_one = ("CBShape:{name}1({var},"
              " {name}_mean, {name}_sigma1, {name}_alphaleft,"
              " {name}_nleft)".format(name=name, var=var))
    workspace.factory(cb_one)
    cb_two = ("CBShape:{name}2({var},"
              " {name}_mean, {name}_sigma2, {name}_alpharight,"
              " {name}_nright)".format(name=name, var=var))
    workspace.factory(cb_two)

    return workspace.factory("SUM:{name}({name}_frac*{name}1,"
                             "{name}2)".format(name=name))

def background(workspace, name="Background", var="x_M"):
    """Exponential shape as background component"""
    exp = "Exponential:{name}({var}, {name}_tau)".format(name=name, var=var)
    return workspace.factory(exp)
    
