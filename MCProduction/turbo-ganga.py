from Ganga.GPI import *
import sys
import inspect
import os


local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

if len(sys.argv) not in (2,3):
    sys.exit("Script requires the id of a Moore (HLT) or Brunel job to use as inputdata and optionally name of a file containing LFNs to process.")

old = int(sys.argv[1])
input_lfns = []
if len(sys.argv) == 3:
    f = open(sys.argv[2])
    for line in f:
        input_lfns.append(line.strip())
    f.close()

if jobs(old).application.__class__ not in (Moore, Brunel):
    sys.exit("The given job is not a Moore or Brunel job.")

j = Job(application=DaVinci(version="v36r2",
                            optsfile=local_dir + "/turbo-job.py",
                            extraopts="""\nexecute()\n""",
                            user_release_area=local_dir +"/../cmtuser/",
                            )
        )

j.outputfiles = [DiracFile("*.dst"),
                 DiracFile("*.xdst")]
j.backend = Dirac()

j.splitter = SplitByFiles(filesPerJob=1)

j.name = jobs(old).name
j.comment = "Turbo with input from job %i"%(old)

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
