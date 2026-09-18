# INCA Exercises — Knowledge Questionnaire

The first INCA exercise is not a bench task but a **15-question
questionnaire** that checks whether you understood the
[INCA lecture](../index.md) before you start touching real calibration data.
You answer in writing, from memory or from the lecture notes, and the answers
are then discussed with the instructor. This page reproduces the exercise in a
self-study format: the questions grouped by theme, what a good answer must
contain, and a model answer for each.

## Goal

Demonstrate that you can explain, in your own words:

- what INCA is and why calibration engineers use it,
- how measurement, calibration and flashing fit together in one workflow,
- which interfaces and protocols connect INCA to an ECU,
- how INCA protects calibration data and fits into a company's tool chain.

## Setup

- **Time:** about 45–60 minutes for the questionnaire alone.
- **Material:** no hardware or license needed — answer offline, with the
  lecture slides and the *INCA Getting Started* manual as reference.
- **Deliverable:** a written answer per question (a few sentences each; bullet
  points are fine).

## The questions

Work through all fifteen before reading the answer key below.

**Purpose and role of the tool**

1. What is INCA, and what is its primary purpose in the automotive industry?
2. How does INCA contribute to developing and optimizing combustion-engine
   control units?
3. What are the main features INCA offers for engine calibration?
4. Which advantages does INCA have over other calibration tools?

**Working with the tool**

5. How does INCA help engineers diagnose and troubleshoot engine problems?
6. Describe the typical workflow of an engineer calibrating and optimizing an
   ECU with INCA.
7. Which data interfaces and communication protocols does INCA support for
   connecting to different ECUs?
8. How does INCA ensure the security and integrity of sensitive calibration
   data during development?

**Context and advanced use**

9. Give examples of automotive companies or projects that use INCA in engine
   development.
10. Which advanced functions do experienced calibration engineers use
    regularly?
11. How does INCA handle real-time adjustments on a running engine?
12. Is INCA used in industries or applications outside automotive?
13. How has INCA evolved with engine technology and industry demands?
14. What training and resources exist for engineers who want to learn INCA?
15. Which collaborations or integrations connect INCA with other tools used in
    engine development?

## Answer key

Compare your answers against these model points. You don't need identical
wording — you need the same substance.

### 1–2. What INCA is and why it exists

INCA (**INtegrated Calibration and Acquisition** system) is ETAS's
measurement, calibration and diagnostics environment for electronic control
units. Engine control software contains tens of thousands of parameters —
scalars, curves and maps — whose final values cannot be determined in the
design office: they are tuned empirically on the test bench and in the
vehicle. INCA lets the engineer **read measured variables from the running ECU
in parallel with changing calibration parameters**, observe the effect
immediately, and iterate until emissions, consumption, drivability and
performance targets are met.

### 3–4. Main features and advantages

- **Experiments**: configurable screens combining oscilloscopes (YT/XY),
  numeric displays, gauges and calibration editors for scalars, curves and
  maps.
- **Database-centered data management**: workspaces, projects, A2L
  descriptions and datasets are managed in one place with versioned datasets.
- **Working Page / Reference Page concept**: edit a copy of the calibration
  while keeping the original reference, and A/B-switch between them.
- **Add-ons and open interfaces**: MDA (measurement data analysis), ODX-LINK
  diagnostics, MATLAB/Simulink integration (INCA-MIP, INCA-SIP), ASAM
  interfaces for testbed automation.
- Advantages over generic tools: it is the de-facto industry standard, so
  ECU suppliers deliver A2L files and protocol support for it; the same tool
  covers measurement, calibration and flashing; and it supports virtually all
  ETAS and third-party hardware through standard interfaces.

### 5. Diagnosis and troubleshooting

Because measurement and calibration happen simultaneously, you watch the
ECU's *internal* variables (not just external sensor signals) while the
engine misbehaves: lambda control states, knock detection counters, ignition
timing actually applied, limiter interventions. Recorded measure files can be
replayed and analyzed offline in MDA. With the ODX-LINK add-on, INCA also
reads fault memory (DTCs) and runs diagnostic services, so calibration and
classical diagnosis live in the same session.

### 6. Typical workflow

```mermaid
flowchart LR
    A["Open workspace<br/>and project"] --> B["Select ECU + A2L<br/>description file"]
    B --> C["Configure hardware<br/>(ETK / XCP on CAN)"]
    C --> D["Build experiment:<br/>variables, displays,<br/>calibration editors"]
    D --> E["Measure and calibrate<br/>online on the running ECU"]
    E --> F["Save working dataset,<br/>compare with reference"]
    F --> G["Download / flash<br/>final dataset to ECU"]
```

### 7. Interfaces and protocols

