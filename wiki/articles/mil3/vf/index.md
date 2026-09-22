# Functional Specifications (VF)

Every vehicle function — from climate control to the gear letter on the
dashboard — is described in a **functional specification** before any software
is written. In the FCA/Stellantis world this document is
called a **VF (Vehicle Function)**, written by a dedicated professional role:
the **functionalist**.

The VF is the reference against which vehicle behavior is judged. If the
observed behavior differs from what the VF specifies, either the software or
the document is wrong, and determining which is a recurring part of test and
integration work.

By the end of this article you will be able to:

- explain what a VF contains and where it sits in the development process,
- decode a VF identifier like `VF200_V5_R4R3_P250FL14`,
- walk through a real VF — VF200, *Gearbox Status Management* for a battery
  electric vehicle (BEV) — and recognize its standard sections in practice.

## What a VF is (and is not)

A VF gives a **complete view of the behavior of one function**:

- the features the function offers,
- the electronic control units (**ECUs**, called *nodes*) involved and the
  signals they exchange,
- the expected behavior under each vehicle operating condition (key-on,
  key-off, cranking, low battery, …),
- the **diagnosis** strategy and the **recovery** behavior when something
  fails,
- a history of the changes made with respect to previous versions.

Two properties define the role of a VF:

- **A VF is not tied to the component structure.** It describes *what* the
  function must do, not *how* a specific ECU is built. The same function may
  be re-allocated to different hardware across projects without changing the
  VF's logic.
- **The software is written starting from the VF.** Requirements and test
  cases are derived from it downstream, so ambiguities in the VF propagate
  into the software and should be raised and resolved with the functionalist.

### Position in the V-model

![Position of functional specifications in the V-model](img/vf-v-model.webp)

The VF sits on the **left branch of the V-model**, just below the requirements
specifications: requirements say *what the vehicle must do*, the VF says *how
each function behaves to achieve it*. On the right branch it is mirrored by
the **integration and system test** phases — the tests that verify the
implemented function against the specification. For this reason, test
engineers work extensively with VFs even if they never author one.

!!! note "One function, many VFs"
    A car-level feature area (car access, climate, braking, lighting,
    infotainment, energy management, …) is usually covered by **several VFs**,
    one per function. Together, a vehicle program's VF set describes its
    entire E/E functional behavior.

## Naming and versioning

A VF is identified by the function name followed by an alphanumeric code:

```
<Function Name>  [ VF<num> _ V<x> _ R<y> ]
```

- **VF number** — identifies the function itself (e.g. VF200).
- **V — Version** — versions the functionality according to the vehicle
  set-up (different architectures or configurations may need different
  versions).
- **R — Release** — tracks the evolutions of the same VF over time (bug
  fixes, adaptations when porting the function to a new project).

So `VF200_V5_R4R3_P250FL14` reads as: function 200, version 5 (releases R3
and R4 merged), ported to project 250FL14.

!!! tip "Always quote the full identifier"
    When you reference a VF in a test report or a defect, write the complete
    `VF_V_R` string plus the project code. "The gearbox VF" is ambiguous —
    release R3 and R4 of the same version can specify different behavior, as
    the case study below shows.

## Anatomy of a VF

Layouts vary slightly between manufacturers' templates, but every VF contains
the same logical sections, described below.

### Revision notes

The document opens with a **revision table**: for every release, the date,
the author (the VF *owner*), and the list of changes — usually referencing a
change request (CR) number. If the VF was **ported** from another project,
the origin is declared here. When a test fails against the specification,
check this table first: the discrepancy may come from reading an outdated
release.

### Functional diagram

The **functional diagram** is a graphical map of the function: every involved
node, every connection, and the **CAN/LIN messages and signals** exchanged on
each branch. Reading conventions you will find:

- different **colors** identify the different networks (C1CAN, C2CAN, C3CAN,
  BHCAN, PCAN, LIN, …);
- each branch is annotated with the **message name** and the
  transmitted/received **signal names**;
