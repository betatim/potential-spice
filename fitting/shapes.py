import ROOT as R
from ROOT import RooFit as R


def signal(workspace, name="Signal", var="x_M"):
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
    
