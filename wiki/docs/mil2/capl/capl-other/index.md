# CAPL — Extra Practice Material

You've made it through the core CAPL (Communication Access Programming Language)
lessons — event procedures, message objects, timers, symbolic access — and the
[CAPL exercises](../capl-exercise/index.md). Nice work. This page is where you go
**next**: two resources that take you from "I can write an `on message` handler"
to "I can read a real, production-style CANoe project and understand why it's
built the way it is."

Here's what you'll be able to do after spending an afternoon here:

- revise any CAPL concept that felt shaky, explained the way an instructor
  actually teaches it live, and
- open a genuine vehicle simulation project, trace how its panels, environment
  variables and CAPL nodes talk to each other, and steal its patterns for your
  own work.

Nothing here is mandatory — but both resources repay the time many times over.

## WIP decks — CAPL taught live

The [WIP](wip/index.md) sub-section holds the slide decks from two classroom
sessions recorded in April 2021. They cover the same ground as the main
[CAPL article](../index.md), but in the order a real instructor builds it up,
with extra care around the syntax traps that catch every beginner.

| Deck | Session | What you'll get from it |
|---|---|---|
| `Academy_Kineton_CAPL_20_04_21` | CAPL part 1 (58 slides) | What CAPL is and where it lives inside CANoe/CANalyzer; the CAPL Browser; syntax and semantics — data types, declarations, constants, casting, arrays, strings; the full operator set; control statements; events and event procedures; timers |
| `Academy_Kineton_CAPL2_22_04_21` | CAPL part 2 (36 slides) | Symbolic access to signals and messages (why `EngineSpeed` beats `0x1A0.byte(2)`); panels; environment variables — and the important warning that they are for panel-to-node communication, **not** for node-to-node data exchange; the function toolbox (`getValue()`, `setBtr()`, logging and math functions, `write()`); how the CANoe system clock behaves when a measurement starts |

Read them **in order** — part 2 assumes you're fluent with the event-procedure
model from part 1 and builds straight on top of it.

!!! note "Overlap is a feature, not a bug"
    Yes, these decks repeat material from the main article. That's the point.
    When a concept didn't click the first time — say, the difference between a
    timer *variable* and a timer *event procedure*, or what `this` means inside
    `on message` — hearing it explained differently is usually what unblocks
    it. Treat part 1 as a revision pass and part 2 as your bridge from syntax
    to real simulations.

## ORC.zip — a real CANoe project to dissect

Reading about CAPL is one thing; reading a working configuration is where it
becomes intuition. `ORC.zip` is a complete **CANoe configuration for the P520
platform (Jeep Renegade)** — the kind of project you'd be handed on day one at
an OEM or Tier-1. Unpack it, open the `.cfg` file in CANoe, and explore:

| File type | Examples | What it does |
|---|---|---|
| Databases | `P520MY_C1-CAN_R1_01272017_E2A.dbc`, `P520MY_C2-CAN_R1_01272017_E2A.dbc` | DBC (Database CAN) network descriptions for the vehicle's two CAN buses — they decode raw frames into named, scaled signals |
| CAPL source | `P520MY_CAN_R1_01272017_E2A.can` | The CAPL node program(s) that simulate ECU behavior |
| Panels | `P520_E3A_R7_CAN.cbf`, `P520MY_CAN_R1_01272017_E2A.cbf` | Panel Editor panels with switches, LEDs and tell-tales — your "dashboard" for driving the simulation |
| Configurations | `P520_E3A_R7_CAN.cfg`, `P520_E3A_R7_CAN_8.2.cfg`, `.stcfg` | The CANoe configuration files that tie buses, nodes, panels and databases together |
| Panel graphics | `icone/` (`chiave2stati.png`, `L_green_red.png`, `Renegade.png`, …) | Bitmaps behind the panel controls — 2/3-state switches, warning lamps, the vehicle image |

The thing to notice while exploring is the data flow — this is the pattern
you'll recreate in your own projects:

```mermaid
flowchart LR
    P["Panel switch<br/>(.cbf panel)"] -->|writes| E[Environment variable]
    E -->|triggers| C["on envVar event<br/>CAPL node (.can)"]
    C -->|sets signals| D["Message object<br/>(from DBC)"]
    D -->|output()| B(("CAN bus<br/>C1 / C2"))
    B -->|feeds| T[Trace & other nodes]
```

!!! tip "Your 20-minute tour"
    Load `P520_E3A_R7_CAN.cfg` in CANoe and open the Simulation Setup. The
    pencil icon on a network node means it carries a CAPL program — double-click
    it to open the `.can` file in the CAPL Browser. Then pick one panel switch
    and follow it end to end: which environment variable it writes, which
    `on envVar` handler reacts, which signals get set, and which message goes
    out on the bus. Doing this once with a real project teaches you more than
    re-reading any deck.

!!! warning "Confidential content"
    The DBC files in this archive are proprietary OEM network specifications.
    Use them for local training only — do not share or publish them.

!!! success "Key takeaways"
    - This page is your deepening shelf, not a new exam topic — dip in whenever
      a CAPL idea needs a second explanation.
    - The [WIP](wip/index.md) decks re-teach CAPL the way an instructor does:
      fundamentals in part 1, symbolic access, panels and functions in part 2.
      Read them in order.
    - `ORC.zip` is a full P520/Renegade CANoe project — two DBCs, CAPL source,
      panels, configurations. Open it and trace one switch all the way to a bus
      frame.
    - You now have the pattern that powers every CANoe simulation: panel →
      environment variable → CAPL event procedure → signals → CAN frame.

## Sub-sections

- [WIP](wip/index.md)

## Downloads

- :material-file: [ORC](../../../assets/mil2/14_CAPL/CAPL_Other/ORC.zip) — 886.8 KB
