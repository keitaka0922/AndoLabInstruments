from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from enum import IntEnum

class SensitivityV(IntEnum):
    V2nV   = 0;  V5nV   = 1;  V10nV  = 2;  V20nV  = 3
    V50nV  = 4;  V100nV = 5;  V200nV = 6;  V500nV = 7
    V1uV   = 8;  V2uV   = 9;  V5uV   = 10; V10uV  = 11
    V20uV  = 12; V50uV  = 13; V100uV = 14; V200uV = 15
    V500uV = 16; V1mV   = 17; V2mV   = 18; V5mV   = 19
    V10mV  = 20; V20mV  = 21; V50mV  = 22; V100mV = 23
    V200mV = 24; V500mV = 25; V1V    = 26

class SensitivityI1M(IntEnum):
    I2fA   = 0;  I5fA   = 1;  I10fA  = 2;  I20fA  = 3
    I50fA  = 4;  I100fA = 5;  I200fA = 6;  I500fA = 7
    I1pA   = 8;  I2pA   = 9;  I5pA   = 10; I10pA  = 11
    I20pA  = 12; I50pA  = 13; I100pA = 14; I200pA = 15
    I500pA = 16; I1nA   = 17; I2nA   = 18; I5nA   = 19
    I10nA  = 20; I20nA  = 21; I50nA  = 22; I100nA = 23
    I200nA = 24; I500nA = 25; I1uA   = 26

class SensitivityI100M(IntEnum):
    I20fA   = 0;  I50fA   = 1;  I100fA  = 2;  I200fA  = 3
    I500fA  = 4;  I1pA    = 5;  I2pA    = 6;  I5pA    = 7
    I10pA   = 8;  I20pA   = 9;  I50pA   = 10; I100pA  = 11
    I200pA  = 12; I500pA  = 13; I1nA    = 14; I2nA    = 15
    I5nA    = 16; I10nA   = 17; I20nA   = 18; I50nA   = 19
    I100nA  = 20; I200nA  = 21; I500nA  = 22; I1uA    = 23
    I2uA    = 24; I5uA    = 25; I10uA   = 26

class TimeConstant(IntEnum):
    TC10us  = 0;  TC30us  = 1;  TC100us = 2;  TC300us = 3
    TC1ms   = 4;  TC3ms   = 5;  TC10ms  = 6;  TC30ms  = 7
    TC100ms = 8;  TC300ms = 9;  TC1s    = 10; TC3s    = 11
    TC10s   = 12; TC30s   = 13; TC100s  = 14; TC300s  = 15
    TC1ks   = 16; TC3ks   = 17; TC10ks  = 18; TC30ks  = 19

