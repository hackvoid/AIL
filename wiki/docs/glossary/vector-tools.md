# Vector Tools

## CANalyzer — *Network Analysis Tool*

CANoe's lighter sibling — purely for monitoring and analysis, no simulation capability. Faster to set up for quick debugging sessions.

- Trace, Statistics, Graphics, Data windows
- Cannot simulate nodes (that's CANoe's job)
- CAPL scripting still available for filters and triggers
- Ideal for: signal snooping, error frame hunting, timing analysis

## CANape — *Calibration and Measurement Tool*

The calibration engineer's primary tool. Connects to ECUs via XCP to read live signal values and write calibration parameters in real time.

- Loads A2L + PAR files to know what to measure/calibrate
- Raster (DAQ lists): group signals by measurement rate (1ms, 10ms, 100ms)
- Characteristic maps: visual editor for 2D/3D lookup tables (maps/curves)
- Data logging: saves MDF4 files with all measured signals
- Script engine: automates calibration sequences

## CANdb++ — *Database Editor for DBC/LDF files*

Vector's database editor for creating and maintaining DBC (CAN) and LDF (LIN) files. Every signal used in CANoe/CANalyzer starts here.

- Define message IDs, cycle times, transmitting nodes
- Define signals: bit start, length, byte order (Intel/Motorola), scaling, offset, unit
- Value tables: map raw integers to named states (e.g. 0=Off, 1=On, 2=Error)
- Attribute definitions: add metadata used by CANoe (e.g. GenSigSendType)
- Import/export: .dbc ↔ Excel, .sym, FIBEX

## CANdela Studio — *Diagnostic Description Editor*

Where CDDs are created and maintained. Define every DTC, DID, routine, and session your ECU supports, then export to ODX or import into CANoe.

- Hierarchical: ECU → ECU Variant → Diagnostic Class → DTC/DID
- Generates the CDD consumed by CANoe and DiVa
- Version management: track changes between SW releases
- Variant coding: define which features are present in which ECU variant

## CANoe — *CAN + network simulation & testing*

The flagship Vector tool. Simulates entire vehicle networks, runs CAPL-based test modules, performs automated diagnostics, and logs everything.

- Simulation: replace missing ECUs with CAPL node simulations
- Test module: structured test cases with verdicts (pass/fail/inconclusive)
- Diagnostics window: send UDS requests, read DTCs, view freeze frames
- Trace window: raw bus traffic with DBC decoding
- Supports CAN, CAN FD, LIN, FlexRay, Ethernet, SOME/IP simultaneously

## CANoe DiVa — *Diagnostic Validation*

Add-on to CANoe that auto-generates and executes diagnostic test cases from a CDD/ODX description. Validates an ECU's diagnostic implementation against its spec.

- Generates hundreds of test cases from CDD automatically
- Tests: service availability per session, NRC correctness, timing (P2, P2*)
- Boundary value tests for DID lengths, byte ranges
- Regression-safe: re-run the same tests after every ECU software release

## DIAdem — *Data Analysis & Report Tool (NI)*

National Instruments tool (common alongside Vector suite) for post-processing large MDF measurement files. Not a Vector product but widely used in V&V workflows.

- Loads MDF4 files directly from CANoe/CANape
- DataFinder: indexes and searches across thousands of measurement files
- Analysis scripts: VBAI/Python for automated pass/fail evaluation
- Report generator: auto-produces PDF reports from templates
- Navigator → Workbook → Script → Report: the typical DIAdem workflow

## vTESTstudio — *Test Automation IDE*

Vector's dedicated test automation environment. Write structured test cases in CAPL, C#, or Python and execute them with automated verdicts.

- Test tree: organize test cases into suites, groups, cases, steps
- Verdict system: PASS / FAIL / INCONCLUSIVE with detailed logs
- CAPL-TE: CAPL variant optimized for test (event-driven + sequential)
- Integrates with requirements tools (ALM, DOORS) for traceability
- Generates XML/HTML test reports exportable to JIRA or similar
