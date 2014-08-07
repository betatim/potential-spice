from Ganga.GPI import *
import sys
import inspect
import os


local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

datasets = {
    # Signal MC for JPsi
    "JPsi": {"optsfile": "JPsiNTuple.py",
             "files": [l.strip() for l in
                       open(local_dir + "/homemade-JPsiincl-brunel.lfns")],
             "filesPerJob": 20,
             },
    # Same sign processing of inclusive B, MagUp and MagDown
    "InclB_neg": {"optsfile": "JPsiNTuple.py",
                  "files": "/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/Reco15DEV/10000000/XDST",
                  "filesPerJob": 10,
                  "extraopts": "execute(decay_descriptor='J/psi(1S) -> mu- mu-')",
                  },
    "InclB_pos": {"optsfile": "JPsiNTuple.py",
                  "files": "/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/Reco15DEV/10000000/XDST",
                  "filesPerJob": 10,
                  "extraopts": "execute(decay_descriptor='J/psi(1S) -> mu+ mu+')",
                  },
    "InclB_neg_Up": {"optsfile": "JPsiNTuple.py",
                     "files": "/MC/Dev/Beam6500GeV-RunII-MagUp-Nu1.5-25ns-Pythia8/Sim08e/Reco15DEV/10000000/XDST",
                     "filesPerJob": 10,
                     "extraopts": "execute(decay_descriptor='J/psi(1S) -> mu- mu-')",
                     },
    "InclB_pos_Up": {"optsfile": "JPsiNTuple.py",
                     "files": "/MC/Dev/Beam6500GeV-RunII-MagUp-Nu1.5-25ns-Pythia8/Sim08e/Reco15DEV/10000000/XDST",
                     "filesPerJob": 10,
                     "extraopts": "execute(decay_descriptor='J/psi(1S) -> mu+ mu+')",
                     },
    # Opposite sign processing of inclusive B, MagUp and MagDown
    "InclB_OS_Down": {"optsfile": "JPsiNTuple.py",
                      "files": "/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/Reco15DEV/10000000/XDST",
                      "filesPerJob": 10,
                      },
    "InclB_OS_Up": {"optsfile": "JPsiNTuple.py",
                    "files": "/MC/Dev/Beam6500GeV-RunII-MagUp-Nu1.5-25ns-Pythia8/Sim08e/Reco15DEV/10000000/XDST",
                    "filesPerJob": 10,
                    },
    # Opposite sign processing of inclusive C, MagUp and MagDown
    "InclC_OS_Down": {"optsfile": "JPsiNTuple.py",
                      "files": "/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/Reco15DEV/20000000/XDST",
                      "filesPerJob": 5,
                      },
    "InclC_OS_Up": {"optsfile": "JPsiNTuple.py",
                    "files": "/MC/Dev/Beam6500GeV-RunII-MagUp-Nu1.5-25ns-Pythia8/Sim08e/Reco15DEV/20000000/XDST",
                            "filesPerJob": 5,
                    },
    }

if len(sys.argv) != 2:
    sys.exit("Script requires a dataset name to run over.")

dataset_name = sys.argv[1]
try:
    options = datasets[dataset_name]

except KeyError:
    print "Can not find datset named %s."%(dataset_name)
    print "Available datasets: %s"%(",".join(datasets.keys()))
    sys.exit(1)


j = Job(application=DaVinci(version="v35r1",
                            optsfile=local_dir + "/" + options['optsfile'],
                            extraopts=options.get("extraopts", "execute()"),
                            )
        )

j.backend = Dirac()
j.splitter = SplitByFiles(filesPerJob=options.get("filesPerJob", 1))
j.name = "Early %s"%(dataset_name)

if isinstance(options["files"], list):
    j.comment = "Files: "+",".join(options["files"])
    j.inputdata = []
    j.inputdata.extend(["LFN:" + lfn for lfn in options["files"]])

elif isinstance(options["files"], str):
    j.comment = "Files from %s"%(options["files"])
    j.inputdata = BKQuery(options["files"],
                          dqflag=['OK']).getDataset()

j.prepare()
j.submit()
