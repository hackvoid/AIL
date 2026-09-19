# RDI Testing — Reading the VF179 Rear Parking Assistance Specification

Welcome to one of the most practical skills in this bootcamp: turning a
requirements document into real tests. In this article you'll work with a
genuine **Vehicle Function (VF) specification** — VF179, *Rear Parking
Assistance* for the P332 battery-electric platform (Edition 2, Revision A) —
the same document the RDI Testing lessons use as their reference. Every
diagnostic exercise you'll meet later (missing messages, plausibility checks,
Unified Diagnostic Services) starts from a requirement in VF179 and ends as a
stimulus you apply on the bench and a behavior you observe.

By the end of this article you'll be able to:

- navigate a VF document and know exactly which section answers which testing
  question,
- find the signals to stimulate, the states to observe, the timing parameters
  to respect, and the diagnostic trouble codes (DTCs) to expect,
- read the PAM state machine fluently enough to design your own test cases.

Don't worry about memorizing everything — the goal is to learn *where to
look*, so the document becomes your ally rather than a wall of text.

## What a VF document contains

A VF document describes one vehicle feature end to end, across all the
electronic control units (ECUs) that cooperate to deliver it. VF179 follows
the standard Stellantis template, and each section answers a question you will
actually ask on the job:

| Section | Content | Question it answers for you |
|---|---|---|
| Vehicle Function Data | Area (Driving Assistance), owner, revision notes | "Which change request altered which requirement?" |
| Functional Diagram | Block diagram of ECUs, devices and signals | "What do I wire up or simulate on the bench?" |
| External Interfaces / I/O / Signal | Every input and output, grouped by physical channel (hardwire, LIN, B/BH-CAN, C-CAN) | "What are the exact message and signal names for CANoe/CANalyzer?" |
| Indication | Telltales and messages shown to the driver | "What should I check on the cluster?" |
| Working Conditions | Ignition states in which the function is active | "What are the preconditions of my test case?" |
| Functional Requirements | The algorithm: variables, state machine, per-ECU rules | "What behavior do I verify?" |
| Diagnosis and Recovery | Diagnosis table + fault-by-fault recovery rules | "Which faults do I inject, and which DTCs should appear?" |
| Configuration Parameters | Named tunable values with default, range, resolution, unit | "What are the concrete thresholds and debounce times?" |

## Meet the four ECUs

Everything in VF179 revolves around four control units. Get friendly with
them now — you'll be stimulating and observing them constantly:

- **PAM** (Park Assist Module) — the brain. It owns the algorithm and the
  three ultrasonic sensors in the rear bumper (left, central, right).
- **BCM** (Body Control Module) — the gateway. It forwards the PAM button
  press over LIN (Local Interconnect Network) and drives the button LED, with
  day and night variants.
- **IPC** (Instrument Panel Cluster) — the driver's display. It shows the car
  graphic with distance arcs and plays the acoustic chimes.
- **LSS** — acquires the physical Park Assist on/off switch.

## System purpose and signal flow

The system's job is simple to state: warn the driver about obstacles behind
the vehicle while parking — including obstacles outside the driver's field of
view — through **visual signals** (arcs on the cluster display) and
**acoustic signals** (chimes whose pulse rate depends on distance). Here's how
the information flows:

```mermaid
flowchart LR
    subgraph HW["Hardwired devices"]
        SENS["Rear bumper sensors ×3"]
        SW["Park Assist switch"]
        HK["Trailer hook sensor"]
        LED["Button LED"]
    end
    SENS --> PAM
    HK -->|"Trailer.Info"| PAM
    SW --> LSS -->|"Park_Assist_On_Off.Req"| BCM
    BCM -->|"LIN_BCM_IGW1.PAMRequestSts"| PAM
    VEH["Brake & transmission ECUs"] -->|"C-CAN: BRAKE1, BRAKE4, TRANSM2"| PAM
    PAM -->|"STATUS_PAM / PARK_INFO"| IPC["IPC cluster"]
    PAM -->|"PAM_LedControlSts"| BCM -->|"LedControlSts.Req"| LED
```

Notice how the document groups interfaces by channel — this is exactly how
you'll set up your tools:

