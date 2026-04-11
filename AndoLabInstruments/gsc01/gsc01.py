from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep


class GSC01(Instrument):
    def __init__(self, adapter, name="GSC-01", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            **kwargs
        )

    def initialize(self):
        """Reset logical origin to current position."""
        self.home()

    ############################################
    ### Motion commands
    ############################################

    def home(self):
        """Perform mechanical origin return (H command)."""
        response = self.ask("H:1")
        if response.strip() != "OK":
            raise RuntimeError(f"Home command failed: {response}")

    def move_relative(self, pulses):
        """
        Set relative move distance and execute (M + G command).
        pulses: positive or negative integer, range ±16,777,215
        """
        direction = "+" if pulses >= 0 else "-"
        response = self.ask(f"M:1{direction}P{abs(pulses)}")
        if response.strip() != "OK":
            raise RuntimeError(f"Move relative command failed: {response}")
        response = self.ask("G:")
        if response.strip() != "OK":
            raise RuntimeError(f"Go command failed: {response}")

    def move_absolute(self, pulses):
        """
        Set absolute move position and execute (A + G command).
        pulses: positive or negative integer, range ±16,777,215
        """
        direction = "+" if pulses >= 0 else "-"
        response = self.ask(f"A:1{direction}P{abs(pulses)}")
        if response.strip() != "OK":
            raise RuntimeError(f"Move absolute command failed: {response}")
        response = self.ask("G:")
        if response.strip() != "OK":
            raise RuntimeError(f"Go command failed: {response}")

    def jog(self, direction):
        """
        Start jog operation and execute (J + G command).
        direction: '+' or '-'
        """
        strict_discrete_set(direction, ["+", "-"])
        response = self.ask(f"J:1{direction}")
        if response.strip() != "OK":
            raise RuntimeError(f"Jog command failed: {response}")
        response = self.ask("G:")
        if response.strip() != "OK":
            raise RuntimeError(f"Go command failed: {response}")

    def stop(self):
        """Decelerate and stop (L command)."""
        self.ask("L:1")

    def stop_immediate(self):
        """Immediate stop without deceleration (L:E command)."""
        self.ask("L:E")

    def set_logical_origin(self):
        """Set current position as logical origin (R command)."""
        response = self.ask("R:1")
        if response.strip() != "OK":
            raise RuntimeError(f"Set origin command failed: {response}")

    ############################################
    ### Speed settings
    ############################################

    def set_speed(self, speed_s, speed_f, accel_time):
        """
        Set motion speed parameters (D command).
        speed_s: start speed (PPS), 100-20000, in steps of 100
        speed_f: max speed (PPS), 100-20000, speed_f >= speed_s
        accel_time: acceleration/deceleration time (ms), 0-1000
        """
        response = self.ask(f"D:1S{speed_s}F{speed_f}R{accel_time}")
        if response.strip() != "OK":
            raise RuntimeError(f"Set speed command failed: {response}")

    def set_jog_speed(self, speed):
        """
        Set jog speed (S:J command).
        speed: 100-20000 PPS, in steps of 100
        """
        response = self.ask(f"S:J{speed}")
        if response.strip() != "OK":
            raise RuntimeError(f"Set jog speed command failed: {response}")

    ############################################
    ### Status
    ############################################

    def get_status(self):
        """
        Query stage status (Q command).
        Returns dict with keys: position, command_ok, limit_stop, busy
        """
        response = self.ask("Q:").strip()
        # format: position(10chars), ACK1, ACK2, ACK3
        # e.g. "     +1000,K,K,R"
        parts = response.split(",")
        return {
            "position":     int(parts[0].strip()),
            "command_ok":   parts[1].strip() == "K",
            "limit_stop":   parts[2].strip() == "L",
            "busy":         parts[3].strip() == "B",
        }

    @property
    def position(self):
        """Current position in pulses."""
        return self.get_status()["position"]

    @property
    def is_busy(self):
        """True if stage is moving."""
        response = self.ask("!:").strip()
        return response == "B"

    def wait_for_stop(self, interval=0.05):
        """Block until stage stops moving."""
        while self.is_busy:
            sleep(interval)

    ############################################
    ### Excitation
    ############################################

    def excitation_on(self):
        """Turn motor excitation ON (C command)."""
        response = self.ask("C:11")
        if response.strip() != "OK":
            raise RuntimeError(f"Excitation ON failed: {response}")

    def excitation_off(self):
        """Turn motor excitation OFF (C command)."""
        response = self.ask("C:10")
        if response.strip() != "OK":
            raise RuntimeError(f"Excitation OFF failed: {response}")

    ############################################
    ### Version info
    ############################################

    def get_version(self):
        """Get ROM version (?:V command)."""
        return self.ask("?:V").strip()

    def get_revision(self):
        """Get revision number (?:- command)."""
        return self.ask("?:-").strip()