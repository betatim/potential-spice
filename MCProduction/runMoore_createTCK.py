from Gaudi.Configuration import *
from Configurables import Moore

## Adapt these to your local environment
Moore().TCKData = '/tmp/thead/'
Moore().ThresholdSettings = 'Physics_draftEM2015'
Moore().generateConfig = True
Moore().configLabel = "Tim's early2015 turbo TCK"

## Make sure these are correct
Moore().DataType = "2015"
Moore().DDDBtag = "dddb-20140729"
Moore().CondDBtag = "sim-20140730-vc-md100"

## Specify input, generally a DST
Moore().inputFiles = [ "PFN:Early2015-Juggled.dst" ]

## General Moore settings, these shouldn't need to be touched
Moore().Simulation=True
Moore().ForceSingleL0Configuration = True
Moore().CheckOdin = True
Moore().EvtMax = 10000
#Moore().UseDBSnapshot = False
#Moore().EnableRunChangeHandler = False
#Moore().Verbose = True