- nodes drawn with **two colors act as gateways** between networks;
- **numbers inside the node blocks** reference other VFs that signals come
  from or go to — this is how you navigate from one VF to the next;
- node outputs are not always bus messages: they can also be **acoustic or
  visual signals** perceived directly by the driver, like an LED or a buzzer.

### Working conditions

The **working conditions table** states under which vehicle states the
function is operational. Typical rows:

| Working mode | Meaning |
|---|---|
| Key off (+30) | Function active on permanent battery supply |
| Key on (+15) | Function active with ignition on |
| Timed, from key off | Function stays alive for a timed window after key-off |
| Excluded during crank (+) | Function suspended while the starter is cranking |
| Excluded with battery discharged (+) | Function cut off under low battery |

Each row is marked Yes/No, with remarks for timing (in minutes) or exclusion
mode (software or hardware). A simple function may live only at key-on; a body
function often needs key-off and timed operation too.

### Function description

The core section, and the longest. It starts by listing the **nodes
involved**, distinguishing those that *"make logic"* (implement the
algorithm) from those that merely forward or display information, with their
input/output signals. Then it describes the behavior in detail, typically as:

- **structured requirements** — `If … then … else …` rules, often in
  shall-style ("the MTA shall send …"),
- **truth tables** mapping input combinations to outputs,
- **state machines** for operating conditions,
- **timeouts and thresholds** expressed as named calibration parameters —
  never hardcoded numbers in the logic itself.

The behavior is usually split per key condition (`@KeyStatus = keyon`,
`@KeyStatus = keyoff`, …), because most functions behave differently when the
vehicle is asleep.

### Working characteristics (parameters)

All tunable values — thresholds, timeouts, debounce times — are collected as
**configuration parameters**, each with a description, the owning node, and
where the value is implemented (PROXI configuration, end-of-line programming,
part number, or to be defined with the supplier). The distinction matters in
testing: changing a parameter is a *calibration* change, not a software
change, and tests must often be repeated per parameter set.

### CAN wake-up

A short section states whether activating the function can **wake the CAN
network** (for example, a door-handle pull waking the body CAN), with a table of
the triggering events per node. This matters for power-management tests.

### Diagnosis and recovery

The last functional section describes, for every input the function depends
on, what happens when it fails:

- the **diagnosis type** (electrical fault, plausibility fault, missing
  message, CRC/message-counter failure),
- which ECU **stores the diagnostic trouble code (DTC)** and with which
  detection time,
- the **recovery strategy**: the default/fallback values the function uses
  while the fault is active.

!!! note "The CDD has the full diagnosis detail"
    The VF only sketches the diagnosis strategy. The complete description of
    DTCs, validation/invalidation conditions and fault debouncing lives in
    each ECU's **CDD (CANdela Diagnostic Description)** file — you will work
    with CDDs in the diagnosis lessons.

### Companion files: DBC and LIN files

A VF never stands alone. The network-level truth about messages and signals
is kept in two companion databases:

- the **DBC (Database CAN) file**, one per CAN network (e.g. BHCAN), mapping
  every message, signal, scaling and node;
- the **LIN description file (LDF)**, doing the same for the LIN sub-networks
  (e.g. the wiping functionality).

When a VF says "the MTA shall send
`STATUS_C_TCM_MTA_DCTM.GearIndicationSts`", the DBC tells you the message ID,
cycle time, start bit, length and value table of that signal. You will read
and edit DBC files constantly in CANalyzer/CANoe.

## Case study: VF200 — Gearbox Status Management (BEV)

The example in this section is **VF200_V5_R4R3**,
*Gearbox Status Management – BEV*, for FCA project **250FL14** (Vehicle
Function Area: *Powertrain Management*, Group: *GearBox*). The function
manages **everything the driver sees and hears about the transmission**: the
gear indication on the instrument panel, its blinking, the warning messages,
the buzzer, the drive-mode (Eco/Power) management, and the vehicle-hold /
parking-brake requests.

