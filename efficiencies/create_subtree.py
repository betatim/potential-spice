# SetupProject LHCb v37r3
import random
import re
import os
import inspect

import ROOT as R


local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# Variables listed here are copied to the sub-ntuple
# allows you to rename them, or compute new variables
# via TTreeFormulas, but you have to give them a new
# name in that case
fit_variables = [("x_M", "X_M/1000"), # convert to GeV
                 ("x_PT", "X_PT/1000"), # convert to GeV
                 ("x_Y", "X_Y"),
                 ("x_TZ", "X_TZ"),
                 ("RAND", random.random),
                 ]
datasets = {"JPsi_data": {'in_file': local_dir + "/../data/JPsi_data_ntuple.root",
                          'out_file': local_dir + "/JPsi_data_sub.root",
                          'cuts': "1",
                          'rename': fit_variables,
                          },
            "JPsi_mc": {'in_file': local_dir + "/../data/JPsi_mc_ntuple.root",
                        'out_file': local_dir + "/JPsi_mc_sub.root",
                        'cuts': "1",
                        'rename': fit_variables,
                        },
            }


def extract_names(branches):
    re1 = '((?:[a-z][a-z0-9_]*))'
    rg = re.compile(re1, re.IGNORECASE|re.DOTALL)
    for find in rg.findall(branches):
        if find != "abs":
            yield find

def enable_branches(tree, branch_names, exclusive=True):
    if exclusive:
        tree.SetBranchStatus("*", 0)

    for branch_name in branch_names:
        tree.SetBranchStatus(branch_name, 1)

def create_tree(ds):
    config = datasets[ds]

    print "Using dataset %s with cuts: %s"%(ds, config['cuts'])

    # One seed for every data set
    random.seed(ds)

    inFile = R.TFile(config['in_file'], "READ")

    tmpFile = R.TFile("/tmp/tmp-asdasdasdq-omgapony.root", "RECREATE")
    tmpFile.cd() # needed for big ntuples
    
    inTree = inFile.Get("Early2015/DecayTree")
    inTree.Write()

    n_before = inTree.GetEntries()

    # Enable branches needed to evaluate if an event passes
    # the initial cuts as well as those needed by the
    # calculation of the final branches
    enable_branches(inTree, extract_names(config['cuts']))
    for _,old in config['rename']:
        if isinstance(old, str):
            enable_branches(inTree, extract_names(old), exclusive=False)

    print "Applying initial cuts"
    tree = inTree.CopyTree(config['cuts'])
    tree.Write()

    total = tree.GetEntries()
    print total, "candidates after inital cuts"

    var_defs = " ".join("float %s;"%new for (new,_) in config['rename'])
    R.gROOT.ProcessLine("""struct TreeHelperStruct{%s};"""%(var_defs))
    from ROOT import TreeHelperStruct, AddressOf
    s = TreeHelperStruct()

    new_branches = {}
    for (new, old) in config['rename']:
        br = tree.Branch(new, AddressOf(s, new), new + "/F")
        if isinstance(old, str):
            new_branches[new] = (R.TTreeFormula("fr_"+new,
                                                old,
                                                tree),
                                 br)

        else:
            # old is really a misnomer here, it is the
            # function to call to create the value for
            # this branch
            new_branches[new] = (old, br)

    print "Looping over all events"
    for i in xrange(total):
        if i%(total/10) == 0:
            print "Now at entry", i+1, "of", total
            
        tree.GetEntry(i)
        for name, (formula,br) in new_branches.iteritems():
            if isinstance(formula, R.TTreeFormula):
                setattr(s, name, formula.EvalInstance(0))

            else:
                setattr(s, name, formula())
                
            br.Fill()

    # By enabling only the new/renamed branches we get rid
    # of all the others
    enable_branches(tree, [new for (new,_) in config['rename']])

    tree.SetName('subTree')
    tree.Write()

    print "Removing extra leaves"
    outFile = R.TFile(config['out_file'], "RECREATE")
    outFile.cd()
    outTree = tree.CloneTree(-1)

    n_after = outTree.GetEntries()

    print "Writing to", config['out_file']
    outTree.Write()

    outTree.SetName('MCTree')
    outTree.Write()

    outFile.Close()

    tmpFile.Close()
    os.remove("/tmp/tmp-asdasdasdq-omgapony.root")


if __name__ == "__main__":
    import sys
    ds_name = sys.argv[1]

    if not ds_name in datasets:
        print "Can not find data set named: %s"%(ds_name)
        print "Possible names: %s"%(", ".join(datasets.keys()))
        sys.exit(1)
    
    create_tree(ds_name)