| Channel | Signals | Direction |
|---|---|---|
| Hardwire | `Trailer.Info`, `LedControlSts.Req`, `Park_Assist_On_Off.Req` | device ↔ PAM/BCM |
| LIN | `LIN_BCM_IGW1.PAMRequestSts` (button press) | BCM → PAM |
| B/BH-CAN | `PARK_INFO.*` (arcs, chime requests, display activation), `STATUS_PAM.*` (system status, fault, LED request), `BH_IGW1.PamAlertMode`, `STATUS_TELEMATIC.AudioSts_Telematic` | PAM → IPC/BCM |
| C-CAN | `BRAKE1.VehicleSpeedVSOSig` (+`FailSts`), `BRAKE4.VehicleStandStillSts`, `TRANSM2.ShiftLeverPosition` | vehicle → PAM |

One more thing to know before diving into the logic: two **PROXI parameters**
(the vehicle's configuration bytes) gate entire branches of it. `CAN node 24
(PAM)` must be `Present` for the BCM/IPC requirements to apply at all, and
`Gear_Box_Type` different from `MTX` enables the gear-lever-based reverse
detection. Other PROXI parameters (`PAM_Configuration`, `PAM_Tuning_Set`,
`Vehicle_Line_Configuration`) select the parameter set for the vehicle model.

## Preconditions: the PAM internal variables

Before the state machine makes sense, you need the handful of variables
everything else depends on. Think of these as the vocabulary of the document:

- **Reverse Condition** — true when `Gear_Box_Type ≠ MTX` and
  `TRANSM2.ShiftLeverPosition` stays equal to `"R"` for longer than
  `TReverseGear` (**400 ms**).
- **Standstill Condition** — true when `BRAKE4.VehicleStandStillSts` is `"True"`.
- **KEY ON / KEY OFF** — buckets of ignition states: KEY ON covers
  `Ignition_ON`, `Ignition_Start`, `Ignition_ON_Engine_ON`; KEY OFF covers
  `Ignition_OFF` and `Initialization`.
- **MODE_PAM** — the last user-selected activation state (`ON`/`OFF`), stored
  in non-volatile memory (NVM) at every change; the power-on default is `OFF`.
- **PAMFault** — a latched failure flag (`TRUE`/`FALSE`), also stored in NVM
  at every change.

## The PAM state machine

This is the heart of the document — and, for you, the richest single source of
test cases. Take your time with it; every arrow here is a scenario waiting to
be verified:

```mermaid
stateDiagram-v2
    [*] --> KEY_OFF
    KEY_OFF --> KEY_ON: ignition → ON / Start / Engine_ON
    KEY_ON --> KEY_OFF: ignition → OFF / Initialization
    state KEY_ON {
        [*] --> ON_Enable: MODE_PAM = ON, PAMFault = FALSE
        [*] --> OFF: MODE_PAM = OFF, PAMFault = FALSE
        [*] --> Disable: PAMFault = TRUE
        state ON_Enable {
            [*] --> ON_Inactive
            ON_Inactive --> ON_Active: Reverse Condition true
            ON_Active --> ON_Inactive: Reverse Condition false
        }
        ON_Enable --> Disable: overspeed in reverse / trailer present / fault
        ON_Enable --> OFF: button pressed
        Disable --> ON_Enable: cause healed, PAMFault = FALSE
        Disable --> OFF: button pressed, PAMFault = FALSE
        OFF --> ON_Enable: button pressed, PAMFault = FALSE
        OFF --> Disable: button pressed, PAMFault = TRUE
    }
```

What makes this testable is that each state announces itself on the bus.
Here's what you can actually observe:

- Entering **KEY ON**, PAM initializes, resets all `STATUS_PAM`/`PARK_INFO`
  signals to defaults except `STATUS_PAM.PAMSystemSts = "ON_Inactive"`, and
  **ignores the shift lever signal for `TFilter` (100 ms)**, treating it as
  `"P"`. Then it reloads `MODE_PAM`/`PAMFault` from NVM and jumps to
  `ON_Enable`, `OFF` or `Disable` accordingly.
- **ON_Inactive**: `PAMSystemSts = "ON_Inactive"`, `RearSensorSts = "Active"`,
  LED off, display not active.
- **ON_Active**: `PAMSystemSts = "ON_Active"`, `DisplayActivation = "Active"`,
  and the `PARK_INFO` signals follow the visual alert table.
- **Disable**: `PAMSystemSts = "ON_Disabled"`, LED on (continuous);
  `PAMAboveSpeed = "True"` only when the cause was exceeding `SPEED_LIMIT`
  while in reverse.
- **OFF**: `PAMSystemSts = "OFF"`, LED on (continuous).

Two transitions deserve special attention when you design tests:

1. **Overspeed** — in `ON_Enable`, if `BRAKE1.VehicleSpeedVSOSig` exceeds
   **SPEED_LIMIT (11 km/h)** while the Reverse Condition holds, PAM moves to
   `Disable`. Dropping back below the limit (with no fault) returns it to
   `ON_Enable`. That boundary at 11 km/h is a classic test point.
2. **Button in Disable with an active fault** — PAM stays in `Disable` and
   the LED blinks for `PAM_LED_BLINK_TIME`, then goes back to continuous
   light. With no fault, the same press moves PAM to `OFF`. Same stimulus,
   two different expected behaviors — a great test case.

!!! note "Why NVM persistence matters for testing"
    Because `MODE_PAM` and `PAMFault` are stored in non-volatile memory at
    every change of state, a key cycle is itself a test stimulus: induce a
    fault, switch KEY OFF/ON, and verify PAM powers up directly in `Disable`.
    A correct ECU must not "forget" the fault across ignition cycles.

## Alerts: arcs, chimes and special cases

In `ON_Active`, PAM requests acoustic feedback per zone through the two rear
speakers. The logic is refreshingly simple:

| Obstacle zone | `ChimeActivation_LHR` | `ChimeActivation_RHR` |
|---|---|---|
| Rear left | Active | Not Active |
| Rear central | Active | Active |
| Rear right | Not Active | Active |

The chime repetition rate varies **linearly with obstacle distance**, between
`REP_MIN_DURATION` (0 ms) and `REP_MAX_DURATION` (375 ms). A value of 0 means
a **continuous tone** — you're against the obstacle, so stop! `ChimeType_Rear`
is fixed to `"Type4"`.

The special cases are where sloppy systems misbehave — and where sharp testers
shine:

- **Wall detection** — if both outer sensors report a wall-shaped obstacle
  continuously for more than `Tpamwalldet` (**3 s**), the acoustic feedback is
  deactivated while the obstacle persists. Otherwise reversing along a wall
  would chime non-stop.
- **Multiple obstacles, same zone** — only the nearest one is signalled.
- **Multiple obstacles, different zones** — the nearest one overall is
  signalled.
- **Moving obstacle at standstill** — if the vehicle is stationary and an
  obstacle sweeps across two consecutive arcs, warnings follow the closest
  position unless the obstacle stays in a different zone continuously for
  `T_Filter_Alerts` (**100 ms**).

On the BCM side, the LED request from PAM is translated into day/night
variants using `InternalLightSts`: continuous or blinking light, with blinking
at `PAM_LED_BLINK_DUTY` (**50 %**) and `PAM_LED_BLINK_FREQ` (**2 Hz**).

## Diagnosis and recovery

Now for the section you'll use most in the exercises. The diagnosis table has
**20 entries (IDs 1.0–20.0)**, each binding a fault to the ECU that detects
it, the enabling ignition condition, and the fault signal it sets. All of them
are active only with ignition `ON` or engine running.

### Faults detected by PAM

| ID | Fault | Type | Fault signal |
|---|---|---|---|
| 1.0 | Sensor short/open circuit (any of the 3) | electrical | `PAMSystemFault` |
| 2.0 | PAM internal failure | internal | `PAMSystemFault` |
| 3.0 | `BRAKE1` missing message | missing message | `PAMSystemFault` |
| 5.0 | `PAM_OperationalModeSts.Info` = SNA | plausibility | `PAMSystemFault` |
| 6.0 | Sensor blockage (vehicle speed between `Min_Speed` 2 and `Max_Speed` 50 km/h) | plausibility | `RearSensorSts = "Not_Active_Blocked"` |
| 8.0 / 9.0 | `LIN_BCM_IGW1` / `BH_IGW1` missing message | missing message | `PAMSystemFault` |
| 10.0 | `PAMRequestSts` stuck "Pressed" beyond `PAM_STUCK_TIMEOUT` (**15 s**) | plausibility | `PAMSystemFault` |
| 11.0 | `VehicleSpeedVSOSig` = SNA or `FailSts` = "Fail Present" | plausibility | `PAMSystemFault` |
| 12.0 / 13.0 | PAM node mute / bus-off | communication | `PAMSystemFault` |
| 16.0 | Vehicle configuration missing or `PAM_Tuning_Set` calibration mismatch | configuration | `PAMSystemFault` |
| 17.0 / 18.0 | `TRANSM2` missing message / `ShiftLeverPosition` = SNA (only if `Gear_Box_Type ≠ MTX`) | missing / plausibility | `PAMSystemFault` |
| 19.0 / 20.0 | `BRAKE4` missing message / `VehicleStandStillSts` = SNA | missing / plausibility | `PAMSystemFault` |

### Faults detected by IPC and BCM

| ID | ECU | Fault | Reaction |
|---|---|---|---|
| 4.0 | IPC | `STATUS_PAM` missing message | Activate "PARKING ASSISTANCE FAIL" indication, force `DisplayActivation` to "NotActive", set DTC |
| 7.0 | IPC | `STATUS_TELEMATIC` missing for `T_Telematic` | Set DTC, manage the PARKING ASSISTANCE indication |
| 14.0 | BCM | `PAM_LedControlSts` = SNA for `DTC_BCM` | Set DTC, keep the LED at its previous value |
| 15.0 | BCM | `STATUS_PAM` missing message for `DTC_BCM` | Set DTC, keep the LED at its previous value |

### The common fault-handling pattern

Here's the good news: nearly every PAM diagnosis follows the same
detect → react → heal script. Learn this one pattern and you've understood
most of the table — and it's exactly the structure your test cases should
mirror:

```mermaid
flowchart TD
    A["Fault persists for the debounce time<br/>in PAM Diagnostic Requirements"] --> B["Set DTC"]
    B --> C["PAMFault = TRUE<br/>stored in NVM"]
    C --> D{"PAM in OFF state?"}
    D -->|no| E["Disable parking assistance<br/>PAMSystemFault = System_Failure or External_Failure<br/>move to Disable state"]
    D -->|yes| F["Stay OFF, keep DTC"]
    E --> G["Fault no longer detected"]
    F --> G
    G --> H["Heal DTC<br/>PAMSystemFault = False<br/>move to ON_Enable"]
```

The details below are what distinguish a good test from a sloppy one — keep
them close:

- **Debounce** — PAM waits `Tign` (**200 ms** default, tunable to 3000 ms)
  after initialization before evaluating any CAN-message fault. Stimulating a
  missing message earlier than that proves nothing.
- **Fault classification** — `PAMSystemFault` is set to `"System_Failure"` for
  internal/sensor/configuration faults and `"External_Failure"` for faults in
  incoming signals and messages. Check the exact enumeration, not just "fault
  present".
- **Freeze frame** — on fault detection PAM stores the vehicle speed from
  `VehicleSpeedVSOSig` among the environmental data; if the speed signal
  itself is failed (`FailSts = "Fail Present"`), a default value is stored.
- **Trailer hook** — an engineering parameter flags trailer-hook presence;
  with `Trailer.Info = "Present"` PAM disables itself deliberately. This is
  expected behavior, not a fault, and must not set a DTC. Injecting it and
  checking that *no* DTC appears is a perfectly valid test.

## Configuration parameters

The parameter table is your cheat sheet for timings and thresholds (the
default column is the "first trial value"). You'll come back to this table
every time you write a test:

| Parameter | Default | Range | Res. | Unit | Owner |
|---|---|---|---|---|---|
| `Tign` | 200 | 0–3000 | 100 | ms | PAM |
| `REP_MIN_DURATION` | 0 | 0–400 | 25 | ms | PAM |
| `REP_MAX_DURATION` | 375 | 0–400 | 25 | ms | PAM |
| `ARC_FLASH_DUTY_CYCLE` | 50 | 0–100 | 5 | % | IPC |
| `ARC_FLASH_PERIOD` | 600 | 0–1000 | 50 | ms | IPC |
| `PAM_LED_BLINK_DUTY` | 50 | 0–100 | 50 | % | BCM |
| `PAM_LED_BLINK_FREQ` | 2 | 0–10 | 2 | Hz | BCM |
| `PAM_STUCK_TIMEOUT` | 15 | 0–30 | 1 | s | PAM |
| `PAM_LED_BLINK_TIME` | — | 0–10 | 1 | s | PAM |
| `TReverseGear` | 400 | 0–1000 | 10 | ms | PAM |
| `SPEED_LIMIT` | 11 | 0–100 | 1 | km/h | PAM |
| `Min_Speed` | 2 | 0–100 | 1 | km/h | PAM |
| `Max_Speed` | 50 | 0–100 | 1 | km/h | PAM |
| `Tpamwalldet` | 3 | 0–10 | 1 | s | PAM |
| `TFilter` | 100 | 0–5000 | 100 | ms | PAM |
| `T_PAMSts_valid` | 100 | 0–3000 | 500 | ms | IPC |
| `T_Filter_Alerts` | 100 | 0–2000 | 100 | ms | PAM |
| `T_Telematic` | 300 | 0–5000 | 1000 | ms | IPC |

## From document to test cases

Time to put it all together. Here's a practical workflow for testing this
function on a bench or HIL (Hardware-in-the-Loop) rig — notice how each step
maps directly back to a section of the document:

1. **Nominal activation** — KEY ON, simulate `TRANSM2.ShiftLeverPosition =
   "R"` for more than 400 ms, expect `PAMSystemSts = "ON_Active"` and
   `DisplayActivation = "Active"`. Release reverse → `"ON_Inactive"`.
2. **Boundaries** — sweep vehicle speed through 11 km/h in reverse and verify
   the `Disable` / `ON_Enable` transitions and the `PAMAboveSpeed` flag; hold
   the lever in "R" for just under and just over `TReverseGear`.
3. **Fault injection, one per diagnosis ID** — cut a message (missing
   message), send SNA — the "signal not available" value — (plausibility),
   open or short a sensor line, hold the button "Pressed" beyond 15 s. For
   each, verify: debounce respected, DTC set, `PAMSystemFault` enumeration
   correct, state moves to `Disable`.
4. **Recovery** — remove the fault and verify DTC healing and the return to
   `ON_Enable`. Then key-cycle and confirm `PAMFault` persisted in NVM until
   healed.
5. **Cross-ECU checks** — stop `STATUS_PAM` and watch the IPC raise "PARKING
   ASSISTANCE FAIL"; send `PAM_LedControlSts = SNA` and confirm the BCM
   freezes the LED at its last valid command.

!!! tip "Exercises built on this document"
    The hands-on exercises in this section apply exactly these rules:
    [Missing Message](exercise-missing-message/index.md),
    [Exercise Diagnosi 2](exercise-diagnosi-2/index.md),
    [Exercise Diagnosi 3](exercise-diagnosi-3/index.md),
    [Diagnostic Exercise 7](exercise-7-diagnostic-exercise/index.md) and the
    [UDS Exercise](uds-exercise/index.md). For the diagnostic protocol itself
    (services, DTCs, sessions) see [Diagnosis](../../diagnosis/index.md).

!!! warning "Parameters are project data"
    `Tign`, `TReverseGear`, `SPEED_LIMIT` and friends are tunable
    configuration, not constants of nature. Before writing a test, confirm
    which values the ECU under test was actually calibrated with (PROXI /
    `PAM_Tuning_Set`) — a mismatch between document revision and ECU
    calibration is a classic false failure.

!!! success "Key takeaways"
    - VF179 specifies the Rear Parking Assistance function across four ECUs:
      PAM (algorithm + sensors), BCM (button/LED gateway), IPC (arcs + chime),
      LSS (switch acquisition) — and you now know what each one does.
    - The PAM state machine — KEY OFF / KEY ON / ON_Enable (ON_Inactive,
      ON_Active) / Disable / OFF — is driven by the Reverse Condition, the PAM
      button, vehicle speed, trailer presence and the latched `PAMFault`.
    - 20 diagnosis entries follow one learnable pattern: debounce → DTC +
      `PAMFault` in NVM → disable → heal and return to `ON_Enable`.
    - Numbers worth remembering: `TReverseGear` 400 ms, `SPEED_LIMIT` 11 km/h,
      `PAM_STUCK_TIMEOUT` 15 s, `Tign` 200 ms, chime period 0–375 ms, wall
      detection after 3 s.
    - Every requirement maps to a stimulus/observation pair — you can now read
      a VF document like a tester, which is the essence of requirement-based
      diagnostic testing.

## Sub-sections

- [Exercise 7 - Diagnostic exercise](exercise-7-diagnostic-exercise/index.md)
- [Exercise Diagnosi 2](exercise-diagnosi-2/index.md)
- [Exercise Diagnosi 3](exercise-diagnosi-3/index.md)
- [Exercise Missing Message](exercise-missing-message/index.md)
- [UDS Exercise](uds-exercise/index.md)

---

## Source material

This article was distilled from the academy lesson materials:

- :material-file-pdf-box: [ISO14229 1 2020](../../../assets/mil2/18_RDI_Testing/18_RDI_Testing/ISO14229_1_2020.pdf) — PDF, 7.2 MB
- :material-file-pdf-box: [VF179 V1 R3 P332BEV Per Academy](../../../assets/mil2/18_RDI_Testing/18_RDI_Testing/VF179_V1_R3_P332BEV_Per_Academy.pdf) — PDF, 1.4 MB

## Downloads

- :material-file: [VF179 V1 R3 P332BEV Per Academy](../../../assets/mil2/18_RDI_Testing/18_RDI_Testing/VF179_V1_R3_P332BEV_Per_Academy.doc) — 667.5 KB