The revision notes already show the kind of changes to expect: across releases,
an unnecessary
parameter (`T_SHOW_OFF_BCM`) was deleted, signal names were corrected
(`Power_Eco.Req` → `EcoPower.Req`), diagnosis timers were aligned
(`MissingMsg_Fast_Time` → `MissingMsg_Default_Time`), and the driver-exit
logic was changed from AND to OR between seat-belt and door status — the kind
of detail that can change a test outcome.

### Nodes and signal flow

![VF200 functional diagram — nodes and signals](img/vf200-functional-diagram.webp)

Three nodes *make logic*:

| Node | Role in VF200 |
|---|---|
| **MTA** (transmission controller) | Reads the lever, decides the gear, requests warnings/buzzer, manages the drive-mode button and the vehicle-hold request |
| **BCM** (body control module) | Acts as a **direct gateway**: routes `STATUS_C_TCM_MTA_DCTM` from C-CAN to B-CAN (`STATUS_B_TCM_MTA_DCTM`), and forwards the seat-belt status from `STATUS_SDM` and the engine status from `STATUS_C_CAN` |
| **IPC** (instrument panel cluster) | Displays the gear position, the blinking, the text warnings, drives the buzzer |

The main inputs the MTA consumes:

| Signal | Carried by | Meaning |
|---|---|---|
| `ShiftLeverPosition.Info` | SLU (shift lever unit) | Requested lever position; the ESM lever has 3 stable positions R–N–D |
| `BrakePedalSts.Info`, `KeyStatus.Info`, `VehicleSpeed.Info` | via VF419 | Brake pedal, key state, vehicle speed |
| `TPBM_INFO.TPBMSts` | via VF026 | Transmission park brake status |
| `STATUS_B_CAN.DriverDoorSts` | via VF092 | Driver door open/closed |
| `STATUS_B_CAN2.SBR1RowDriverSeatSts` | SDM (airbag module) via BCM gateway | Seat belt fastened |
| `MOT2.EngineSts` | via VF406 | Engine OFF / cranking / ON |
| `Power_Eco_Switch.Req` | Power_Eco button | Drive-mode selection |

```mermaid
flowchart LR
    SLU["SLU lever unit"] -->|ShiftLeverPosition| MTA
    PWR["Power_Eco button"] -->|Power_Eco_Switch.Req| MTA
    V419["VF419 signals<br/>brake / key / speed"] --> MTA
    TPBM["VF026 TPBM"] -->|TPBM_INFO.TPBMSts| MTA
    MTA -->|"STATUS_C_TCM_MTA_DCTM"| BCM
    MTA -->|"MOT5.Vehicle_Hold_Rq"| NET["C-CAN"]
    SDM["SDM seat belt"] -->|STATUS_SDM| BCM
    BCM -->|"STATUS_B_TCM_MTA_DCTM<br/>(gateway B-CAN)"| IPC["IPC cluster"]
    IPC --> DRV(("Driver:<br/>display, blink, buzzer"))
```

### Working conditions

VF200's table is instructive: most sub-functions (blinking, buzzer, warnings,
gear-change request, power-eco management, …) are active at **key-on (+15)**,
some remain active in a **timed window after key-off** (the IPC must keep
showing indications for `T_SHOW_OFF_IPC`), and some are **excluded during
cranking** or with **low battery**. In the requirement text you will see
guards like `@KeyStatus.info = Keyon_EngineOff:` before every rule — behavior
is always qualified by which condition is active.

### Gear-change request logic

The core algorithm decides whether a lever movement is *accepted*. The
pattern repeats for N, R and D:

- At **key-on, engine off**: the gear is accepted only if the **brake pedal
  is pressed** at the moment of the lever transition; otherwise the MTA emits
  `RoboticTransmissionWarnings = Press_Brake_Pedal_Repeat_Warning` for a
  `Tmessage` time.
