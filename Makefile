
# Create subTrees used as input for the fitter
subtrees: fitting/JPsi_data_sub.root

fitting/JPsi_data_sub.root: data/JPsi_data_ntuple.root
	python fitting/create_subtree.py JPsi_data


# Collect the ganga output
.PHONY: JPsi_data_ntuple JPsi_mc_ntuple
collect_ntuples: data/JPsi_mc_ntuple.root data/JPsi_data_ntuple.root

data/JPsi_data_ntuple.root:
	python data/get_data.py JPsi_data

data/JPsi_mc_ntuple.root:
	python data/get_data.py JPsi_mc
