# CAPL — Extra Practice Material

This page collects two supplementary resources for CAPL (Communication Access
Programming Language), intended for use after the core lessons — event
procedures, message objects, timers, symbolic access — and the
[CAPL exercises](../capl-exercise/index.md). They cover the progression from
writing individual `on message` handlers to reading and understanding a
production-style CANoe project:

- recorded classroom slide decks for revising any CAPL concept, presented in
  the order an instructor teaches it live, and
- a complete vehicle simulation project in which you can trace how panels,
  environment variables and CAPL nodes interact, and reuse its patterns in
  your own work.

Both resources are optional supplementary material.

## WIP decks — CAPL taught live

The [WIP](wip/index.md) sub-section holds the slide decks from two classroom
sessions recorded in April 2021. They cover the same material as the main
[CAPL article](../index.md), but in the order an instructor presents it in a
classroom, with additional attention to common syntax errors for beginners.

| Deck | Session | What you'll get from it |
|---|---|---|
| `Academy_Kineton_CAPL_20_04_21` | CAPL part 1 (58 slides) | What CAPL is and where it lives inside CANoe/CANalyzer; the CAPL Browser; syntax and semantics — data types, declarations, constants, casting, arrays, strings; the full operator set; control statements; events and event procedures; timers |
| `Academy_Kineton_CAPL2_22_04_21` | CAPL part 2 (36 slides) | Symbolic access to signals and messages (why `EngineSpeed` beats `0x1A0.byte(2)`); panels; environment variables — and the important warning that they are for panel-to-node communication, **not** for node-to-node data exchange; the function toolbox (`getValue()`, `setBtr()`, logging and math functions, `write()`); how the CANoe system clock behaves when a measurement starts |

Read them **in order** — part 2 assumes familiarity with the event-procedure
model from part 1 and builds directly on it.

!!! note "Intentional overlap with the main article"
    These decks intentionally repeat material from the main article. Concepts
    that were unclear on first reading — for example, the difference between a
    timer *variable* and a timer *event procedure*, or the meaning of `this`
    inside `on message` — are often clarified by a second explanation in
    different words. Use part 1 as a revision pass and part 2 as the transition
    from syntax to complete simulations.

## ORC.zip — a complete CANoe project

Reading a working configuration complements the syntax reference in the decks.
`ORC.zip` is a complete **CANoe configuration for the P520 platform (Jeep
Renegade)**, representative of the projects used in OEM and Tier-1 development.
Unpack it, open the `.cfg` file in CANoe, and examine its contents:

| File type | Examples | What it does |
|---|---|---|
| Databases | `P520MY_C1-CAN_R1_01272017_E2A.dbc`, `P520MY_C2-CAN_R1_01272017_E2A.dbc` | DBC (Database CAN) network descriptions for the vehicle's two CAN buses — they decode raw frames into named, scaled signals |
| CAPL source | `P520MY_CAN_R1_01272017_E2A.can` | The CAPL node program(s) that simulate ECU behavior |
| Panels | `P520_E3A_R7_CAN.cbf`, `P520MY_CAN_R1_01272017_E2A.cbf` | Panel Editor panels with switches, LEDs and tell-tales — your "dashboard" for driving the simulation |
| Configurations | `P520_E3A_R7_CAN.cfg`, `P520_E3A_R7_CAN_8.2.cfg`, `.stcfg` | The CANoe configuration files that tie buses, nodes, panels and databases together |
| Panel graphics | `icone/` (`chiave2stati.png`, `L_green_red.png`, `Renegade.png`, …) | Bitmaps behind the panel controls — 2/3-state switches, warning lamps, the vehicle image |

The key aspect to observe while exploring is the data flow, which follows the
same pattern in most CANoe simulation projects:

```mermaid
flowchart LR
    P["Panel switch<br/>(.cbf panel)"] -->|writes| E[Environment variable]
    E -->|triggers| C["on envVar event<br/>CAPL node (.can)"]
    C -->|sets signals| D["Message object<br/>(from DBC)"]
    D -->|output()| B(("CAN bus<br/>C1 / C2"))
    B -->|feeds| T[Trace & other nodes]
```

!!! tip "Suggested exploration"
    Load `P520_E3A_R7_CAN.cfg` in CANoe and open the Simulation Setup. The
    pencil icon on a network node means it carries a CAPL program — double-click
    it to open the `.can` file in the CAPL Browser. Then pick one panel switch
    and follow it end to end: which environment variable it writes, which
    `on envVar` handler reacts, which signals get set, and which message goes
    out on the bus. Tracing one complete path through a real configuration is
    the most effective way to consolidate this material.

!!! warning "Confidential content"
    The DBC files in this archive are proprietary OEM network specifications.
    Use them for local training only — do not share or publish them.

!!! success "Key takeaways"
    - This page provides supplementary material for the CAPL lessons: two
      recorded classroom decks and a complete CANoe project, for use when a
      CAPL concept needs a second explanation.
    - The [WIP](wip/index.md) decks cover the same content as the main article
      in classroom order: fundamentals in part 1, symbolic access, panels and
      functions in part 2. Read them in order.
    - `ORC.zip` contains a full P520/Renegade CANoe project — two DBCs, CAPL
      source, panels, configurations — for tracing one panel switch through to
      the corresponding bus frame.
    - The standard data flow in CANoe simulations is: panel → environment
      variable → CAPL event procedure → signals → CAN frame.
