# get the basic configuration from here
#import GaudiPython
from LHCbKernel.Configuration import *
from Configurables import ( LHCbConfigurableUser, LHCbApp,
                            DstConf, CaloDstUnPackConf )

from Configurables import Moore, HltConfigSvc
from Configurables import ConfigTarFileAccessSvc
ConfigTarFileAccessSvc().File='config.tar'
Moore().TCKData='/afs/cern.ch/work/s/sbenson/public/forTeslaExtendedReps'

Moore().InitialTCK="0x45b10044"
Moore().UseTCK = True
Moore().ForceSingleL0Configuration = False
Moore().CheckOdin = False
Moore().EvtMax = -1
Moore().EnableDataOnDemand = False
Moore().DDDBtag   = "dddb-20130929-1"
Moore().CondDBtag = "sim-20131023-vc-md100"
Moore().DataType = '2012'
Moore().Simulation = True

from GaudiConf import IOHelper
IOHelper().inputFiles( [ "/tmp/ikomarov/With_new_L0.dst"] ) 
Moore().outputFile = '/tmp/ikomarov/With_new_HLT.dst'

from Configurables import L0MuonAlg
L0MuonAlg( "L0Muon" ).L0DUConfigProviderType = "L0DUConfigProvider"
