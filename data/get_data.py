from subprocess import call
import shutil
import inspect
import os


local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
ganga_job_dir = "~/gj/"

# Currently use incl_b and incl_c as "data"
# the J/Psi signal MC is privately produced
datasets = {"JPsi_data": "{562,563,567,566}/*/output/DVNtuples.root",
            "JPsi_mc": "569/*/output/DVNtuples.root",
            }

if __name__ == "__main__":
    import sys
    ds_name = sys.argv[1]
    if not ds_name in datasets:
        print "Can not find data set named: %s"%(ds_name)
        sys.exit(1)
    
    input_pattern = datasets[ds_name]
    args = " -f /tmp/%s_ntuple.root %s/%s"%(ds_name,
                                            ganga_job_dir,
                                            input_pattern)
    print "Running: hadd %s"%(args)

    try:
        retcode = call("hadd" + args, shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
            sys.exit(1)
            
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e
        sys.exit(1)

    final_name = "%s/%s_ntuple.root"%(local_dir, ds_name)
    if os.path.exists(final_name):
        print "%s already exists, to replace it: delete it first and re-run this script"%(final_name)
        os.remove("/tmp/%s_ntuple.root"%(ds_name))
        sys.exit(1)
        
    shutil.move("/tmp/%s_ntuple.root"%ds_name,  final_name)
