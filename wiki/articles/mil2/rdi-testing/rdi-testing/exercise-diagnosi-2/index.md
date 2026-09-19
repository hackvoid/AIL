# Hands-On Diagnostics: RDIs, DTCs and the IPC Cluster

Time to get your hands on a real control unit. In this bench exercise you move
from *knowing* the diagnostic theory to *doing* what a diagnostics engineer does
every day: talking to the **instrument panel cluster (IPC)** of the P332
battery-electric platform over **UDS (Unified Diagnostic Services)**, using its
**CANdela Diagnostic Description (CDD)** database
`D2956_IPC_E2A_R10_332BEV.cdd` as your map.

**What you'll practice:** navigating a diagnostic database, reading and writing
**RDIs (Read Data Identifiers)**, provoking a fault on purpose, watching the
**DTC (Diagnostic Trouble Code)** status byte evolve, and rescuing the snapshot
evidence before you clear anything. Don't worry about breaking something —
that's what the bench is for.

## Goal

By the end of this exercise you will be able to:

- open a CDD database and pull out the complete lists of RDIs, DTCs (with their
  DTC tables), I/O controls and routines;
- match each of those elements to the UDS service that operates on it;
- read an RDI and turn its raw hexadecimal answer into a real physical value;
- write RDIs and *prove* the write by reading the value back;
- create a fault, read the DTC status byte, and drive bits 0, 1 and 2 back to
  zero with the right maneuvers;
- retrieve the **snapshot (freeze frame)** stored with a DTC before clearing
  the fault memory.

## Setup

| Item | Details |
|---|---|
| Bench | Academy bench with the IPC ECU powered and wired to the CAN network |
| Diagnostic tool | CANoe/CANalyzer with the Diagnostics Console (or an equivalent UDS tester) |
| Database | `D2956_IPC_E2A_R10_332BEV.cdd` loaded into the diagnostic session |
| Signal injection | Bench means to stimulate inputs (e.g. simulated vehicle speed) and to provoke faults |

!!! warning "Work on the bench, not on a vehicle"
    Every maneuver here — writing identifiers, clearing fault memory — is done
    on the academy bench ECU. Writing RDIs or clearing DTCs on a real vehicle
    can alter its configuration or erase evidence needed for troubleshooting.

## Step 1 — Explore the diagnostic database

Think of the CDD as the ECU's own user manual. Open it in the CANdela viewer
(or the diagnostics console's database view) and extract four lists:

1. **All RDIs** — the 16-bit identifiers the ECU exposes for reading: VIN
   (Vehicle Identification Number), software/hardware versions, vehicle speed,
   odometer, telltale states, and more.
2. **All DTCs with their DTC table** — each fault code with its meaning, the
   associated failure type byte, and its debounce/healing parameters.
3. **All I/O controls** — the actuators and outputs you can override for
   testing (e.g. forcing telltales or gauge pointers).
4. **All routines** — parametrized procedures you can start and stop on demand
   (self-tests, calibration routines, …).

## Step 2 — Map elements to diagnostic services

Now connect the dots: for each list from Step 1, identify which UDS service
operates on it. This table is your cheat sheet for the rest of the exercise:

| Element | UDS service | Positive response |
|---|---|---|
| Read an RDI | `0x22` ReadDataByIdentifier | `0x62` |
| Write an RDI | `0x2E` WriteDataByIdentifier | `0x6E` |
| Read DTCs / status / snapshots | `0x19` ReadDTCInformation | `0x59` |
| Clear fault memory | `0x14` ClearDiagnosticInformation | `0x54` |
| Override an I/O | `0x2F` InputOutputControlByIdentifier | `0x6F` |
| Start/stop a routine | `0x31` RoutineControl | `0x71` |

!!! note "Response SID = request SID + 0x40"
    A positive response always carries the request's service identifier (SID)
    plus `0x40` (`0x22` → `0x62`). If you see `0x7F` instead, that's a
    **negative response**: `0x7F <original SID> <NRC>` — decode the Negative
    Response Code (e.g. `0x31` requestOutOfRange) before assuming the ECU is
    broken.

## Step 3 — Read and interpret an RDI

1. Pick an RDI from your list and send `ReadDataByIdentifier` with its DID
   (Data Identifier).
2. Decode the response: `62 <DID hi> <DID lo> <data bytes…>`. Those bytes are
   not yet the answer — apply the scaling factor, offset and unit defined for
   that identifier in the CDD to get the physical value.
3. Change the vehicle conditions on the bench so the chosen RDI's content
   actually changes, and read it again to confirm you see the difference.

### Vehicle speed sweep

Now for the fun part. Find the RDI that carries the vehicle speed and run the
full sweep, recording the raw response and the decoded value at each point:

| Simulated speed | What to do |
|---|---|
| 60 km/h | Request the RDI, decode the hex value, verify it matches |
| 150 km/h | Repeat |
| 250 km/h | Repeat |
| 600 km/h | Repeat — observe carefully |

!!! tip "600 km/h is a trap — on purpose"
    600 km/h is far beyond anything this signal should ever see. Depending on
    the CDD definition you will get the signal's saturation value, an
    "invalid/not available" pattern (e.g. all bits set), or a negative
    response. The point of this step is to discover how the ECU and the
    conversion formula behave **at and beyond the valid range** — probing the
    edges like this is exactly what testing a diagnostic specification means.

## Step 4 — Write RDIs

Reading is only half the story. Now you'll change data inside the ECU:

1. Select **three writable RDIs** from the database (the CDD marks which
   identifiers support `WriteDataByIdentifier` — read-only ones will answer
   with NRC `0x31` requestOutOfRange).
2. Write new content with service `0x2E`, building the payload from the DID
   plus the correctly formatted data bytes.
3. **Verify each write** by reading the same RDI back with `0x22` and
   comparing the returned bytes with what you sent. A write you haven't read
   back is a write you haven't done.

```mermaid
sequenceDiagram
    participant T as Tester (CANoe)
    participant E as IPC ECU
    T->>E: "22 <DID> — ReadDataByIdentifier"
    E-->>T: "62 <DID> <value>"
    Note over T: decode raw bytes<br/>with CDD scaling
    T->>E: "2E <DID> <new value> — WriteDataByIdentifier"
    E-->>T: "6E <DID> (positive)"
    T->>E: "22 <DID> — read back to verify"
    E-->>T: "62 <DID> <new value>"
```

## Step 5 — Fault, status byte, healing and snapshot

This is where the exercise comes together: you'll watch a fault live its whole
life inside the ECU, from detection to healing.

### Create the fault and read the status byte

1. Provoke a fault condition on the bench (e.g. disconnect or short a
   monitored line — pick a DTC from your list whose cause you can actually
   reproduce).
2. Read the DTC with `0x19 0x02` (reportDTCByStatusMask) and look at its
   **status byte** — eight bits that tell the fault's life story.

### Heal bits 0, 1 and 2

| Bit | Name | How to drive it to 0 |
|---|---|---|
| 0 | testFailed | Remove the fault cause; the monitoring test runs again and passes |
| 1 | testFailedThisOperationCycle | Complete the current operation cycle and start a new one (key off/on) with the test passing |
| 2 | pendingDTC | Let the ECU count fault-free operation cycles until the DTC "heals" (matures) per its CDD parameters |

```mermaid
flowchart TD
    A["Fault present → test fails"] --> B["bit0=1, bit2=1"]
    B --> C["Remove fault cause"]
    C --> D["Test passes → bit0=0"]
    D --> E["New operation cycle → bit1=0"]
    E --> F["N fault-free cycles → bit2=0<br/>(healed)"]
    F -. "0x14 ClearDiagnosticInformation" .-> G["Memory erased<br/>status byte = 0x00"]
```

### Clear the memory and get the snapshot

Order matters here — read this sequence before you touch the tool:

1. **Before clearing**, identify which snapshot record is attached to your
   DTC: query `0x19 0x04` (reportDTCSnapshotRecordByDTCNumber) with the DTC
   number. The freeze frame captures the ECU's state (speed, voltage,
   counters, …) at the exact moment the fault was detected.
