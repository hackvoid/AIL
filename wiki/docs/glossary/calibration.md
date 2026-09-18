# Calibration

## Characteristic Map (Map/Curve) — *ECU Lookup Table*

2D or 3D lookup tables in the ECU software that define a function's output based on one or two input axes. Core targets of calibration work.

- Curve: 1 input axis → output values (e.g. throttle angle → torque request)
- Map: 2 input axes → output values (e.g. RPM × load → injection timing)
- Edited live in CANape's graphical map view over XCP
- Changes written to ECU RAM; saved to PAR file; flashed to NVM if needed
- A2L defines the address, axis descriptions, units, and value ranges

## DAQ / STIM — *Data Acquisition / Stimulation*

XCP modes for data flow. DAQ streams signal values from ECU to tool. STIM injects values from tool into ECU (bypassing internal computation).

- DAQ: ECU sends signal values at configured rates (measurement rasters)
- STIM: override ECU internal signals externally — used for bypass/stimulation testing
- Bypass calibration: simulate a sensor or function with external signal source
- In CANape: configure DAQ lists per measurement task; rates from 1ms to 1s

## Flash Programming Sequence — *UDS ECU Update Flow*

The standardized sequence of UDS services used to reflash an ECU with new software.

- 1. Open Programming Session (0x10 0x02)
- 2. Security Access (0x27 seed-key unlock)
- 3. Erase Memory via Routine Control (0x31 0x01 eraseMemory)
- 4. Request Download (0x34) — tell ECU what you're sending
- 5. Transfer Data (0x36) — send blocks of HEX data
- 6. Transfer Exit (0x37) — done sending
- 7. Validate via Routine Control (0x31 checksumVerify)
- 8. ECU Reset (0x11 0x01)

## Measurement Raster — *Task/Rate Configuration*

The time interval at which a signal is sampled and transmitted via XCP. Signals are grouped into rasters matching their dynamics.

- 1ms raster: fast dynamics — injection timing, pressure control loops
- 10ms raster: medium dynamics — engine torque, temperatures (control)
- 100ms raster: slow dynamics — ambient temperature, status flags
- Wrong raster → aliasing or excessive bus load
- CANape lets you drag signals between rasters in the Measurement Setup
