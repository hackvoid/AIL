# Diagnosis Exercises

This section applies the diagnostic concepts from the
[Diagnosis](../index.md) lesson to a scripted fault scenario. The earlier
lesson described how UDS (Unified Diagnostic Services) requests and DTC
(Diagnostic Trouble Code) status bits behave; here you predict the ECU's
exact reply when a diagnostic tester queries it during a sequence of
vehicle manoeuvres, byte by byte.

Tracing a fault through *detected → pending → confirmed → healed* is a core
diagnostic task in day-to-day E/E work. By the end of this section you will
be able to:

- predict an ECU's full reply to a `ReadDTCInformation` request at any point
  in a manoeuvre sequence,
- track every DTC status bit as a fault appears, is confirmed and heals,
- explain why a tester can report "no faults" while a fault is present in
  the ECU but not yet confirmed.

## What you'll practice

The exercises use concrete byte values throughout:

- **UDS service `0x19` (ReadDTCInformation)** — sub-function `0x02`
  (reportDTCByStatusMask). The request `19 02 08` asks: *"tell me every DTC
  whose status byte has bit 3 (confirmedDTC) set."*
- **The DTC status byte** — the eight bits that describe a fault's life:
  testFailed, testFailedThisOperationCycle, pendingDTC, confirmedDTC, and
  testNotCompletedSinceLastClear. You will set and clear each one
  by hand.
- **Fault timing logic** — enable conditions (when the ECU is even allowed to
  look for the fault), setting and healing conditions, event-based
  debouncing, and the difference between a **monitoring cycle** (key on to
  key off) and a **driving cycle** (engine actually running).
- **Warning lamp behavior** — how the MIL (Malfunction Indicator Lamp, the
  "check engine" light) follows the confirmedDTC bit and only goes out after
  a defined number of clean driving cycles.

## Goal

For each of the 30 manoeuvres in Exercise Diagnosi 1, write down the ECU's
**complete response** to the tester request `19 02 08` — including the DTC
status mask expressed bit by bit. If your predicted bits line up with the
fault's true lifecycle across the whole sequence, you have understood how a
real ECU stores and forgets faults.

## Setup

What you are working with:

| Item | What it is |
|---|---|
| [Exercise Diagnosi 1](exercise-diagnosi-1/index.md) | A 30-step manoeuvre script built around a cruise-control (CC) button fault: a short circuit to battery (SCB) that appears, gets pushed, removed, re-inserted and healed across key cycles and engine runs. |
| ISO 14229-1:2020 | The full UDS specification, provided in the exercise directory as the normative reference. Keep it open at the `DTCStatusAvailabilityMask` table — every answer you write is an 8-bit mask built from those definitions. |
| A spreadsheet | The exercise asks you to log every ECU response in Excel, one row per step, with the status byte expanded into individual bits. |

The exercise's ground rules:

- **Enable condition:** the ECU only monitors the fault while the CC button
  is pushed.
- **Fault condition:** SCB on the CC button.
- **DTC:** code `00 25`, symptom byte `00`. Status bits 4 and 5 are unused.
- **MIL:** switches on at the first driving cycle with the fault confirmed,
  and heals after **2 clean driving cycles**.
- **Setting and healing are event-based** — no time debounce to simulate.
- **Monitoring cycle** = key on to key off; **driving cycle** = engine run.
- Every manoeuvre counts as fully completed.

## The lifecycle you are tracking

The following state diagram summarizes the fault lifecycle used throughout
the exercise:

```mermaid
stateDiagram-v2
    [*] --> NoFault
    NoFault --> Pending: fault detected (enable condition met)
    Pending --> Confirmed: fault still present in a later cycle
    Confirmed --> Healing: fault removed, MIL stays on
    Healing --> NoFault: 2 clean driving cycles, MIL off
    Pending --> NoFault: fault gone before confirmation
```

The request `19 02 08` filters on **bit 3 (confirmedDTC)**: while the fault
is merely *pending*, the ECU legitimately answers "no DTCs". Only once the
fault is confirmed does `00 25` appear in the response — and it only
disappears again after the healing conditions are met.

## Steps

1. **Re-read the Diagnosis lesson first.** You need the UDS service overview,
   the DTC format (2-byte code + 1-byte symptom) and the status-bit map fresh
   in mind before attempting any manoeuvre.
2. **Open ISO 14229-1 at the DTC status bit table** and keep it beside you.
   The standard is the authoritative definition whenever a bit's meaning is
   unclear.
3. **Work the manoeuvres strictly in order.** The reply to step *N* depends
   entirely on the ECU state left behind by steps *1…N−1*. Skipping ahead
   makes the exercise meaningless.
4. **Write every response bit by bit** in your spreadsheet — never just
   "fault yes/no". The status transitions pending → confirmed → healed are
   only visible in the individual bits.
5. **Sanity-check your solution against the physics of the scenario.** The
   MIL must light exactly when confirmedDTC sets; the DTC must disappear
   from the `19 02 08` response only after the 2 required healing driving
   cycles; and a push of the CC button with no SCB present must produce a
   clean testNotCompleted → completed transition.

!!! tip "Why the mask matters"
    A tester sending `19 02 08` only *sees* DTCs whose status byte matches
    the mask — here, bit 3 (confirmedDTC). A pending fault that has not yet
    been confirmed is invisible to that request. Choosing the right status
    mask is the difference between "the ECU looks clean" and "the fault is
    present but not yet confirmed" — a common situation when a customer
    reports that a problem "comes and goes".

!!! note "Further diagnosis exercises"
    Additional hands-on scenarios based on a real `.cdd` diagnostic
    description of the instrument cluster are available in the RDI Testing
    section:
    [Exercise Diagnosi 2](../../rdi-testing/rdi-testing/exercise-diagnosi-2/index.md)
    and
    [Exercise Diagnosi 3](../../rdi-testing/rdi-testing/exercise-diagnosi-3/index.md).

!!! success "Key takeaways"
    - An ECU's reply to `19 02 08` can be derived at any point in a fault
      scenario from the DTC status byte and the fault's lifecycle state.
    - The DTC status byte records the fault lifecycle: pending at detection,
      confirmed after repetition in a later cycle, healed only after the
      required clean driving cycles.
    - "No DTCs in the response" does not mean "no fault"; it means no stored
      DTC matches the requested status mask.
    - ISO 14229-1 defines every status bit and byte value used in this
      exercise and is the normative reference for interpreting them.

## Sub-sections

- [Exercise Diagnosi 1](exercise-diagnosi-1/index.md)

---

## Source material

This article was distilled from the academy lesson materials:

- :material-file-pdf-box: [ISO14229 1 2020](../../../assets/mil2/17_Diagnosis/17_Diagnosis_Exercises/ISO14229_1_2020.pdf) — PDF, 7.2 MB
