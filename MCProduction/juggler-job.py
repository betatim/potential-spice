from Gaudi.Configuration import *
from LHCbKernel.Configuration import *
from Configurables import GaudiSequencer,RawEventJuggler
from Configurables import LHCbApp

def execute():
    LHCbApp()
    tck = "0x40b10033"
    MySeq = GaudiSequencer("MoveTCKtoNewLocation")
    MyWriter = InputCopyStream("CopyToFile")
    RawEventJuggler().TCK = tck
    RawEventJuggler().Input = 4.0 #2.0 ?
    RawEventJuggler().Output = 0.0
    RawEventJuggler().Sequencer = MySeq
    RawEventJuggler().WriterOptItemList = MyWriter
    RawEventJuggler().KillInputBanksAfter= " L0*|Hlt*"
    RawEventJuggler().KillExtraNodes = True 
    ApplicationMgr().TopAlg = [MySeq]
    LHCbApp().EvtMax = -1

    from GaudiConf import IOHelper
    IOHelper().outStream("Early2015-Juggled.dst", MyWriter)
    #IOHelper().inputFiles( [ "PATH/TO/INPUT"], clear=True ) 
