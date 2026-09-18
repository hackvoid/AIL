# Protocols

## CAN / CAN FD — *Controller Area Network*

The dominant automotive bus. CAN FD (Flexible Data-rate) extends classic CAN to 64-byte payloads and up to 8 Mbit/s data phase speed.

- Classic CAN: max 8 bytes/frame, up to 1 Mbit/s
- CAN FD: up to 64 bytes, data phase up to 8 Mbit/s, nominal up to 1 Mbit/s
- Arbitration: lower ID = higher priority (0x000 wins over 0x7FF)
- Error frames, stuff bits, ACK field — hardware handles automatically
- Monitor with CANalyzer or CANoe; DBC required to decode signals

## FlexRay — *Deterministic High-Speed Bus*

Time-triggered bus for safety-critical applications requiring determinism and redundancy (chassis control, brake-by-wire, steer-by-wire).

- Up to 10 Mbit/s per channel, two redundant channels (A+B)
- Static + dynamic segment: guaranteed slots + flexible slots
- Cycle time is fixed (1–16 ms typical)
- Requires FIBEX description; niche hardware (VN7600 for Vector)

## ISO 15765-2 (CAN TP) — *CAN Transport Protocol*

Segments UDS messages longer than 8 bytes across multiple CAN frames. Handles flow control between tester and ECU.

- Single Frame (SF): payload ≤7 bytes, sent in one CAN frame
- First Frame (FF): starts a multi-frame transfer
- Consecutive Frame (CF): subsequent chunks
- Flow Control (FC): ECU tells tester its buffer size and delay (STmin)
- Block Size (BS) and STmin tuning matters for programming performance

## LIN — *Local Interconnect Network*

Single-wire, low-speed (up to 20 kbit/s) bus used for non-critical body functions. Master sends schedule header, slave responds.

- One master, up to 16 slaves — no arbitration needed
- Used for: windows, mirrors, seats, HVAC controls
- Described by LDF file; monitored in CANalyzer/CANoe
- Common issues: no response (slave dead), checksum errors, schedule violations

## SOME/IP — *Scalable service-Oriented MiddlewarE over IP*

Ethernet-based service-oriented protocol for automotive. ECUs advertise services, other ECUs subscribe. Used in AUTOSAR Adaptive architectures.

- Service Discovery (SOME/IP-SD): ECUs find services at runtime
- Client subscribes to events, server sends on change or periodically
- CANoe + Ethernet hardware monitors SOME/IP natively
- Wireshark (with automotive plugins) is also useful for debugging

## XCP — *Universal Measurement and Calibration Protocol*

The standard protocol for reading and writing ECU memory during runtime. Used by CANape for live calibration and measurement.

- Runs on top of CAN, USB, Ethernet, or SxI
- GET_DAQ_LIST: what signals can I read?
- SET_MTA + DOWNLOAD: write to calibration addresses
- Time-correlation: XCP timestamps sync with logger timestamps
- Replaces older CCP (CAN Calibration Protocol) — but CCP still exists
