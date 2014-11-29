from Ganga.GPI import *
import sys
import inspect
import os


local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

if len(sys.argv) != 2:
    sys.exit("Script requires a bookkeeping path as input.")

bk_path = sys.argv[1]

j = Job(application=Moore(version="v23r2",
                          optsfile=local_dir + "/juggler-job.py",
                          extraopts="""\nexecute()\n""",
                          )
        )

j.outputfiles = [DiracFile("*.dst"),
                 DiracFile("*.xdst")]
j.backend = Dirac()

j.splitter = SplitByFiles(filesPerJob=1)

j.name = "Juggler Early2015"
j.comment = "Input from %s"%(bk_path)


j.inputdata = BKQuery(bk_path).getDataset()

j.prepare()
queues.add(j.submit)
