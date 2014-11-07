from Configurables import EventNodeKiller, ApplicationMgr
appConf = ApplicationMgr()
appConf.ExtSvc += ['DataOnDemandSvc']
enk = EventNodeKiller('KillTrigRawEvent')
enk.Nodes = [ "Hlt","Hlt1","Hlt2","Trig","Raw", "Trigger/RawEvent", "Trigger" ]
appConf.TopAlg.insert( 0,  enk.getFullName() ) 

from Configurables import L0App
L0App().TCK = '0x0044'
L0App().ReplaceL0Banks = True
L0App().EvtMax = -1
L0App().DataType = '2012'
L0App().DDDBtag   = 'dddb-20130929-1'  ## latest strip20 tags as of Jan2013
L0App().CondDBtag = 'sim-20131023-vc-md100'
L0App().Simulation = True
L0App().outputFile = '/tmp/ikomarov/With_new_L0.dst'
from Configurables import EventSelector
EventSelector().PrintFreq = 3
from Configurables import MessageSvc
MessageSvc().OutputLevel = 3
from GaudiConf import IOHelper
IOHelper().inputFiles( [ "/tmp/ikomarov/Rewrited.dst"] ) 
from Configurables import RootCnvSvc
RootCnvSvc().OutputLevel=3
