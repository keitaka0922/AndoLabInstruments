"""
NF Corporation EC750SA プログラマブル交流電源 PyMeasure ドライバー

接続方法:
  - USB (USBTMC): "USB0::3402::12::SER_NUMBER::INSTR"
  - RS232: "ASRL/dev/ttyUSB0::INSTR" など (任意波転送は USB のみ対応)

使用例:
    from pymeasure.instruments import EC750SA

    # USB 接続
    source = EC750SA("USB0::3402::12::000001::INSTR")

    source.reset()
    source.voltage_range = 100       # 100V レンジS
    source.mode = "AC-INT"           # 交流内部信号源モード
    source.frequency = 50.0          # 50 Hz
    source.voltage = 100.0           # 100 Vrms
    source.output_enabled = True     # 出力オン

    print(source.measured_voltage)   # 計測電圧
    print(source.measured_current)   # 計測電流
    print(source.measured_power)     # 有効電力

    source.output_enabled = False    # 出力オフ
    source.shutdown()
"""

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_range,
    strict_discrete_set,
    truncated_range,
)


class EC750SA(Instrument):
    """NF Corporation EC750SA プログラマブル交流電源ドライバー。

    SCPI (IEEE 488.2 / SCPI 1999.0) 準拠。
    USB (USBTMC) または RS232 インターフェース経由で制御します。

    :param adapter: VISA リソース文字列またはアダプタオブジェクト
    :param name: 機器の識別名 (省略可)
    :param kwargs: Instrument に渡す追加引数
    """

    name = "NF Corporation EC750SA"

    # ────────────────────────────────────────────
    # SOURce サブシステム
    # ────────────────────────────────────────────

    mode = Instrument.control(
        "MODE?",
        "MODE %s",
        """出力モードを設定／取得します。
        AC-INT / AC-EXT / AC-ADD / AC-SYNC /
        ACDC-INT / ACDC-EXT / ACDC-ADD / ACDC-SYNC から選択。
        出力オン中は変更できません。""",
        validator=strict_discrete_set,
        values=[
            "AC-INT", "AC-EXT", "AC-ADD", "AC-SYNC",
            "ACDC-INT", "ACDC-EXT", "ACDC-ADD", "ACDC-SYNC",
        ],
    )

    voltage = Instrument.control(
        "VOLT?",
        "VOLT %g",
        """交流出力電圧を Vrms 単位で設定／取得します。
        100V レンジ: 0.0～155.0 Vrms (ARB 波形時は Vp-p: 0.0～440.0)
        200V レンジ: 0.0～310.0 Vrms (ARB 波形時は Vp-p: 0.0～880.0)
        AC-EXT / AC+DC-EXT モードでは使用できません。""",
        validator=truncated_range,
        values=[0.0, 880.0],
    )

    voltage_offset = Instrument.control(
        "VOLT:OFFS?",
        "VOLT:OFFS %g",
        """直流出力電圧を V 単位で設定／取得します (AC+DC-INT/ADD/SYNC モード専用)。
        100V レンジ: -220.0～220.0 V
        200V レンジ: -440.0～440.0 V""",
        validator=truncated_range,
        values=[-440.0, 440.0],
    )

    voltage_range = Instrument.control(
        "VOLT:RANG?",
        "VOLT:RANG %d",
        """出力電圧レンジを V 単位で設定／取得します (100 または 200)。
        出力オン中は変更できません。""",
        validator=strict_discrete_set,
        values=[100, 200],
        cast=int,
    )

    voltage_limit_high = Instrument.control(
        "VOLT:LIM:HIGH?",
        "VOLT:LIM:HIGH %g",
        """設定可能な出力電圧の上限を設定／取得します。
        100V レンジ: 0.1～220.0 V / 200V レンジ: 0.1～440.0 V""",
        validator=truncated_range,
        values=[0.1, 440.0],
    )

    voltage_limit_low = Instrument.control(
        "VOLT:LIM:LOW?",
        "VOLT:LIM:LOW %g",
        """設定可能な出力電圧の下限を設定／取得します。
        100V レンジ: -220.0～-0.1 V / 200V レンジ: -440.0～-0.1 V""",
        validator=truncated_range,
        values=[-440.0, -0.1],
    )

    frequency = Instrument.control(
        "FREQ?",
        "FREQ %g",
        """出力周波数を Hz 単位で設定／取得します (1.0～550.0 Hz)。
        AC-EXT / AC-SYNC / AC+DC-EXT / AC+DC-SYNC モードでは使用できません。""",
        validator=strict_range,
        values=[1.0, 550.0],
    )

    frequency_limit_high = Instrument.control(
        "FREQ:LIM:HIGH?",
        "FREQ:LIM:HIGH %g",
        """設定可能な周波数の上限を Hz 単位で設定／取得します (1.0～550.0 Hz)。""",
        validator=strict_range,
        values=[1.0, 550.0],
    )

    frequency_limit_low = Instrument.control(
        "FREQ:LIM:LOW?",
        "FREQ:LIM:LOW %g",
        """設定可能な周波数の下限を Hz 単位で設定／取得します (1.0～550.0 Hz)。""",
        validator=strict_range,
        values=[1.0, 550.0],
    )

    waveform = Instrument.control(
        "FUNC?",
        "FUNC %s",
        """出力波形を設定／取得します (SIN / SQU / ARB1～ARB16)。
        AC-EXT / AC+DC-EXT モードでは使用できません。""",
        validator=strict_discrete_set,
        values=["SIN", "SQU"] + [f"ARB{i}" for i in range(1, 17)],
    )

    phase = Instrument.control(
        "PHAS?",
        "PHAS %g",
        """出力開始時の位相を度単位で設定／取得します (0.0～359.9°)。
        出力オン中または AC-EXT / AC+DC-EXT モードでは変更できません。""",
        validator=strict_range,
        values=[0.0, 359.9],
    )

    phase_clock = Instrument.control(
        "PHAS:CLOC?",
        "PHAS:CLOC %s",
        """外部同期モード時の同期信号源を設定／取得します (LINE / EXT)。
        AC-SYNC / AC+DC-SYNC モード専用。出力オン中は変更できません。""",
        validator=strict_discrete_set,
        values=["LINE", "EXT"],
    )

    current_limit_rms = Instrument.control(
        "CURR:LIM:RMS?",
        "CURR:LIM:RMS %g",
        """電流実効値リミッタを A 単位で設定／取得します。
        100V レンジ: 1.0～10.5 A / 200V レンジ: 1.0～5.3 A""",
        validator=strict_range,
        values=[1.0, 10.5],
    )

    current_limit_peak_high = Instrument.control(
        "CURR:LIM:PEAK:HIGH?",
        "CURR:LIM:PEAK:HIGH %g",
        """電流ピーク値リミッタ（正極性）を Apk 単位で設定／取得します。
        100V レンジ: 10.0～31.5 Apk / 200V レンジ: 5.0～15.8 Apk""",
        validator=strict_range,
        values=[10.0, 31.5],
    )

    current_limit_peak_low = Instrument.control(
        "CURR:LIM:PEAK:LOW?",
        "CURR:LIM:PEAK:LOW %g",
        """電流ピーク値リミッタ（負極性）を Apk 単位で設定／取得します。
        100V レンジ: -31.5～-10.0 Apk / 200V レンジ: -15.8～-5.0 Apk""",
        validator=strict_range,
        values=[-31.5, -10.0],
    )

    voltage_dc_offset_adjust_ac = Instrument.control(
        "VOLT:ADJ:OFFS:AC?",
        "VOLT:ADJ:OFFS:AC %g",
        """AC モード時の DC オフセット電圧調整値を mV 単位で設定／取得します (-50.0～50.0 mV)。
        AC-INT / AC-EXT / AC-ADD / AC-SYNC モード専用。""",
        validator=strict_range,
        values=[-50.0, 50.0],
    )

    voltage_dc_offset_adjust_dc = Instrument.control(
        "VOLT:ADJ:OFFS:DC?",
        "VOLT:ADJ:OFFS:DC %g",
        """AC+DC モード時の DC オフセット電圧調整値を mV 単位で設定／取得します (-250～250 mV)。
        AC+DC-INT / AC+DC-EXT / AC+DC-ADD / AC+DC-SYNC モード専用。""",
        validator=strict_range,
        values=[-250.0, 250.0],
    )

    # ────────────────────────────────────────────
    # OUTPut サブシステム
    # ────────────────────────────────────────────

    output_enabled = Instrument.control(
        "OUTP?",
        "OUTP %s",
        """出力リレーのオン／オフを制御します (True=ON / False=OFF)。""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    # ────────────────────────────────────────────
    # MEASure サブシステム (クエリのみ)
    # ────────────────────────────────────────────

    measured_voltage = Instrument.measurement(
        "MEAS:VOLT?",
        """出力電圧実効値を Vrms 単位で返します。""",
        cast=float,
    )

    measured_voltage_peak_high = Instrument.measurement(
        "MEAS:VOLT:HIGH?",
        """出力電圧の最大ピーク値を Vpk 単位で返します。""",
        cast=float,
    )

    measured_voltage_peak_low = Instrument.measurement(
        "MEAS:VOLT:LOW?",
        """出力電圧の最小ピーク値を Vpk 単位で返します。""",
        cast=float,
    )

    measured_voltage_average = Instrument.measurement(
        "MEAS:VOLT:AVE?",
        """出力電圧平均値を V 単位で返します。""",
        cast=float,
    )

    measured_current = Instrument.measurement(
        "MEAS:CURR?",
        """出力電流実効値を Arms 単位で返します。""",
        cast=float,
    )

    measured_current_peak_high = Instrument.measurement(
        "MEAS:CURR:HIGH?",
        """出力電流の最大ピーク値を Apk 単位で返します。""",
        cast=float,
    )

    measured_current_peak_low = Instrument.measurement(
        "MEAS:CURR:LOW?",
        """出力電流の最小ピーク値を Apk 単位で返します。""",
        cast=float,
    )

    measured_current_average = Instrument.measurement(
        "MEAS:CURR:AMPL?",
        """出力電流平均値を A 単位で返します。""",
        cast=float,
    )

    measured_current_crest_factor = Instrument.measurement(
        "MEAS:CURR:CRES?",
        """出力電流のクレストファクタ（波高率）を返します。""",
        cast=float,
    )

    measured_power = Instrument.measurement(
        "MEAS:POW:AC?",
        """有効電力を W 単位で返します。""",
        cast=float,
    )

    measured_apparent_power = Instrument.measurement(
        "MEAS:POW:AC:APP?",
        """皮相電力を VA 単位で返します。""",
        cast=float,
    )

    measured_reactive_power = Instrument.measurement(
        "MEAS:POW:AC:REAC?",
        """無効電力を var 単位で返します。""",
        cast=float,
    )

    measured_power_factor = Instrument.measurement(
        "MEAS:POW:AC:PFAC?",
        """出力力率を返します (0.00～1.00)。""",
        cast=float,
    )

    measured_frequency = Instrument.measurement(
        "MEAS:FREQ?",
        """外部同期信号周波数を Hz 単位で返します (外部同期モード専用)。""",
        cast=float,
    )

    # ────────────────────────────────────────────
    # DISPlay サブシステム
    # ────────────────────────────────────────────

    display_measure_mode = Instrument.control(
        "DISP:MEAS:MODE?",
        "DISP:MEAS:MODE %s",
        """計測表示モードを設定／取得します。
        RMS / AVG / PEAK / HC1 / HC2 / HC3 / HC4 から選択。
        高調波電流計測 (HC1～HC4) は AC-INT 50/60Hz 時のみ有効。""",
        validator=strict_discrete_set,
        values=["RMS", "AVG", "PEAK", "HC1", "HC2", "HC3", "HC4"],
    )

    # ────────────────────────────────────────────
    # INPut サブシステム
    # ────────────────────────────────────────────

    input_gain = Instrument.control(
        "INP:GAIN?",
        "INP:GAIN %g",
        """外部信号入力のゲインを設定／取得します。
        100V レンジ: 0.0～220.0 / 200V レンジ: 0.0～440.0
        AC-EXT / AC-ADD / AC+DC-EXT / AC+DC-ADD モード専用。""",
        validator=truncated_range,
        values=[0.0, 440.0],
    )

    # ────────────────────────────────────────────
    # SYSTem サブシステム
    # ────────────────────────────────────────────

    beeper_enabled = Instrument.control(
        "SYST:BEEP:STATe?",
        "SYST:BEEP:STATe %s",
        """ビープ音のオン／オフを制御します (True=ON / False=OFF)。""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    ext_io_enabled = Instrument.control(
        "SYST:CONF:EXTIO?",
        "SYST:CONF:EXTIO %s",
        """外部制御入力の有効／無効を制御します (True=ON / False=OFF)。""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    power_on_output = Instrument.control(
        "SYST:PON?",
        "SYST:PON %s",
        """電源投入時の出力状態を設定／取得します (True=ON / False=OFF)。""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    sequence_time_unit = Instrument.control(
        "SYST:TUN?",
        "SYST:TUN %d",
        """シーケンスステップ実行時間の単位を設定／取得します (0=s / 1=ms)。""",
        validator=strict_discrete_set,
        values=[0, 1],
        cast=int,
    )

    # ────────────────────────────────────────────
    # SEQuence サブシステム
    # ────────────────────────────────────────────

    sequence_condition = Instrument.measurement(
        "SEQ:COND?",
        """シーケンスの状態を返します (0=Idle / 1=Run / 2=Hold)。""",
        cast=int,
    )

    sequence_current_step = Instrument.measurement(
        "SEQ:CST?",
        """実行中のステップ番号を返します (-1=Idle)。""",
        cast=int,
    )

    sequence_step = Instrument.control(
        "SEQ:STEP?",
        "SEQ:STEP %d",
        """シーケンス編集対象のステップ番号を設定／取得します (1～255)。""",
        validator=strict_range,
        values=[1, 255],
        cast=int,
    )

    # ────────────────────────────────────────────
    # PROGram サブシステム (シーケンス実行制御)
    # ────────────────────────────────────────────

    sequence_execute = Instrument.setting(
        "PROG:EXEC %s",
        """シーケンス動作を制御します。
        STOP / START / HOLD / BRANCH0 / BRANCH1 から選択。
        出力オン中、かつ AC/AC+DC-INT モード時のみ使用可能。""",
        validator=strict_discrete_set,
        values=["STOP", "START", "HOLD", "BRANCH0", "BRANCH1"],
    )

    # ────────────────────────────────────────────
    # 共通コマンド
    # ────────────────────────────────────────────

    def reset(self):
        """機器をリセットして工場出荷時設定に戻します (*RST)。
        出力オン中は実行できません。"""
        self.write("*RST")

    def clear(self):
        """ステータスレジスタ・エラーキューをクリアします (*CLS)。"""
        self.write("*CLS")

    @property
    def id(self):
        """機器の識別情報を返します (メーカー, 型名, 製造番号, FWバージョン)。"""
        return self.ask("*IDN?")

    @property
    def error(self):
        """エラーキューから最新のエラーを読み取ります。
        Returns:
            tuple: (エラーコード: int, エラーメッセージ: str)
        """
        response = self.ask("SYST:ERR?")
        parts = response.split(",", 1)
        code = int(parts[0].strip())
        msg = parts[1].strip().strip('"') if len(parts) > 1 else ""
        return code, msg

    def check_errors(self):
        """エラーキューを全て読み取り、エラーがあれば Exception を送出します。"""
        errors = []
        while True:
            code, msg = self.error
            if code == 0:
                break
            errors.append(f"[{code}] {msg}")
        if errors:
            raise Exception("EC750SA エラー: " + " / ".join(errors))

    def save(self, memory: int):
        """現在の設定を指定メモリ番号 (1～30) に保存します (*SAV)。"""
        if not 1 <= memory <= 30:
            raise ValueError("メモリ番号は 1～30 の範囲で指定してください。")
        self.write(f"*SAV {memory}")

    def recall(self, memory: int):
        """指定メモリ番号 (1～30) の設定を読み出します (*RCL)。
        出力オン中は実行できません。"""
        if not 1 <= memory <= 30:
            raise ValueError("メモリ番号は 1～30 の範囲で指定してください。")
        self.write(f"*RCL {memory}")

    def wait(self):
        """全オペレーション完了まで機器を待機させます (*WAI)。"""
        self.write("*WAI")

    def self_test(self):
        """セルフテストを実行します (*TST?)。本器では常に 0 を返します。"""
        return int(self.ask("*TST?"))

    # ────────────────────────────────────────────
    # ヘルパーメソッド
    # ────────────────────────────────────────────

    def shutdown(self):
        """出力をオフにして安全状態にします。"""
        self.output_enabled = False

    def configure_ac(
        self,
        voltage: float,
        frequency: float,
        voltage_range: int = 100,
        waveform: str = "SIN",
    ):
        """AC 出力の基本パラメータを一括設定します。

        Args:
            voltage:       出力電圧 [Vrms]
            frequency:     出力周波数 [Hz]
            voltage_range: 電圧レンジ (100 または 200)
            waveform:      波形 ("SIN" / "SQU" / "ARB1"～"ARB16")
        """
        self.output_enabled = False  # 設定変更前に出力オフ
        self.voltage_range = voltage_range
        self.mode = "AC-INT"
        self.waveform = waveform
        self.frequency = frequency
        self.voltage = voltage

    def measure_all(self) -> dict:
        """主要計測値をまとめて取得して辞書で返します。

        Returns:
            dict: キー = 物理量名, 値 = 計測値
        """
        return {
            "voltage_rms_V":      self.measured_voltage,
            "current_rms_A":      self.measured_current,
            "power_W":            self.measured_power,
            "apparent_power_VA":  self.measured_apparent_power,
            "reactive_power_var": self.measured_reactive_power,
            "power_factor":       self.measured_power_factor,
            "crest_factor":       self.measured_current_crest_factor,
        }

    def reset_current_peak_hold(self):
        """出力電流ピーク値ホールドを 0 Apk にリセットします。"""
        self.write("MEAS:CURR:AMPL:RES 1")

    def release_warning(self):
        """ワーニングを解除します (全ワーニング要因がクリアされている必要があります)。"""
        self.write("SYST:WREL 1")

    def clear_sequence(self):
        """選択中のシーケンスメモリをクリアします。"""
        self.write("SEQ:DEL 1")

    def get_waveform_catalog(self) -> list:
        """利用可能な波形名称のリストを返します。

        Returns:
            list[str]: 波形名称のリスト (例: ["SIN", "SQU", "ARB1", ...])
        """
        response = self.ask("TRAC:CAT?")
        return [w.strip() for w in response.split(",")]
