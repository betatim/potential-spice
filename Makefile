
# Create subTrees used as input for the fitter
subtrees: fitting/JPsi_data_sub.root fitting/JPsi_mc_sub.root
fitting/%_sub.root: data/%_ntuple.root fitting/create_subtree.py
	python fitting/create_subtree.py $*


# Collect the ganga output
collect_ntuples: data/JPsi_mc_ntuple.root data/JPsi_data_ntuple.root
data/%_ntuple.root:
	python data/get_data.py $*