| Connection | Protocol / hardware | Notes |
|---|---|---|
| Parallel | **ETK** emulator test probe | replaces ECU memory; fastest, full data access |
| Serial on CAN | **CCP** or **XCP-on-CAN** | standard ASAM calibration protocols |
| Serial on Ethernet | **XCP-on-Ethernet** | high data rates |
| Serial legacy | K-Line diagnostic interface | older ECUs |
| Description format | **A2L** (ASAM-MCD 2MC) | maps symbolic names to addresses, scaling, limits |

The ECU must contain the matching protocol driver (about 30 lines of extra
code for an ETK acquisition table; more for CCP/XCP), otherwise no connection
is possible.

### 8. Security and data integrity

- The **reference page is read-only**: the originally loaded dataset is always
  preserved for comparison and rollback.
- **Datasets are versioned** in the database; every calibration change is a
  new dataset, not an overwrite.
- Access to projects and flash/download operations can be restricted per user
  and per ECU, and calibration files travel with checksums so corrupted or
  mismatched data is rejected instead of flashed.

### 9–12. Users, advanced functions, real-time behavior, other domains

- INCA is used by virtually all major OEMs and Tier-1 suppliers (Bosch/ETAS's
  parent ecosystem, and engine, transmission and hybrid projects across the
  industry) — it is the tool you will most likely find already installed on a
  calibration bench.
- Advanced functions: automated calibration via the ASAM-MCD 3MC testbed
  interface, scripting through open APIs, Simulink model calibration with
  INCA-SIP, bypass/rapid-prototyping hooks (EHOOKS), and measurement-data
  mining in MDA.
- Real-time operation relies on **emulation memory**: with an ETK the ECU runs
  its program from emulation RAM, so parameters are edited while the engine
  runs; the Working Page / Reference Page switch lets you flip between old and
  new calibration at the push of a button, even mid-run. Serial (CCP/XCP)
  systems do the same with smaller SERAM/SERAP emulation RAM.
- Outside road vehicles, INCA is used wherever engine/ECU calibration exists:
  marine, agricultural and construction machinery, stationary gensets, and
  increasingly electrified powertrains.

### 13–15. Evolution, training, ecosystem

- Evolution: from CCP to XCP, from parallel ETK to serial calibration, from
  pure ICE maps to hybrid/EV functions, FlexRay and Ethernet support, MDF4
  measurement files, and growing automation interfaces — each driven by new
  bus technology and by the shift from bench work to automated testbeds.
- Training: ETAS offers official courses and the *Getting Started* manual and
  online help ship with the product; this bootcamp's own INCA lessons are the
  first step.
- Integrations: MATLAB/Simulink (INCA-MIP/SIP), ASAM-standard interfaces to
  testbed automation systems, diagnostic toolchains via ODX-LINK, and third-
  party hardware through the open HWI interface.

## Common mistakes

- **Confusing measurement with calibration.** Measuring = reading variables;
  calibrating = writing parameters. INCA does both, but they are different
  operations with different risks.
- **Thinking INCA changes the ECU program.** Calibration edits *data*
  (parameters, curves, maps), not code. Code changes need a rebuild and a
  flash.
- **Forgetting the A2L file.** Without the A2L description matching the exact
  software version in the ECU, variables cannot be addressed — a wrong A2L is
  a classic source of corrupted calibrations.
- **Editing the reference.** You always edit the Working Page; the Reference
  Page exists so you can compare and roll back. Overwriting your reference
  destroys your baseline.

!!! success "Key takeaways"
    - INCA = ETAS's integrated environment for **measurement, calibration and
      flashing** of ECUs; its job is to tune the thousands of parameters in
      control software on the running system.
    - The core concepts are the **experiment**, the **A2L description file**,
      and the **Working Page / Reference Page** pair for safe A/B calibration.
    - ECUs connect via **ETK (parallel)** or **CCP/XCP (serial over CAN,
      Ethernet, …)**; the matching protocol driver must exist in the ECU.
    - Data integrity comes from read-only reference datasets, versioning and
      access control — never calibrate without a rollback path.

!!! tip "Next step"
    Once you can answer all 15 questions confidently, move on to the
    hands-on INCA/MDA exercises in [INCA 2](../../inca-2/index.md), where you
    work with real measurement files.

---

## Source material

This article was distilled from the academy lesson materials:

- :material-file-pdf-box: [INCA questionnaire](../../../assets/mil3/26_INCA/26_INCA_Exercises/1_INCA_questionnaire.pdf) — PDF, 74.2 KB
- :material-file-pdf-box: [INCA Questionnaire](../../../assets/mil3/26_INCA/26_INCA_Exercises/2_INCA_Questionnaire.pdf) — PDF, 77.1 KB
