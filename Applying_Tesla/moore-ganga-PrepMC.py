from Ganga.GPI import *
import sys
import inspect
import os

my_area = '/afs/cern.ch/user/i/ikomarov/cmtuser'
local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

j = Job(application=Moore(version="v22r1p1",
                          optsfile=local_dir + "/PrepMC.py",
                          user_release_area=my_area
                          ),
        #inputdata = DaVinci().readInputData('Jpsi2MuMuRun2.py')
        inputdata = DaVinci().readInputData('MC201224142001Beam4000GeV-2012-MagDown-Nu25-Pythia6Sim08aDigi13Trig0x409f0045Reco14aStripping20NoPrescalingFlaggedSTREAMSDST.py')
        )

#j.outputfiles = [MassStorageFile("*.dst")]
j.outputfiles = [DiracFile("*.dst")]
                 #DiracFile("*.xdst")]
#j.backend = Interactive()
j.backend = Dirac()

j.splitter = SplitByFiles(filesPerJob=1)

j.name = "PrepMC"

j.submit()
