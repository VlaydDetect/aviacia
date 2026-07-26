"""Неблокирующий UDP-клиент нативного протокола X-Plane 12."""

from __future__ import annotations

import socket
import struct
import threading
import time
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DataRefSample:
    value: float
    timestamp: float


class XPlaneConnector:
    """Одна подписка, один поток приёма и явное освобождение ресурсов."""

    def __init__(
            self,
            ip: str = "127.0.0.1",
            port: int = 49000,
            *,
            sock=None,
            receive_timeout_s: float = 0.2,
            start_receiver: bool = True,
    ) -> None:
        self.address = (ip, int(port))
        self.sock = sock if sock is not None else socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if hasattr(self.sock, "settimeout"):
            self.sock.settimeout(receive_timeout_s)
        self._lock = threading.RLock()
        self._samples: dict[str, DataRefSample] = {}
        self._index_to_dref: dict[int, str] = {}
        self._dref_to_index: dict[str, int] = {}
        self._frequencies: dict[str, int] = {}
        self._next_index = 1
        self._stop = threading.Event()
        self._thread = None
        if start_receiver:
            self._thread = threading.Thread(
                target=self._receive_loop, name="xplane-rref", daemon=True)
            self._thread.start()

    @property
    def current_dref_values(self) -> dict:
        """Совместимое read-only представление старого XPlaneConnectX."""
        with self._lock:
            return {
                name: {"value": sample.value, "timestamp": sample.timestamp}
                for name, sample in self._samples.items()
            }

    def subscribe(
            self,
            datarefs: Iterable[str],
            *,
            frequency_hz: int = 20,
            timeout_s: float = 0.0,
            retry_interval_s: float = 0.5,
    ) -> None:
        requested = []
        with self._lock:
            for name in datarefs:
                if name in self._dref_to_index:
                    index = self._dref_to_index[name]
                else:
                    index = self._next_index
                    self._next_index += 1
                    self._dref_to_index[name] = index
                    self._index_to_dref[index] = name
                requested.append((index, name))
                self._frequencies[name] = int(frequency_hz)
        for index, name in requested:
            self._send_rref(index, name, frequency_hz)
        if timeout_s > 0:
            self.wait_for(
                (name for _, name in requested),
                timeout_s=timeout_s,
                retry_interval_s=retry_interval_s,
            )

    def subscribeDREFs(
            self,
            subscribed_drefs,
            history: float = 0.0,
            timeout: float = 0.0,
            retry_interval: float = 0.5,
            **_,
    ) -> None:
        """Совместимость с прежним клиентом."""
        del history
        requested = tuple(subscribed_drefs)
        with self._lock:
            if not self._dref_to_index:
                self._next_index = 0
        for name, frequency in requested:
            self.subscribe((name,), frequency_hz=frequency, timeout_s=0.0)
        if timeout > 0:
            self.wait_for(
                (name for name, frequency in requested if frequency > 0),
                timeout_s=timeout,
                retry_interval_s=retry_interval,
            )

    def unsubscribe(self, datarefs: Iterable[str] | None = None) -> None:
        with self._lock:
            names = tuple(datarefs) if datarefs is not None else tuple(self._dref_to_index)
            indexed = [(self._dref_to_index.get(name), name) for name in names]
        for index, name in indexed:
            if index is not None:
                self._send_rref(index, name, 0)

    def value(self, dataref: str, *, max_age_s: float | None = None) -> float | None:
        with self._lock:
            sample = self._samples.get(dataref)
        if sample is None:
            return None
        if max_age_s is not None and time.monotonic() - sample.timestamp > max_age_s:
            return None
        return sample.value

    def snapshot(self, *, max_age_s: float | None = None) -> dict[str, float]:
        with self._lock:
            items = tuple(self._samples.items())
        now = time.monotonic()
        return {
            name: sample.value for name, sample in items
            if max_age_s is None or now - sample.timestamp <= max_age_s
        }

    def clear_samples(self) -> None:
        """Discard pre-reload values so readiness cannot use stale telemetry."""
        with self._lock:
            self._samples.clear()

    def wait_for(
            self,
            datarefs: Iterable[str],
            *,
            timeout_s: float,
            retry_interval_s: float = 0.5,
    ) -> None:
        pending = set(datarefs)
        deadline = time.monotonic() + timeout_s
        next_retry = time.monotonic() + max(0.01, retry_interval_s)
        while pending and time.monotonic() < deadline:
            pending = {name for name in pending if self.value(name) is None}
            if pending:
                now = time.monotonic()
                if now >= next_retry:
                    with self._lock:
                        retry = tuple(
                            (self._dref_to_index[name], name, self._frequencies[name])
                            for name in pending
                            if name in self._dref_to_index and name in self._frequencies
                        )
                    for index, name, frequency in retry:
                        self._send_rref(index, name, frequency)
                    next_retry = now + max(0.01, retry_interval_s)
                time.sleep(0.01)
        if pending:
            raise TimeoutError(
                f"X-Plane {self.address[0]}:{self.address[1]} не ответил за "
                f"{timeout_s:.2f} с; отсутствуют DataRef: {', '.join(sorted(pending))}")

    def send_dref(self, dataref: str, value: float) -> None:
        encoded = dataref.encode("utf-8")
        if len(encoded) >= 500:
            raise ValueError("имя DataRef длиннее 499 байт")
        packet = struct.pack('<4sxf500s', b'DREF', float(value), encoded)
        self.sock.sendto(packet, self.address)

    def sendDREF(self, dataref: str, value: float) -> None:
        self.send_dref(dataref, value)

    def send_command(self, command: str) -> None:
        encoded = command.encode("utf-8")
        if len(encoded) >= 500:
            raise ValueError("команда X-Plane длиннее 499 байт")
        self.sock.sendto(
            struct.pack('<4sx500s', b'CMND', encoded),
            self.address,
        )

    def sendCMND(self, command: str) -> None:
        self.send_command(command)

    def reload_aircraft(self) -> None:
        self.send_command("sim/operation/reload_aircraft_no_art")

    def fix_all_systems(self) -> None:
        self.send_command("sim/operation/fix_all_systems")

    def send_position(
            self,
            *,
            lat: float,
            lon: float,
            elevation_m: float,
            roll_deg: float,
            pitch_deg: float,
            heading_true_deg: float,
            aircraft_index: int = 0,
    ) -> None:
        packet = struct.pack(
            '<4sxidddfff',
            b"VEHS",
            int(aircraft_index),
            float(lat),
            float(lon),
            float(elevation_m),
            float(heading_true_deg),
            float(pitch_deg),
            float(roll_deg),
        )
        # X-Plane вычисляет высоту первого VEHS по старой геопозиции.
        self.sock.sendto(packet, self.address)
        self.sock.sendto(packet, self.address)

    def sendPOSI(self, lat, lon, elev, phi, theta, psi_true, ac=0) -> None:
        self.send_position(
            lat=lat, lon=lon, elevation_m=elev, roll_deg=phi, pitch_deg=theta,
            heading_true_deg=psi_true, aircraft_index=ac)

    def sendCTRL(self, lat_control: float, lon_control: float, rudder_control: float, throttle: float, gear: int,
                 flaps: float, speedbrakes: float, park_brake: float) -> None:
        """Send basic controls to the ego aircraft. There are hundreds of DataRefs that provide more fine-grained control. These can be set through the setDREF method.

        Args:
            lat_control (float): Lateral pilot input, i.e., yoke rotation, or side stick left/right position. Ranges from [-1...1].
            lon_control (float): Longitudinal pilot input, i.e., yoke and side stick forward/backward position. Ranges from [-1...1].
            rudder_control (float): Rudder pilor input. Ranges from [-1...1].
            throttle (float): Throttle position. Ranges from [-1...1] with -1 being full reverse thrust, and 1 being full forward thrust.
            gear (int): Requested gear position. 0 corresponds to gear up, and 1 corresponds to gear down.
            flaps (float): Requested flaps position. Ranges from [0...1].
            speedbrakes (float): Requested speedbakes position. Possible values are {-0.5, [0...1]} where -0.5 means the speedbrake is armed, 0 is retracted, and 1 is fully deployed.
            park_brake (float): Requested park brake ratio. Ranged from [0...1]

        Example:
            xpc = XPlaneConnectX()
            xpc.sendCTRL(lat_control=-0.2, lon_control=0.0, rudder_control=0.2, throttle=0.8, gear=1, flaps=0.5, speedbrakes=0, park_brake=0)
        """

        # lateral control
        dref = "sim/cockpit2/controls/yoke_roll_ratio"
        msg = struct.pack('<4sxf500s', b'DREF', lat_control, dref.encode('UTF-8'))
        self.sock.sendto(msg, self.address)

        # longitudinal control
        dref = "sim/cockpit2/controls/yoke_pitch_ratio"
        msg = struct.pack('<4sxf500s', b'DREF', lon_control, dref.encode('UTF-8'))
        self.sock.sendto(msg, self.address)

        # rudder control
        dref = "sim/cockpit2/controls/yoke_heading_ratio"
        msg = struct.pack('<4sxf500s', b'DREF', rudder_control, dref.encode('UTF-8'))
        self.sock.sendto(msg, self.address)

        # throttle
        dref = "sim/cockpit2/engine/actuators/throttle_jet_rev_ratio_all"
        msg = struct.pack('<4sxf500s', b'DREF', throttle, dref.encode('UTF-8'))
        self.sock.sendto(msg, self.address)

        # gear
        dref = "sim/cockpit/switches/gear_handle_status"
        msg = struct.pack('<4sxf500s', b'DREF', gear, dref.encode('UTF-8'))
        self.sock.sendto(msg, self.address)

        # flaps
        # dref = "sim/cockpit2/controls/flap_handle_request_ratio" #this only for X-Plane 12.0+
        dref = "sim/cockpit2/controls/flap_ratio"
        msg = struct.pack('<4sxf500s', b'DREF', flaps, dref.encode('UTF-8'))
        self.sock.sendto(msg, self.address)

        # speedbrakes
        dref = "sim/cockpit2/controls/speedbrake_ratio"
        msg = struct.pack('<4sxf500s', b'DREF', speedbrakes, dref.encode('UTF-8'))
        self.sock.sendto(msg, self.address)

        # park brake
        dref = "sim/cockpit2/controls/parking_brake_ratio"
        msg = struct.pack('<4sxf500s', b'DREF', park_brake, dref.encode('UTF-8'))
        self.sock.sendto(msg, self.address)

    def pause(self, flag: bool) -> None:
        self.send_command("sim/operation/pause_on" if flag else "sim/operation/pause_off")

    def pauseSIM(self, flag: bool) -> None:
        self.pause(flag)

    def inject_rref_packet(self, packet: bytes, *, timestamp: float | None = None) -> None:
        """Разобрать пакет; публично для детерминированных mock-тестов."""
        if packet[:4] != b"RREF" or (len(packet) - 5) % 8:
            return
        received_at = time.monotonic() if timestamp is None else timestamp
        with self._lock:
            for offset in range(5, len(packet), 8):
                index, value = struct.unpack_from("<if", packet, offset)
                name = self._index_to_dref.get(index)
                if name is not None:
                    self._samples[name] = DataRefSample(float(value), received_at)

    def _send_rref(self, index: int, dataref: str, frequency_hz: int) -> None:
        encoded = dataref.encode("utf-8")
        if len(encoded) >= 400:
            raise ValueError("имя DataRef длиннее 399 байт")
        packet = struct.pack("<4sxii400s", b"RREF", int(frequency_hz), int(index), encoded)
        self.sock.sendto(packet, self.address)

    def _receive_loop(self) -> None:
        while not self._stop.is_set():
            try:
                packet, _ = self.sock.recvfrom(16384)
            except (socket.timeout, TimeoutError):
                continue
            except OSError:
                if self._stop.is_set():
                    return
                continue
            self.inject_rref_packet(packet)

    def close(self) -> None:
        if self._stop.is_set():
            return
        try:
            self.unsubscribe()
        finally:
            self._stop.set()
            try:
                self.sock.close()
            finally:
                if self._thread is not None and self._thread.is_alive():
                    self._thread.join(timeout=0.5)

    def __enter__(self) -> "XPlaneConnector":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self.close()
        return False


# Старое публичное имя оставлено для пользовательских скриптов.
XPlaneConnectX = XPlaneConnector
