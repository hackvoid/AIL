# Test Methods

## Fault Injection — *FI*

Deliberately introducing failures to verify that the ECU detects them correctly and responds safely. Core to functional safety (ISO 26262) verification.

- Signal faults: set sensor signal to stuck-at-min, stuck-at-max, out-of-range
- Bus faults: dominant stuck bits, bus-off conditions, missing messages (timeout)
- Hardware faults (HIL): relay open/short circuits on I/O pins
- Verify: correct DTC set, correct fallback behavior, correct MIL state
- CANoe supports fault injection via CAPL or the VT System hardware

## HIL Testing — *Hardware-in-the-Loop*

Real ECU hardware connected to a real-time simulation of the physical plant (engine, vehicle dynamics, sensors, actuators). The most realistic pre-vehicle test environment.

- Real ECU receives simulated sensor inputs; its outputs are captured and fed back
- Fault injection: simulate sensor failures, open circuits, short to ground/battery
- Residual bus simulation: CANoe simulates all other ECUs not under test
- Automation: test scripts run overnight; results compared to expected values
- Tools: Vector VT System (I/O boards) + CANoe + dSPACE or ETAS LABCAR

## P2 / P2* Timing — *Diagnostic Response Timing*

ISO 14229 timing requirements for how fast an ECU must respond to diagnostic requests.

- P2server_max: max time between request and response (default 50ms)
- P2*server_max: max time after NRC 0x78 (ResponsePending) before final response (default 5s)
- NRC 0x78: ECU says 'still working, wait for me'
- Test with DiVa or manual timing checks in CANoe trace
- Violations are a common finding in diagnostic validation

## Residual Bus Simulation — *RBS*

CANoe simulates all CAN/LIN nodes not physically present in the test setup, providing realistic bus traffic to the ECU under test.

- Configured from DBC/LDF: CANoe knows which messages each node should send
- CAPL nodes add behavior: conditional message sending, signal manipulation
- Critical for HIL: ECU must see expected bus activity or it enters safe states/DTCs
- Check symbol mappings: which signals come from real HW vs simulated nodes

## SIL / MIL Testing — *Software/Model-in-the-Loop*

Earlier-stage test methods that validate software or models without physical hardware.

- MIL: Simulink model runs against simulated environment. Tests model logic early.
- SIL: compiled ECU code (not model) runs in a PC simulation environment
- PIL (Processor-in-the-Loop): code runs on target processor, comms via simulator
- Catches functional bugs before expensive HIL or vehicle time
- CANoe can interface with SIL environments via FMI/FMU or VEOS (Vector)

## Test Coverage Metrics — *Requirements Traceability*

Tracking which requirements are covered by which test cases. Mandatory for ISO 26262 / ASPICE compliance.

- Each test case links to ≥1 requirement ID
- Coverage report: % of requirements with at least one passing test
- Test types: black-box (spec-based), white-box (code coverage), grey-box
- Tools: vTESTstudio ↔ DOORS/Polarion/codeBeamer for bidirectional traceability
- ASPICE WP: SWE.4 (software unit verification), SWE.5 (integration test)
