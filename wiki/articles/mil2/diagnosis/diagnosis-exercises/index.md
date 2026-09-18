# Diagnosis Exercises

This section turns the theory of the [Diagnosis](../index.md) lesson into
practice. Instead of listening to how UDS services and DTC status bits work,
you now have to **predict exactly what an ECU will answer** when a diagnostic
tester queries it — step by step, through a scripted sequence of vehicle
manoeuvres.

The exercises train the single most-used diagnostic skill in day-to-day E/E
work: reasoning about how a fault is detected, confirmed, reported, stored and
healed across ignition and driving cycles.

## What you will practice

Working through these exercises you will apply, with concrete byte values:

- **UDS service `0x19` (ReadDTCInformation)** — in particular sub-function
  `0x02` with a status mask (`19 02 08` asks for DTCs whose *confirmedDTC* bit
  is set), and how the ECU's reply changes as the fault state evolves.
- **The DTC status byte** — the eight status bits (testFailed,
  testFailedThisOperationCycle, pendingDTC, confirmedDTC,
  testNotCompletedSinceLastClear, and friends) and when each one sets and clears.
- **Fault timing logic** — enable conditions, setting/healing conditions,
  event-based vs. time-based debouncing, and the difference between a
  **monitoring cycle** (key on to key off) and a **driving cycle** (engine run).
- **Warning lamp behavior** — how the MIL (Malfunction Indicator Lamp) follows
  the confirmedDTC bit and heals after a defined number of clean cycles.

## Contents of this section

| Item | What it is |
|---|---|
| [Exercise Diagnosi 1](exercise-diagnosi-1/index.md) | A 30-step manoeuvre sequence on a cruise-control button fault (short circuit to battery). For every step you must write the ECU's full reply to `19 02 08`, tracking the DTC status mask bit by bit in a spreadsheet. |
| ISO 14229-1:2020 | The full UDS specification, provided in the exercise directory as your reference. Use it to check service formats, sub-function parameters and the exact meaning of each DTC status bit. |

## Suggested approach

1. **Re-read the Diagnosis lesson** first — you need the UDS service overview,
   the DTC format (2-byte code + 1-byte symptom) and the status-bit map fresh
   in mind before attempting the exercises.
2. **Open ISO 14229-1 at the DTC status bit table** (the
   `DTCStatusAvailabilityMask` description) and keep it beside you; every
   answer you write is an 8-bit mask built from those definitions.
3. **Work the manoeuvres strictly in order** — the reply to step *N* depends on
   the ECU state left by steps *1…N−1*. Skipping ahead makes the exercise
   meaningless.
4. **Write every response bit by bit** in the spreadsheet, not just "yes/no
   fault": the point is to see pending → confirmed → healed transitions in the
   individual bits.
5. **Verify against the solution logic**: does the MIL light exactly when
   confirmedDTC sets? Does the DTC disappear from the `19 02 08` response only
   after the required healing cycles?

!!! tip "Why the mask matters"
    A tester that requests `19 02 08` only receives DTCs whose status byte
    matches the mask — here, bit 3 (confirmedDTC). A *pending* fault that has
    not yet been confirmed is invisible to that request. Choosing the right
    status mask is what separates "the ECU looks clean" from "the fault is
    there, just not confirmed yet".

!!! note "Further diagnosis exercises"
    More hands-on diagnostic scenarios — working with a real `.cdd` diagnostic
    description of the instrument cluster — live in the RDI Testing section:
    [Exercise Diagnosi 2](../../rdi-testing/rdi-testing/exercise-diagnosi-2/index.md)
    and
    [Exercise Diagnosi 3](../../rdi-testing/rdi-testing/exercise-diagnosi-3/index.md).

!!! success "Key takeaways"
    - This section is pure practice: given a fault scenario and a manoeuvre
      script, predict the ECU's exact reply to a UDS `ReadDTCInformation`
      request.
    - Everything hinges on the DTC status byte: know which bit sets at
      detection (pending), which at confirmation, and how healing cycles clear
      them.
    - Keep ISO 14229-1 open while you work — it is the normative reference for
      every byte value you write.
