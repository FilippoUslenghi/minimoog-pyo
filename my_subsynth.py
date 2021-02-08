from pyo import *

class mySubSynth(PyoObject):

    """
    This class instances a subtractive synthesizer with 3 oscillators and one fourth-order lowpass resonant filter Moog alike.
    You can control the oscillators and filter parameters via GUI 
    You can play the syntheziser using you computer keyboard or the MIDI keyboard on your desktop.

    :Parent: :py:class:`PyoObject`

    :Args:

      type1 : int, optional
          Waveform type of the first oscillator. Eight possible values :  
            0. Saw up
            1. Saw down  
            2. Square  
            3. Triangle  
            4. Pulse  
            5. Bipolar pulse  
            6. Sample and hold  
            7. Modulated Sine
            Default to 0.
      sharp1 : float or PyoObject, optional
          Sharpness factor of the first oscillator. Sharper waveform results  
          in more harmonics in the spectrum. Defaults to 0.5.
      type2 : int, optional
          Waveform type of the second oscillator. Eight possible values :  
            0. Saw up
            1. Saw down  
            2. Square  
            3. Triangle  
            4. Pulse  
            5. Bipolar pulse  
            6. Sample and hold  
            7. Modulated 
            Default to 0.
      sharp2 : float or PyoObject
          Sharpness factor of the second oscillator. Sharper waveform results  
          in more harmonics in the spectrum. Defaults to 0.5.
      type3 : int, optional
          Waveform type of the third oscillator. Eight possible values :  
            0. Saw up
            1. Saw down  
            2. Square  
            3. Triangle  
            4. Pulse  
            5. Bipolar pulse  
            6. Sample and hold  
            7. Modulated Sine
            Default to 0.
      sharp3 : float or PyoObject
          Sharpness factor of the third oscillator. Sharper waveform results  
          in more harmonics in the spectrum. Defaults to 0.5.
      cutoffFact : float or PyoObject, optional
          Factor of the cutoff frequency of the filter. Defaults to 0.5.
      res: float or PyoObject, optional  
        Amount of Resonance of the filter, usually between 0 (no resonance)  
        and 1 (medium resonance). Default to 0.5

    >>> s=Server().boot()
    >>> sy = mySubSynth().out()
    >>> sy.ctrl()
    """

    def __init__(self, type1=0, sharp1=1, type2=0, sharp2=1, type3=0, sharp3=1, cutoffFact=0.5, res=0.5):
        
        # Call superclass (PyoObject) constructor
        super().__init__()
        
        # Define and initialize instance attributes
        self._type1 = type1
        self._sharp1 = sharp1
        self._type2 = type2
        self._sharp2 = sharp2
        self._type3 = type3
        self._sharp3 = sharp3
        self._cutoffFact = cutoffFact
        self._res = res

        # pitches in Hz
        notes = Notein()
        # Show a keyboard widget to supply MIDI events
        notes.keyboard()
       
        # Note pitches
        freqs = MToF(notes["pitch"])
        # ADSR on note amplitudes
        self._env = MidiAdsr(notes["velocity"], attack=0.05, decay=0.4, sustain=0.2, release=0.5, mul=0.65)

        # Define audio processing chain using constructor arguments
        #1. Create the first oscillator
        self._osc1 = LFO(freq=freqs, sharp=self._sharp1, type=self._type1, mul=self._env)
        #2. Add the first oscillator to the second one
        self._osc2 = LFO(freq=freqs, sharp=self._sharp2, type=self._type2, mul=self._env, add=self._osc1)
        #3. Add the sum the previuos two oscillators to the third one
        self._osc3 = LFO(freq=freqs, sharp=self._sharp3, type=self._type3, mul=self._env, add=self._osc2)

        #4. Filter the result of the sum of the three oscillators with a lowpass resonant filter
        self._filt = MoogLP(input=self._osc3, freq=self._env*20000*self._cutoffFact, res=self._res)
        #5. Make the signal stereo
        self._stereo = Pan(self._filt, outs=2, pan=0.5)


        # Define output seen by outside world: self._base_objs
        # Returned by getBaseObjects() method
        self._base_objs = self._stereo.getBaseObjects()

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list_osc = [SLMap(0, 7, "lin", "type1", self._type1, res='int', dataOnly=True), 
                              SLMap(0, 1, "lin", "sharp1", self._sharp1, res='float'), 
                              SLMap(0, 7, "lin", "type2", self._type2, res='int', dataOnly=True),
                              SLMap(0, 1, "lin", "sharp2", self._sharp2, res='float'),
                              SLMap(0, 7, "lin", "type3", self._type3, res='int', dataOnly=True),
                              SLMap(0, 1, "lin", "sharp3", self._sharp3, res='float')]
        super().ctrl(self._map_list_osc, title, wxnoserver)

        self._map_list_filt = [SLMap(0, 1, "lin", "cutoffFact", self._cutoffFact, res='float'),
                               SLMap(0, 1, "lin", "res", self._res, res='float')]
        super().ctrl(self._map_list_filt, title, wxnoserver)

        self._env.ctrl()

    def play(self, dur=0, delay=0):
        self._osc1.play(dur, delay)
        self._osc2.play(dur, delay)
        self._osc3.play(dur, delay)
        self._filt.play(dur, delay)
        self._stereo.play(dur, delay)
        return super().play(dur, delay)

    def stop(self):
        self._osc1.stop()
        self._osc2.stop()
        self._osc3.stop()
        self._filt.stop()
        self._stereo.stop()
        return super().stop()

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._osc1.play(dur, delay)
        self._osc2.play(dur, delay)
        self._osc3.play(dur, delay)
        self._filt.play(dur, delay)
        self._stereo.play(dur, delay)
        return super().out(chnl, inc, dur, delay)

    def setType1(self, x):
        """
        Replace the `type1` attribute.

        :Args:

            x : int
                New `type1` attribute.

        """
        self._type1 = x
        self._osc1.type = x

    def setSharp1(self, x):
        """
        Replace the `sharp1` attribute.

        :Args:

            x : float or PyoObject
                New `sharp1` attribute.

        """
        self._sharp1 = x
        self._osc1.sharp = x

    def setType2(self, x):
        """
        Replace the `type2` attribute.

        :Args:

            x : int
                New `type2` attribute.

        """
        self._type2 = x
        self._osc2.type = x

    def setSharp2(self, x):
        """
        Replace the `sharp2` attribute.

        :Args:

            x : float or PyoObject
                New `sharp2` attribute.

        """
        self._sharp2 = x
        self._osc2.sharp = x

    def setType3(self, x):
        """
        Replace the `type3` attribute.

        :Args:

            x : int
                New `type3` attribute.

        """
        self._type3 = x
        self._osc3.type = x

    def setSharp3(self, x):
        """
        Replace the `sharp3` attribute.

        :Args:

            x : float or PyoObject
                New `sharp3` attribute.

        """
        self._sharp3 = x
        self._osc3.sharp = x

    def setCutoffFact(self, x):
        """
        Replace the `cutoffFact` attribute.

        :Args:

            x : float or PyoObject
                New `cutoffFact` attribute.

        """
        self._cutoffFact = x
        self._filt.freq = self._env*20000*x
    
    def setRes(self, x):
        """
        Replace the `res` attribute.

        :Args:

            x : float or PyoObject
                New `res` attribute.

        """
        self._res = x
        self._filt.res = x

    @property
    def type1(self):
        """int. Type of osc1."""
        return self._type1
    @type1.setter
    def type1(self, x):
        self.setType1(x)
    
    @property
    def sharp1(self):
        """float or PyoObject. Sharp of osc1."""
        return self._sharp1
    @sharp1.setter
    def sharp1(self, x):
        self.setSharp1(x)

    @property
    def type2(self):
        """int. Type of osc2."""
        return self._type2
    @type2.setter
    def type2(self, x):
        self.setType2(x)
    
    @property
    def sharp2(self):
        """float or PyoObject. Sharp of osc2."""
        return self._sharp2
    @sharp2.setter
    def sharp2(self, x):
        self.setSharp2(x)

    @property
    def type3(self):
        """int. Type of osc3."""
        return self._type3
    @type3.setter
    def type3(self, x):
        self.setType3(x)

    @property
    def sharp3(self):
        """float or PyoObject. Sharp of osc3."""
        return self._sharp3
    @sharp3.setter
    def sharp3(self, x):
        self.setSharp3(x)

    @property
    def cutoffFact(self):
        """float or PyoObject. CutoffFact of filt."""
        return self._cutoffFact
    @cutoffFact.setter
    def cutoffFact(self, x):
        self.setCutoffFact(x)

    @property
    def res(self):
        """float or PyoObject. Res of filt."""
        return self._res
    @res.setter
    def res(self, x):
        self.setRes(x)
        


if __name__ == "__main__":
    
    s=Server().boot()
    s.amp=0.5

    sy = mySubSynth().out()
    sy.ctrl()

    s.gui(locals())
        