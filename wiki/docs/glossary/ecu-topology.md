# ECU Topology

## ADAS / Ethernet Backbone — *High-Bandwidth Sensor Fusion Network*

Automotive Ethernet domain used for cameras, radar, lidar, autonomous functions, and high-bandwidth software architectures.

- Supports SOME/IP and DoIP
- Gigabit bandwidth for sensor streams
- Used heavily in AUTOSAR Adaptive systems
- ADAS ECU performs sensor fusion
- Critical for modern autonomous functions

## Body CAN — *Comfort & Convenience Network*

Handles low-priority body electronics, comfort systems, lighting, locking, HVAC, and operator interfaces.

- Lower speed than powertrain CAN
- BCM is typically the central coordinator
- Heavy use of LIN sub-networks
- Focuses on user interaction and convenience
- Gateway filters traffic between domains

## Chassis CAN — *Vehicle Dynamics Network*

Supports steering, braking, suspension, and stability systems requiring synchronized real-time dynamics data.

- Very timing-sensitive domain
- High interaction with ABS/ESP ECU
- Often integrated with ADAS functions
- Safety-critical communication paths
- Extensive redundancy and plausibility checks

## Gateway ECU — *Central Communication Router*

Routes messages between CAN, LIN, FlexRay, and Ethernet domains while enforcing filtering, security, and diagnostics access.

- Central nervous system of the vehicle network
- Controls diagnostic routing
- Implements firewall/security policies
- Performs network wake-up management
- Bridges low-speed and high-speed domains

## HV Battery / EV Topology — *High Voltage Control Network*

Dedicated EV/hybrid control domain coordinating battery management, inverters, charging, and thermal control.

- Safety-critical isolation monitoring
- Torque requests coordinated with inverter
- Battery thermal control is essential
- HV interlock monitoring always active
- Regenerative braking integrated with ESP

## LIN Subnetwork — *Local Peripheral Network*

Low-speed single-wire network used for smart actuators and sensors controlled by a master ECU.

- One master controls all bus timing
- No arbitration required
- Cheap and lightweight
- Usually attached beneath BCM or door ECU
- Perfect for deterministic low-bandwidth peripherals

## Powertrain CAN — *High-Speed Drivetrain Network*

Primary real-time CAN network responsible for engine, transmission, propulsion, emissions, and torque coordination.

- Usually 500 kbit/s or CAN FD
- Strict timing and deterministic messaging
- Carries torque, RPM, gear, pedal, and thermal signals
- Gateway routes data to body and infotainment domains
- Loss of this network often causes limp mode or no-start
