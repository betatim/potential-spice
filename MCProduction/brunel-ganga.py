from Ganga.GPI import *
import sys


local_dir= "/afs/cern.ch/user/t/thead/w/private/early2015/MCProduction/"

if len(sys.argv) not in (2,3):
    sys.exit("Script requires the id of the boole job to use as inputdata and optionally a file containing LFNs to process.")
  
old = int(sys.argv[1])
input_lfns = []
if len(sys.argv) == 3:
    f = open(sys.argv[2])
    for line in f:
        input_lfns.append(line.strip())
    f.close()

if jobs(old).application.__class__ is not Boole:
    sys.exit("The given job is not a Boole job.")

j = Job(application=Brunel(version="v46r1",
                           optsfile=local_dir+"brunel-job.py",
                           extraopts="\nexecute()\n",
                           )
        )

j.backend = Dirac()
j.backend.diracOpts = 'ReplicateUserOutputData=False'
j.splitter = SplitByFiles(filesPerJob=1)
j.name = jobs(old).name
j.comment = "Input from job %i"%(old)
j.outputfiles = [DiracFile("*.xdst")]

if input_lfns:
    j.inputdata = []
    logicals = [LogicalFile(l[5:-1]) for l in input_lfns]
    j.inputdata.extend(logicals)

else:
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