- At **key-on, engine on**, engaging **R**: coming from D, the vehicle speed
  must be ≤ `Rthreshold`; coming from N, the brake must also be pressed. If
  the speed is too high, the MTA sends `Vehicle_Speed_Too_High_to_Shift_R`
  **and forces N** — but as soon as speed drops below the threshold (lever
  still in R), it stops the warning and engages R.
- Engaging **D** mirrors this with `Forwardthreshold` (a *negative* first
  trial value of −3 km/h — the car may still be rolling slightly backwards).

**Mismatch detection**: the MTA continuously compares the lever position with
the actually engaged gear (and the park-brake status). If a mismatch persists
longer than `T_Gear_Mismatch` (first trial 500 ms), it sets
`GearIndicationSts = Blinking` **and** `BuzzerReqSts = OtherCaseSoundOn` —
the blinking gear letter and audible warning the driver perceives when the
requested gear could not be engaged.

### Drive-mode (Power_Eco) management

The Power_Eco button cycles the drive mode. The sequence is
**Normal → Eco → Power → Eco → …** — note that Normal is only the
*predominant mode* at startup; after that, the button toggles between Eco and
Power. Each press is debounced (`Tdebounce`, first trial 60 ms) and mapped
onto `DriveModeSts`:

```mermaid
stateDiagram-v2
    [*] --> Normal: startup (DriveModeSts = No_program_Selected)
    Normal --> Eco: button press (after Tdebounce)
    Eco --> Power: button press
    Power --> Eco: button press
```

At every key-on→key-off transition the MTA reports
`DriveModeSts = No_program_Selected` for the `T_SHOW_OFF_MTA` window.

### Vehicle-hold (transmission parking brake) scenarios

The most complex part of VF200 is `MOT5.Vehicle_Hold_Rq` — when the MTA asks to
hold the vehicle. The VF enumerates **seven scenarios**, with explicit
priority rules (driver-exit scenarios override normal operation). Two of them
illustrate the safety reasoning:

- **Switch-off**: at key-on→key-off, if the last known speed was below
  `TPBM_threshold` the MTA requests hold; otherwise it warns
  `Vehicle_In_Neutral`.
- **Driver exit in D/R (7th scenario)**: at key-on engine-on, if the driver
  opens the door **and** unfastens the seat belt while in D or R, and the
  speed is below the threshold, the MTA **autonomously shifts to N** and
  requests hold. Exit conditions require the driver to be back (door closed /
  belt fastened) and a fresh, brake-pressed lever movement.

!!! warning "OR vs AND is a safety decision"
    The 6th scenario (driver exit in N) triggers with door open **or** belt
    unfastened; the 7th requires **both**. That OR was introduced by a change
    request — a reminder that these logical operators are deliberate safety
    choices, and that your tests must cover each side of them.

### Indications on the cluster

The IPC translates each MTA signal into something the driver perceives. The
mapping is one-to-one and fully testable:

| MTA signal value | IPC indication |
|---|---|
| `GearIndicationSts = Blinking` | Shifter position display blinks |
| `BuzzerReqSts = OtherCaseSoundOn` | Gear buzzer on |
| `RoboticTransmissionWarnings = Press_Brake_Pedal_Warning` | "GEAR PRESS BRAKE" text |
| `… = Press_Brake_Pedal_Repeat_Warning` | "GEAR RT PRESS BRAKE REPEAT" text |
| `… = Vehicle_Speed_Too_High_to_Shift_R / _D` | "SPEED TOO HIGH TO R / D" text |
| `… = Trans_Recover_Mode_Warning` | "TRANSMISSION RECOVERY MODE" text |
| `… = Vehicle_In_Neutral` | "VEHICLE IN N – PULL HANDBRAKE" (also at key-off, for `T_SHOW_OFF_IPC`) |

