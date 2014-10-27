from Ganga.GPI import *
import sys
import inspect
import os


local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

if len(sys.argv) is not 2:
  sys.exit("Error, needs one argument, the event type to use.")

event_type = int(sys.argv[1])

j = Job(application=Gauss(version="v47r0",
                          optsfile = local_dir + "/gauss-job.py",
                          extraopts = """\nexecute('%s')\n"""%event_type
                          )
        )

j.name = "Early-%s"%event_type
j.outputfiles = [DiracFile("*.sim",
                           locations=['CERN-USER'])]

j.backend=Dirac()
j.backend.settings['BannedSites'] = ['LCG.RRCKI.ru']

events = 10000
eventsperjob = 25

j.splitter = GaussSplitter(numberOfJobs=int(round(events*1.1/eventsperjob)),
                           eventsPerJob=eventsperjob)


j.prepare()
j.submit()
