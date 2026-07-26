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
        for index, name in requested:
            self._send_rref(index, name, frequency_hz)
        if timeout_s > 0:
            self.wait_for((name for _, name in requested), timeout_s=timeout_s)

    def subscribeDREFs(self, subscribed_drefs, timeout: float = 0.0, **_) -> None:
        """Совместимость с прежним клиентом."""
        for name, frequency in subscribed_drefs:
            self.subscribe((name,), frequency_hz=frequency, timeout_s=0.0)
        if timeout > 0:
            self.wait_for((name for name, frequency in subscribed_drefs if frequency > 0),
                          timeout_s=timeout)

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

    def wait_for(self, datarefs: Iterable[str], *, timeout_s: float) -> None:
        pending = set(datarefs)
        deadline = time.monotonic() + timeout_s
        while pending and time.monotonic() < deadline:
            pending = {name for name in pending if self.value(name) is None}
            if pending:
                time.sleep(0.01)
        if pending:
            raise TimeoutError("X-Plane не ответил на DataRef: " + ", ".join(sorted(pending)))

    def send_dref(self, dataref: str, value: float) -> None:
        encoded = dataref.encode("utf-8")
        if len(encoded) >= 500:
            raise ValueError("имя DataRef длиннее 499 байт")
        packet = struct.pack("<5sf500s", b"DREF\0", float(value), encoded)
        self.sock.sendto(packet, self.address)

    def sendDREF(self, dataref: str, value: float) -> None:
        self.send_dref(dataref, value)

    def send_command(self, command: str) -> None:
        self.sock.sendto(b"CMND\0" + command.encode("utf-8") + b"\0", self.address)

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
            "<4sxidddfff",
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


# Старое публичное имя оставлено для пользовательских скриптов.
XPlaneConnectX = XPlaneConnector
