from Ganga.GPI import *
import sys
import inspect
import os


local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

if len(sys.argv) not in (3,4):
    sys.exit("Script requires the id of a Moore (L0) job to use as inputdata, the magnet polarity and optionally name of a file containing LFNs to process.")

old = int(sys.argv[1])
polarity = str(sys.argv[2])
input_lfns = []
if len(sys.argv) == 4:
    f = open(sys.argv[3])
    for line in f:
        input_lfns.append(line.strip())
    f.close()

if jobs(old).application.__class__ is not Moore:
    sys.exit("The given job is not a Moore job.")

j = Job(application=Moore(version="v23r2",
                          optsfile=local_dir + "/moore-job.py",
                          extraopts="""\nexecute("%s")\n"""%(polarity),
                          user_release_area=local_dir +"/../cmtuser/",
                          )
        )

j.outputfiles = [DiracFile("*.dst"),
                 DiracFile("*.xdst")]
j.backend = Dirac()

j.splitter = SplitByFiles(filesPerJob=1)

j.name = jobs(old).name
j.comment = "HLT with input from job %i"%(old)

j.inputsandbox.append(local_dir + "/tcks/config.tar")

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
queues.add(j.submit)
#j.submit()