2. Note the snapshot content.
3. Only now clear the fault memory with `0x14` ClearDiagnosticInformation.
4. Read the DTCs again: the entry — and its snapshot — must be gone.

!!! warning "Snapshots die with the clear"
    `0x14` erases DTCs **and their snapshot/extended data**. In real
    troubleshooting you always download snapshots *before* clearing — once
    cleared, the evidence is unrecoverable.

## Expected results

- Four complete lists extracted from the CDD (RDIs, DTCs + DTC table, I/O,
  routines), each mapped to its UDS service.
- A log of the speed sweep showing raw hex responses and correctly decoded
  values at 60 / 150 / 250 km/h, plus documented out-of-range behavior at
  600 km/h.
- Three RDIs written and verified by read-back.
- A description of the fault creation, the status byte at fault time, the
  maneuvers that cleared bits 0–2, the snapshot content, and a clean fault
  memory at the end.

## Common mistakes

- **Forgetting the `+0x40` response SID** and misreading a positive response
  as garbage — or missing that `0x7F` means negative response.
- **Decoding raw bytes without the CDD conversion** (factor/offset/byte
  order) — the hex value is not the physical value.
- **Trying to write a read-only RDI** — check the CDD; expect NRC `0x31`.
- **Clearing the fault memory before reading the snapshot**, losing it
  forever.
- **Confusing bit 2 (pendingDTC) with bit 3 (confirmedDTC)** — pending heals
  by itself after fault-free cycles; confirmed only disappears with an
  explicit clear.
- Declaring the ECU faulty when the 600 km/h test returns an invalid value —
  out-of-range behavior must be checked against the specification first.

!!! success "Key takeaways"
    - The CDD database is your contract with the ECU: RDIs, DTCs, I/O and
      routines, each bound to a UDS service (`0x22`/`0x2E`/`0x19`/`0x14`/`0x2F`/`0x31`).
    - Always decode responses with the database's scaling — and always probe
      boundary values (600 km/h) to see saturation and invalid-value handling.
    - A write is only proven by read-back.
    - The DTC status byte tells the fault's life story; bits 0–2 clear through
      specific healing maneuvers, not by magic.
    - Grab snapshots **before** `ClearDiagnosticInformation` — clearing wipes
      the evidence.
    - You just ran the full daily loop of a diagnostics engineer. This exact
      workflow is what you'll repeat on every ECU you meet.
