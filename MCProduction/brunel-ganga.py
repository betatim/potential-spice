from Ganga.GPI import *
import sys


local_dir= "/afs/cern.ch/user/t/thead/w/private/early2015/MCProduction/"

if len(sys.argv) is not 2:
    sys.exit("Script requires the id of the boole job to use as inputdata.")
  
old = int(sys.argv[1])
if jobs(old).application.__class__ is not Boole:
    sys.exit("The given job is not a Boole job.")

j = Job(application=Brunel(version="v46r1",
                           optsfile=local_dir+"brunel-job.py",
                           extraopts="\nexecute()\n",
                           )
        )

j.backend = Dirac()
j.splitter = SplitByFiles(filesPerJob=1)
j.name = jobs(old).name
j.comment = "Input from job %i"%(old)
j.outputfiles = [DiracFile("*.xdst")]


if len(jobs(old).subjobs) == 0:
    j.inputdata = jobs(old).outputfiles
else:
    j.inputdata = []
    for osj in jobs(old).subjobs.select(status='completed'):
        for f in osj.outputfiles:
            if isinstance(f, DiracFile):
                if f.lfn:
                    j.inputdata.extend([LogicalFile(f.lfn)])

j.prepare()
j.submit()
