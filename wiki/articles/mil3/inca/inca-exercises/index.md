# INCA Exercises — Knowledge Questionnaire

This exercise is a **15-question questionnaire** on the material covered in
the [INCA lecture](../index.md). No bench, hardware, or license is required.
Answers are written from memory or notes and then discussed with the
instructor.

**Topics covered:** what INCA (INtegrated Calibration and Acquisition system)
is, how measurement, calibration and flashing fit into one workflow, how INCA
communicates with an electronic control unit (ECU), and how it protects
calibration data.

This page provides the questions grouped by theme and a model answer for
each. Answer the questions first, then compare against the answer key.

## Goal

By the end of this exercise you'll be able to explain, in your own words:

- what INCA is and why calibration engineers rely on it,
- how measurement, calibration and flashing fit together in one workflow,
- which interfaces and protocols connect INCA to an ECU,
- how INCA protects calibration data and fits into a company's tool chain.

## Setup

- **Time:** about 45–60 minutes for the questionnaire alone.
- **Material:** no hardware or license needed — answer offline, with the
  lecture slides and the *INCA Getting Started* manual as reference.
- **Deliverable:** a written answer per question (a few sentences each; bullet
  points are fine).

## Steps

1. Read all fifteen questions below once, without writing anything, to
   identify what you already know and what requires a look-up.
2. Write your answers from memory first; only then fill gaps from the lecture
   material.
3. Compare your answers against the answer key. Identical wording is not
   required; the substance must match.
4. Bring any incorrect or incomplete answers to the discussion with the
   instructor.

## The questions

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

### 1–2. What INCA is and why it exists

INCA is ETAS's integrated environment for **measurement, calibration and
diagnostics** of electronic control units. Engine control software contains
tens of thousands of parameters — scalars, curves and maps — whose final
values cannot be determined at a desk. They are tuned empirically, on the
test bench and in the vehicle. INCA lets you **read measured variables from
the running ECU while changing calibration parameters at the same time**, see
the effect immediately, and iterate until emissions, consumption, drivability
and performance targets are met. This measure–calibrate loop is the core of a
calibration engineer's work, and INCA is the tool that implements it.

### 3–4. Main features and advantages

- **Experiments**: configurable screens combining oscilloscopes (YT/XY),
  numeric displays, gauges and calibration editors for scalars, curves and
  maps — the main working environment for the running ECU.
- **Database-centered data management**: workspaces, projects, A2L
  descriptions and datasets live in one place, with versioned datasets.
- **Working Page / Reference Page concept**: edit a copy of the calibration
  while keeping the original reference intact, and A/B-switch between them.
- **Add-ons and open interfaces**: MDA (Measurement Data Analyzer), ODX-LINK
  diagnostics, MATLAB/Simulink integration (INCA-MIP, INCA-SIP), and ASAM
  interfaces for testbed automation.
- Advantages over generic tools: INCA is the de-facto industry standard, so ECU
  suppliers deliver A2L files and protocol support for it out of the box; one
  tool covers measurement, calibration *and* flashing; and it drives virtually
  all ETAS and third-party hardware through standard interfaces.

### 5. Diagnosis and troubleshooting

Because measurement and calibration happen simultaneously, you watch the
ECU's *internal* variables — not just external sensor signals — while the
engine exhibits a fault: lambda control states, knock detection counters, the
ignition timing actually applied, limiter interventions. Recorded measure
files can be replayed and analyzed offline in MDA. With the ODX-LINK add-on,
INCA also reads fault memory (diagnostic trouble codes, DTCs) and runs
diagnostic services, so calibration and classical diagnosis live in the same
session.

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

Note that the ECU must contain the matching protocol
driver (about 30 lines of extra code for an ETK acquisition table; more for
CCP/XCP). Without this driver, no connection is possible.

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
  industry). It is the tool most commonly found installed on calibration
  benches.
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
  measurement files, and growing automation interfaces — each step driven by
  new bus technology and by the shift from bench work to automated testbeds.
- Training: ETAS offers official courses, and the *Getting Started* manual and
  online help ship with the product. This bootcamp's INCA lessons serve as an
  introduction.
- Integrations: MATLAB/Simulink (INCA-MIP/SIP), ASAM-standard interfaces to
  testbed automation systems, diagnostic toolchains via ODX-LINK, and
  third-party hardware through the open HWI interface.

## Common mistakes

Frequent errors made by new engineers:

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
      flashing** of ECUs — it tunes the thousands of parameters in control
      software on the running system.
    - The three core concepts are the **experiment**, the **A2L description
      file**, and the **Working Page / Reference Page** pair for safe A/B
      calibration.
    - ECUs connect via **ETK (parallel)** or **CCP/XCP (serial over CAN,
      Ethernet, …)** — and the matching protocol driver must exist in the ECU.
    - Data integrity comes from read-only reference datasets, versioning and
      access control: never calibrate without a rollback path.
    - The 15 questions covered INCA's purpose, features, interfaces, data
      security, user base, real-time operation, evolution, training resources,
      and tool integrations.

!!! tip "Next step"
    Once you can answer all 15 questions confidently, move on to the
    hands-on INCA/MDA exercises in [INCA 2](../../inca-2/index.md), where you
    work with real measurement files.
