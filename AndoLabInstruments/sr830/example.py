from sr830 import SR830, SensitivityV, TimeConstant

if __name__ == "__main__":
    sr830 = SR830("GPIB0::8::INSTR")
    sr830.initialize()

    # Input settings
    sr830.input_config = 'A'
    sr830.ground_config = 'Ground'
    sr830.coupling_config = 'AC'
    sr830.notch_filter_config = 'both'

    # Sensitivity settings
    sr830.sensitivity_config = SensitivityV.V1mV
    sr830.dynamic_reserve_config = 'normal'
    sr830.time_constant = TimeConstant.TC1s
    sr830.filter_slope_config = 24
    sr830.sync_filter_config = False

    # Reference settings
    sr830.reference_source = 'internal'
    sr830.internal_frequency = 1000.0  # Hz
    sr830.phase = 0.0
    sr830.harmonic = 1
    sr830.output_reference_voltage = 1.0  # Vrms

    # Auto config
    sr830.auto_gain()
    sr830.auto_phase()

    # Read data
    x, y = sr830.snap(1, 2)
    r, theta = sr830.snap(3, 4)
    print(f"X={x:.6e} V, Y={y:.6e} V")
    print(f"R={r:.6e} V, theta={theta:.3f} deg")
    