class SR830(Instrument):
    def __init__(self, adapter, name="SR830", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI = False,
            **kwargs
        )
    
    def initialize(self):
        self.write('*RST')
    ############################################
    ### Input settings
    ############################################
    input_config = Instrument.control(
        "ISRC?", "ISRC %d",
        """input config""",
        validator=strict_discrete_set,
        values={'A': 0, 'A-B': 1, 'I(1M)': 2, 'I(100M)': 3},
        map_values=True
    )

    ground_config = Instrument.control(
        "IGND?", "IGND %d",
        """ground config""",
        validator=strict_discrete_set,
        values={'Float': 0, 'Ground': 1},
        map_values=True
    )
    
    coupling_config = Instrument.control(
        "ICPL?", "ICPL %d",
        """coupling config""",
        validator=strict_discrete_set,
        values={'AC': 0, 'DC': 1},
        map_values=True
    )

    notch_filter_config = Instrument.control(
        "ILIN?", "ILIN %d",
        """notch filter config""",
        validator=strict_discrete_set,
        values={'out': 0, 'line': 1, '2xline': 2, 'both': 3},
        map_values=True
    )

    ############################################
    ### Sensitivity settings
    ############################################
    sensitivity_config = Instrument.control(
        "SENS?", "SENS %d",
        """sensitivity config""",
        validator=strict_discrete_set,
        values=list(SensitivityV) + list(SensitivityI1M) + list(SensitivityI100M),
        map_values=False
    )

    time_constant = Instrument.control(
        "OFLT?", "OFLT %d",
        """time constant""",
        validator=strict_discrete_set,
        values=list(TimeConstant),
        map_values=False
    )

    dynamic_reserve_config = Instrument.control(
        "RMOD?", "RMOD %d",
        """dynamic reserve mode""",
        validator=strict_discrete_set,
        values={'high': 0, 'normal': 1, 'low_noise': 2},
        map_values=True
    )

    filter_slope_config = Instrument.control(
        "OFSL?", "OFSL %d",
        """low pass filter slope (dB/oct)""",
        validator=strict_discrete_set,
        values={6: 0, 12: 1, 18: 2, 24: 3},
        map_values=True
    )

    sync_filter_config = Instrument.control(
        "SYNC?", "SYNC %d",
        """synchronous filter (only valid below 200 Hz)""",
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )
    ############################################
    ### Reference settings
    ############################################
    phase = Instrument.control(
        "PHAS?", "PHAS %g",
        """reference phase shift (deg), -360.00 to 729.99"""
    )

    reference_source = Instrument.control(
        "FMOD?", "FMOD %d",
        """reference source""",
        validator=strict_discrete_set,
        values={'external': 0, 'internal': 1},
        map_values=True
    )

    internal_frequency = Instrument.control(
        "FREQ?", "FREQ %g",
        """reference frequency (Hz), 0.001 to 102000. internal mode only for set"""
    )

    reference_slope = Instrument.control(
        "RSLP?", "RSLP %d",
        """external reference trigger slope""",
        validator=strict_discrete_set,
        values={'sine': 0, 'ttl_rising': 1, 'ttl_falling': 2},
        map_values=True
    )

    harmonic = Instrument.control(
        "HARM?", "HARM %d",
        """detection harmonic (1 to 19999, limited by n*f <= 102 kHz)"""
    )

    output_reference_voltage = Instrument.control(
        "SLVL?", "SLVL %g",
        """sine output amplitude (Vrms), 0.004 to 5.000"""
    )

    ############################################
    ### Data readout
    ############################################
    x = Instrument.measurement("OUTP?1", """X output (V)""")
    y = Instrument.measurement("OUTP?2", """Y output (V)""")
    r = Instrument.measurement("OUTP?3", """R output (V)""")
    theta = Instrument.measurement("OUTP?4", """theta output (deg)""")

    ch1 = Instrument.measurement("OUTR?1", """CH1 display value""")
    ch2 = Instrument.measurement("OUTR?2", """CH2 display value""")

    def snap(self, *params):
        """
        Read multiple parameters simultaneously (SNAP).
        params: 1=X, 2=Y, 3=R, 4=θ, 5=AuxIn1, 6=AuxIn2,
                7=AuxIn3, 8=AuxIn4, 9=Freq, 10=CH1, 11=CH2
        e.g.: lockin.snap(1, 2)       -> (X, Y)
              lockin.snap(3, 4)       -> (R, θ)
              lockin.snap(1, 2, 9, 5) -> (X, Y, Freq, AuxIn1)
        """
        if not 2 <= len(params) <= 6:
            raise ValueError("snap requires 2 to 6 parameters")
        query = "SNAP?" + ",".join(str(p) for p in params)
        raw = self.ask(query)
        return tuple(float(v) for v in raw.split(","))

    def get_aux_in(self, channel):
        """Read Aux Input voltage (V), channel: 1-4"""
        return float(self.ask(f"OAUX?{channel}"))

    def set_aux_out(self, channel, voltage):
        """Set Aux Output voltage (V), channel: 1-4, -10.5 to 10.5 V"""
        self.write(f"AUXV {channel},{voltage}")

    def get_aux_out(self, channel):
        """Read Aux Output voltage (V), channel: 1-4"""
        return float(self.ask(f"AUXV?{channel}"))
    
    ############################################
    ### Auto config
    ############################################

    def auto_gain(self):
        """
        Perform Auto Gain (same as pressing [AUTO GAIN] key).
        Does nothing if time constant is greater than 1 second.
        May take some time to complete if the time constant is long.
        """
        self.write("AGAN")

    def auto_phase(self):
        """
        Perform Auto Phase (same as pressing [AUTO PHASE] key).
        Does nothing if the phase is unstable.
        Outputs take many time constants to reach new values --
        do not call again without waiting the appropriate amount of time.
        """
        self.write("APHS")

    def auto_offset(self, channel):
        """
        Auto offset X (1), Y (2) or R (3) to zero.
        Same as pressing [AUTO OFFSET] key.
        """
        strict_discrete_set(channel, [1, 2, 3])
        self.write(f"AOFF {channel}")

    def auto_reserve(self):
        """
        Perform Auto Reserve (same as pressing [AUTO RESERVE] key).
        May take some time to complete.
        """
        self.write("ARSV")