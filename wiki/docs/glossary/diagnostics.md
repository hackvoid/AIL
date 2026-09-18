# Diagnostics

## CDD / ODX / PDX — *Diagnostic Descriptions*

Standardized database formats that describe an ECU's full diagnostic capability — all DTCs, DIDs, routines, and sessions.

- CDD: CANdela Studio's native format (Vector-specific)
- ODX (ASAM MCD-2D): open standard, importable into CANoe
- PDX: packaged ODX (.pdx = zipped ODX folder)
- CANoe's DiVa auto-generates test cases from CDD/ODX descriptions
- Always match CDD version to ECU SW version — mismatches cause NRC errors

## DoIP — *Diagnostics over IP — ISO 13400*

Tunnels UDS messages over Ethernet (UDP/TCP). Required for high-bandwidth diagnostics in Ethernet-enabled vehicles and during ECU programming over IP.

- Vehicle announcement: UDP port 13400, ECU broadcasts its logical address
- Activation request (TCP) before sending diagnostic messages
- Logical address replaces CAN ID as the ECU identifier
- CANoe supports DoIP natively with Ethernet hardware (e.g. VN5640)

## DTC — *Diagnostic Trouble Code*

A standardized fault code stored in an ECU's non-volatile memory when a monitored function fails or goes out of range. The core output of OBD-II and UDS diagnostics.

- Format: P0xxx (Powertrain), B0xxx (Body), C0xxx (Chassis), U0xxx (Network)
- Read with UDS service 0x19 (ReadDTCInformation)
- Each DTC has a status byte: confirmed, pending, test failed this cycle
- Freeze frame data is often stored alongside the DTC

## DTC Status Byte — *ISO 14229-1 §11*

An 8-bit mask that tells you the lifecycle state of a DTC — not just whether a fault exists, but how it behaved over drive cycles.

- Bit 0: testFailed — fault active RIGHT NOW
- Bit 1: testFailedThisMonitoringCycle
- Bit 3: confirmedDTC — failed in ≥2 drive cycles (usually)
- Bit 6: testNotCompletedThisMonitoringCycle
- Bit 7: warningIndicatorRequested (MIL on)
- Always check the full byte — a cleared DTC can still have Bit 4 set (pendingDTC)

## Freeze Frame — *Snapshot Data*

A snapshot of key ECU parameters (speed, RPM, load, temperature) captured at the moment a DTC is triggered. Invaluable for root-cause analysis.

- Read via UDS 0x19 subfunction 0x04 (reportDTCSnapshotRecordByDTCNumber)
- OBD-II mandates freeze frames for emissions-related DTCs (Mode $02)
- Each OEM defines which signals go into freeze frames
- In CANoe DIAgnosis, freeze frame data appears as decoded parameter records

## KWP2000 — *Keyword Protocol 2000 — ISO 14230*

The predecessor to UDS. Still found in legacy ECUs, especially pre-2008 vehicles. Similar session/service model but different framing.

- Physical layer: K-Line (single wire, not CAN)
- Services similar to UDS but different SIDs (e.g. ReadDataByLocalID vs 0x22)
- Largely superseded — but you'll encounter it in HIL rigs with legacy ECUs

## OBD-II / WWH-OBD — *On-Board Diagnostics*

Legislated emissions diagnostics accessible to any generic scan tool. OBD-II is the US standard; WWH-OBD (ISO 27145) is the European evolution using UDS over CAN.

- Mode 0x01: Current data (PIDs like 0x0C = RPM, 0x0D = speed)
- Mode 0x02: Freeze frame data
- Mode 0x03: Confirmed DTCs
- Mode 0x07: Pending DTCs
- Mode 0x09: Vehicle info (VIN, CALID, CVN)
- Pin 6 (CAN-H) + Pin 14 (CAN-L) on OBD-II connector → diagnostic bus

## Security Access (0x27) — *Seed-Key Algorithm*

A challenge-response handshake that unlocks restricted ECU functions (write data, flash programming, clear protected DTCs).

- Request seed: 0x27 0x01 → ECU returns a random seed value
- Client computes key from seed using a shared algorithm (OEM-specific)
- Send key: 0x27 0x02 + computed key → ECU unlocks if correct
- Typical lockout: 3 failed attempts → ECU locks for N minutes
- Vector CANoe handles seed-key via DLL plugins (CDD/ODX import)

## UDS — *Unified Diagnostic Services — ISO 14229*

The dominant diagnostic protocol in modern automotive ECUs. A request-response framework over CAN, LIN, FlexRay, or Ethernet.

- Runs over transport layer: ISO 15765-2 (CAN TP) or DoIP (Ethernet)
- Key services: 0x10 (Session), 0x11 (Reset), 0x14 (Clear DTCs), 0x19 (Read DTCs), 0x22 (Read Data), 0x2E (Write Data), 0x27 (Security Access), 0x31 (Routine), 0x34-0x37 (Programming)
- Sessions: Default (0x01), Extended (0x03), Programming (0x02)
- Negative responses: 0x7F + SID + NRC (e.g. 0x22 = conditionsNotCorrect)
