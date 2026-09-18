# Signals & Troubleshooting

## ABS / ESP Intervention — *Vehicle Stability Control*

Brake and stability systems intervene when wheel slip, yaw instability, or traction loss is detected.

- ESP can request engine torque reduction from ECM
- Yaw estimation combines steering angle, wheel speed, and IMU data
- ABS pulsation occurs from brake pressure modulation
- Sensor plausibility checks are critical
- Network timing synchronization matters for stability control

## CAN Communication Failure — *Network Timeout Analysis*

ECUs stop receiving required network messages, causing DTCs, fallback modes, and cascading failures.

- Most ECUs expect cyclic alive messages
- Timeouts trigger substitute values or degraded operation
- Gateway ECUs isolate domains and route traffic
- Bus-off states indicate severe CAN errors
- Signal invalidation strategies vary by OEM

## Low Power / Limp Mode — *Torque Limitation Analysis*

Vehicle enters reduced-power mode because one or more ECUs intentionally limit torque output to protect the drivetrain, emissions system, turbocharger, transmission, or engine.

- Primary symptom: accelerator pedal increases but engine torque request stays capped
- ECM may ignore driver torque request due to protection strategies
- Transmission ECU can request torque reduction during faults or overheating
- ESP/ABS can reduce torque during traction events
- Hybrid systems may reduce combustion torque when HV faults exist
- Limp mode often sets maximum RPM and disables boost pressure
- Always compare: Driver Demand Torque vs Delivered Torque vs Torque Limiter

## Misfire Detection — *Combustion Stability Monitoring*

ECM detects uneven crankshaft acceleration caused by incomplete or unstable combustion events.

- Misfires are typically detected through crankshaft speed fluctuation analysis
- Persistent misfires trigger catalyst protection torque reduction
- Severe misfires can disable injectors to prevent catalyst damage
- Cylinder-specific counters are usually available via DID or measurement variables
- Misfire monitoring may disable during cold start or high load

## No Start Condition — *Crank / No Crank Diagnosis*

Engine fails to start due to electrical, immobilizer, fuel, ignition, synchronization, or communication issues between powertrain ECUs.

- Differentiate between no-crank and crank-no-start immediately
- Starter activation usually requires BCM + immobilizer + ECM agreement
- ECM requires valid crankshaft synchronization before injection
- Fuel pressure and spark enable conditions must both pass
- CAN communication failure can block start authorization
- Many OEMs route start authorization through BCM or gateway ECU

## Sensor Plausibility Fault — *Cross-Signal Validation*

ECU compares multiple sensors representing the same physical behavior and flags implausible combinations.

- Used extensively for safety-critical systems
- Pedal sensors usually have inverse redundancy channels
- Throttle position often cross-checked against airflow
- Transmission and wheel speeds are cross-correlated
- Sensor fusion failures can trigger limp mode

## Transmission Shift Harshness — *TCM Shift Quality Analysis*

Improper clutch pressure control or torque coordination causes rough gear changes, flare, or delayed shifts.

- Modern transmissions coordinate heavily with ECM torque reduction
- Shift quality depends on hydraulic pressure timing
- Slip calculations compare input/output shaft speeds
- Thermal protection strategies alter shift behavior
- CAN delays can destabilize coordinated shifts

## Turbo Underboost / Overboost — *Boost Pressure Regulation*

Turbocharger boost pressure deviates from commanded target due to airflow restriction, actuator issues, leaks, or control instability.

- Desired boost and actual boost should track closely under steady acceleration
- Overboost may trigger immediate torque intervention
- Wastegate and VGT actuators are heavily monitored
- Boost diagnostics depend on barometric compensation
- Underboost often produces black smoke in diesel systems
