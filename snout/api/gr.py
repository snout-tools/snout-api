from snout.api.agent import SnoutAgent
import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))
try:
    from gnuradio import gr
except ImportError as e:
    print('Error importing gnuradio. Snout requires a gnuradio installation')
    sys.exit(f'{e.__class__.__name__}: {e.message}')
from gnuradio import blocks
import signal

class GnuradioComponentAPI(SnoutAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.block = gr.hier_block2
        self.samp_rate = kwargs.get("sample_rate") # desired sample rate of the component
        self.instrument = kwargs.get("instrument") # instrument attached to this component
        self.center_freq = kwargs.get("center_freq") # default center freq (can be altered)
        self.mode = None # tx, rx, rf
        #TODO: attributes/properties for rx and tx connect blocks
        self.build_component()
    
    def build_component(self):
        """Add code here to actually initialize the block and
        build the gnuradio component 
        """
        raise NotImplementedError


class GnuradioHandlerAPI(SnoutAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tb = gr.top_block
        gr.top_block.__init__(self.tb, self.name)

        self.samp_rate = kwargs.get("samp_rate")
        self.center_freq = None
    
    def add_instrument(self, instrument):
        self.add_component(instrument.component)
    
    def add_tx(self, component):
        raise NotImplementedError
    
    def add_rx(self, component):
        raise NotImplementedError

    def add_component(self, component):
        """Adds a GnuradioComponent to the flowgraph. First,
        figures out if the component is compatible, and if so then adds it 
        to the flowgraph.

        Args:
            component (GnuradioComponent): instrument to add
        """
        raise NotImplementedError
    
    def reset(self):
        """Removes all current components, resetting the handler's
        flowgraph
        """
        self.tb = gr.top_block
        gr.top_block.__init__(self.tb, self.name)
        self.center_freq = None

    def runlogic(self, *args, **kwargs):

        def sig_handler(sig=None, frame=None):
            self.tb.stop()
            self.tb.wait()

            sys.exit(0)

        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)

        self.tb.start()

        # self.tb.wait()
    
    def stoplogic(self, *args, **kwargs):

        self.tb.stop()

