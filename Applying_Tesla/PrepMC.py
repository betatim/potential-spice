from Gaudi.Configuration import *
from LHCbKernel.Configuration import *
from Configurables import GaudiSequencer,RawEventJuggler
from Configurables import LHCbApp

LHCbApp()
tck = "0x409f0045" 
MySeq=GaudiSequencer("MoveTCKtoNewLocation")
MyWriter=InputCopyStream("CopyToFile")
RawEventJuggler().TCK=tck
RawEventJuggler().Input=2.0 
RawEventJuggler().Output=0.0 
RawEventJuggler().Sequencer=MySeq
RawEventJuggler().WriterOptItemList=MyWriter
RawEventJuggler().KillInputBanksAfter="L0*|Hlt*"
RawEventJuggler().KillExtraNodes=True 
ApplicationMgr().TopAlg = [MySeq]
LHCbApp().EvtMax=1000

from GaudiConf import IOHelper
IOHelper().outStream("/tmp/ikomarov/Rewrited.dst",MyWriter)
IOHelper().inputFiles( [ "/tmp/ikomarov/00024923_00000001_1.allstreams.dst"], clear=True ) 
