# Scripting

## CAPL Basics — *CAN Access Programming Language*

C-like scripting language built into all Vector tools. Every automated behavior in CANoe/CANalyzer is written in CAPL.

- Event-driven: on message, on timer, on key, on start, on preStart
- Direct access to bus signals and system variables
- Runs inside the CANoe simulation environment — not a general-purpose language
- Compiled into a .cbf binary; source is .can (for nodes) or .cin (includes)

## CAPL Test Functions — *vTESTstudio / Test Module*

CAPL test functions for writing structured test cases with automatic pass/fail verdicts.

- testStep(): log a named step with PASS/FAIL result
- testWaitForSignalInRange(): block until signal enters expected range (or timeout)
- testExpectSignalMatch(): assert a signal matches a value
- testCaseTitle() / testSuiteBegin(): structure your test tree
- Always handle timeouts — a hanging test is worse than a failing test

## on message / on signal — *CAPL Event Handlers*

Core CAPL event triggers for reacting to bus activity.

- on message 0x1A0: fires on every CAN frame with that ID
- on message EngineData: fires when the named DBC message arrives
- on signal EngineSpeed: fires when the signal value changes
- on envVar: fires when an environment variable changes
- on diagResponse: fires after a UDS diagnostic response is received

## System Variables — *CANoe Global State*

Named variables shared across all CAPL nodes, panels, and test modules in a CANoe configuration. The glue between simulation components.

- Defined in CANoe's System Variable editor (namespace::name)
- Types: int, float, byte array, string
- sysSetVariable() / sysGetVariable() in CAPL
- Panels: bind controls to system variables for operator interaction
- Useful for: mode switches, fault injection triggers, simulation parameters