The IPC also runs its own internal logic: it activates
`GearInsertNAndPressBrakeToStart.Req` whenever the lever is not in N **or**
the brake is not pressed (shown at key-on engine-off as "GEAR RT BEFORE
CRANKING"), and derives `EcoPower.Req` from the received `DriveModeSts`.

### Diagnosis and recovery in VF200

The diagnosis table lists every input, the fault type, and the storing ECU.
The recovery rules follow the standard patterns:

| Fault | Detecting ECU | Recovery while fault active |
|---|---|---|
| `ShiftLeverPosition` electrical / plausibility fault | MTA | DTC validated, "Motor Fault" to IPC; keep D if driving forward, otherwise force N and declare `ShiftLeverPosition = N` |
| `Power_Eco_Switch.Req` stuck (`TStuck`, 20 s) or electrical | MTA | Force `DriveModeSts = No_program_Selected`, go to Normal mode |
| `STATUS_B_CAN` missing (> `MissingMsg_Default_Time`) | MTA | Assume `DriverDoorSts = Closed` |
| `STATUS_B_CAN2` missing | MTA | Assume `Seat Belt Fasten` |
| `TPBM_INFO` missing or CRC/MC fail (`MTA_CRC_MC_wrong_timer`) | MTA | Use last valid `TPBMSts` (default `Released`) |
| `STATUS_SDM` missing | BCM | Forward `Seat Belt Fasten` |
| `STATUS_C_CAN`, `STATUS_B_TCM_MTA_DCTM`, `EDR_INFO` missing | IPC | Assume `EngineSts = On`, requests `Not_Active`, brake switch `Not_active` |

The design principle is consistent: **fallback values are chosen on the safe side** —
assume the door is closed and the belt fastened (so no spurious hold
request), declare the engine running, and neutralize driver-visible requests.

### Configuration parameters

VF200 closes with its calibration table of tunable parameters:

| Parameter | Meaning | First trial value |
|---|---|---|
| `Rthreshold` | Max speed to engage reverse | 3 km/h |
| `Forwardthreshold` | Min speed to engage drive | −3 km/h |
| `TPBM_threshold` | Speed below which vehicle hold can be requested | 4 km/h |
| `T_Gear_Mismatch` | Delay before declaring lever/gear mismatch | 500 ms |
| `Tdebounce` | Button debounce / filtering | 60 ms |
| `TStuck` | Button-pressed-too-long plausibility fault | 20 s |
| `Tmessage` | Duration of a warning message to the IPC | 10 s |
| `T_SHOW_OFF_MTA` / `T_SHOW_OFF_IPC` | Keep sending/showing after key-off | 8 s / 7 s |
| `MissingMsg_Default_Time` | Missing-message detection time | 2.5 s |
| `MTA_CRC_MC_wrong_timer` | CRC / message-counter failure debounce | 3 |

!!! tip "For your test cases"
    Every `If … then` rule, every truth-table row, every scenario number and
    every parameter in a VF is a candidate test case. In the test-design
    lessons, a VF like VF200 is exactly the document you will be asked to
    derive cases from — boundary values around `Rthreshold`,
    `TPBM_threshold` and the mismatch timer are typical targets.

!!! success "Key takeaways"
    - A VF is the functionalist's document describing the complete behavior of
      one vehicle function; software and tests are derived from it, and it is
      independent of the component structure.
    - A VF identifier `Function [VFn_Vx_Ry]` encodes the function number, the
      version (vehicle set-up) and the release (evolution); the full string
      must be quoted in test reports and defects.
    - The fixed sections are: revision notes, functional diagram, working
      conditions, function description, parameters, CAN wake-up, diagnosis &
      recovery — plus the DBC/LIN companion files and the CDD for full
      diagnosis detail.
    - VF requirements are written per key condition and use named calibration
      parameters rather than hardcoded values.
    - VF200 illustrates the typical patterns: lever/gear mismatch → blinking +
      buzzer, speed-thresholded engagement with forced-N fallback, seven
      prioritized vehicle-hold scenarios, one-to-one IPC mapping, and
      safe-side recovery defaults for every failed input.
