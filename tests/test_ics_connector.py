"""Транспорт стенда: разбор телеметрии и отправка команд.

На проводе чистый JSON (подтверждено разработчиком стенда), поэтому никакого кадрирования здесь
быть не должно. Сокет инжектируется, тесты не открывают портов и не зависят от сети.
"""

import json
import socket
from dataclasses import fields

import pytest

from ismpu.io.ics_connector import (
    ICSBenchConnector, ICSInputs, ICSOutputs, ControlModeState, GearState, ResilientSender,
)

BENCH_ADDR = ("127.0.0.1", 3030)


def _full_payload(**overrides) -> dict:
    """Полный набор полей ICSInputs — стенд обязан прислать их все."""
    payload = {}
    for f in fields(ICSInputs):
        if f.name.endswith("Status"):
            payload[f.name] = int(GearState.DownLock)
        elif f.type is int or f.name.endswith(("Valid", "WeightOnWheels")):
            payload[f.name] = 1
        else:
            payload[f.name] = 0.0
    payload.update(overrides)
    return payload


class _FakeSocket:
    """Минимальный UDP-сокет: очередь входящих датаграмм + журнал отправленных."""

    def __init__(self, incoming=()):
        self.incoming = list(incoming)
        self.sent = []
        self.closed = False

    def settimeout(self, _t):
        pass

    def recvfrom(self, _size):
        if not self.incoming:
            raise socket.timeout
        return self.incoming.pop(0)

    def sendto(self, packet, addr):
        self.sent.append((packet, addr))
        return len(packet)

    def close(self):
        self.closed = True


def _connector(incoming=(), **kwargs):
    sock = _FakeSocket(incoming)
    conn = ICSBenchConnector("127.0.0.1", 3030, sock=sock, **kwargs)
    return conn, sock


# --------------------------------------------------------------------------- #
# Разбор телеметрии: совместимость вперёд
# --------------------------------------------------------------------------- #

def test_parses_a_complete_payload():
    inputs = ICSInputs.from_dict(_full_payload(GroundSpeed=72.5))
    assert inputs.GroundSpeed == 72.5
    assert inputs.NoseGearStatus is GearState.DownLock


def test_unknown_fields_are_ignored():
    """Стенд может добавить сигнал — нас это ронять не должно (аналог дописывания полей)."""
    inputs = ICSInputs.from_dict(_full_payload(SomeFutureSignal=42, AnotherOne="x"))
    assert not hasattr(inputs, "SomeFutureSignal")
    assert inputs.GroundSpeed == 0.0


def test_missing_fields_raise_instead_of_defaulting_to_zero():
    """Подставить ноль значило бы выдумать телеметрию, по которой считается управление."""
    payload = _full_payload()
    del payload["GroundSpeed"]
    del payload["TrueHeading"]
    with pytest.raises(ValueError) as exc:
        ICSInputs.from_dict(payload)
    assert "GroundSpeed" in str(exc.value) and "TrueHeading" in str(exc.value)


# --------------------------------------------------------------------------- #
# Обмен: чистый JSON, без кадра
# --------------------------------------------------------------------------- #

def test_reads_plain_json():
    raw = json.dumps(_full_payload(GroundSpeed=50.0)).encode()
    conn, _ = _connector([(raw, BENCH_ADDR)])
    inputs = conn.receive_inputs()
    assert inputs is not None and inputs.GroundSpeed == 50.0
    assert conn.send_addr == BENCH_ADDR          # адрес стенда определён автоматически


def test_sends_bare_json_without_any_framing():
    """Стенд делает UTF8.GetString() → JsonConvert. Любые байты перед JSON сломали бы разбор."""
    conn, sock = _connector([(json.dumps(_full_payload()).encode(), BENCH_ADDR)])
    conn.receive_inputs()
    assert conn.send_outputs(ICSOutputs(ControlMode=ControlModeState.Rollout)) is True
    packet, addr = sock.sent[0]
    assert addr == BENCH_ADDR
    assert packet.lstrip()[:1] == b"{"                       # payload начинается сразу с JSON
    assert json.loads(packet.decode("utf-8"))["ControlMode"] == int(ControlModeState.Rollout)


def test_send_without_a_known_address_is_refused():
    conn, sock = _connector()
    assert conn.send_outputs(ICSOutputs()) is False
    assert sock.sent == []


# --------------------------------------------------------------------------- #
# Устойчивость отправки
# --------------------------------------------------------------------------- #

def test_send_errors_are_counted_not_raised(caplog):
    """Windows отдаёт WSAECONNRESET на UDP, если получатель закрыл порт. Ронять цикл нельзя."""
    class _BadSocket(_FakeSocket):
        def sendto(self, _packet, _addr):
            raise OSError(ResilientSender.WINDOWS_CONNRESET, "connection reset")

    sock = _BadSocket([(json.dumps(_full_payload()).encode(), BENCH_ADDR)])
    conn = ICSBenchConnector("127.0.0.1", 3030, sock=sock)
    conn.receive_inputs()
    with caplog.at_level("WARNING"):
        for _ in range(5):
            assert conn.send_outputs(ICSOutputs()) is False
    assert conn.send_error_count == 5
    assert len(caplog.records) == 1        # лог разрежён, а не по записи на каждую ошибку
