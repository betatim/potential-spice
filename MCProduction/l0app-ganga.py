from Ganga.GPI import *
import sys
import inspect
import os


local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

if len(sys.argv) not in (3,4):
    sys.exit("Script requires the id of a Boole or Moore job to use as inputdata, magnet polarity and optionally name of a file containing LFNs to process.")

old = int(sys.argv[1])
polarity = str(sys.argv[2])
input_lfns = []
if len(sys.argv) == 4:
    f = open(sys.argv[3])
    for line in f:
        input_lfns.append(line.strip())
    f.close()

if jobs(old).application.__class__ not in (Boole, Moore):
    sys.exit("The given job is not a Boole or Moore job.")

j = Job(application=Moore(version="v23r2",
                          optsfile=local_dir + "/l0app-job.py",
                          extraopts="""\nexecute("%s")\n"""%polarity,
                          )
        )

j.outputfiles = [DiracFile("*.dst"),
                 DiracFile("*.xdst")]
j.backend = Dirac()

j.splitter = SplitByFiles(filesPerJob=1)

j.name = jobs(old).name
j.comment = "L0 input from job %i"%(old)

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
#j.submit()
queues.add(j.submit)
