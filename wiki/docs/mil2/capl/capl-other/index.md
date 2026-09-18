# CAPL — Additional Material

This section collects **supplementary CAPL material** that does not belong to the
main lecture track. You should already be comfortable with the core language —
event procedures, message objects, timers, and symbolic access — covered in the
[CAPL](../index.md) topic and practiced in the [CAPL exercises](../capl-exercise/index.md)
before spending time here.

Two things live in this section:

- a **WIP sub-section** with the slide decks from two live CAPL training
  sessions, and
- **`ORC.zip`**, a complete sample CANoe project you can open and dissect.

## WIP — recorded session decks

The [WIP](wip/index.md) sub-section contains the decks from two classroom
sessions held in April 2021. They overlap with the main CAPL lectures but are
worth reading because they present the language in the order an instructor
actually teaches it, with extra emphasis on syntax pitfalls.

| Deck | Session | Contents |
|---|---|---|
| `Academy_Kineton_CAPL_20_04_21` | CAPL part 1 (58 slides) | What CAPL is and where it sits in CANoe/CANalyzer; the CAPL Browser; syntax and semantics (data types, declarations, constants, casting, arrays, strings); operators; control statements; events and event procedures; timers |
| `Academy_Kineton_CAPL2_22_04_21` | CAPL part 2 (36 slides) | Symbolic access to signals and messages; panels; environment variables and why they must not be used for node-to-node data exchange; CAPL functions (`getValue()`, `setBtr()`, logging, math functions, `write()`); the CANoe system clock |

Suggested order: **part 1 first, then part 2** — part 2 explicitly builds on the
event-procedure model introduced in part 1.

!!! note "Overlap is intentional"
    These decks repeat ground already covered by the main CAPL article. Treat
    them as a revision pass: if a concept was unclear the first time (for
    example the difference between a timer variable and a timer event
    procedure, or the `this` keyword inside `on message`), the alternative
    explanation here often unblocks it.

## ORC.zip — sample CANoe project

`ORC.zip` is a real, working **CANoe configuration for the P520 platform**
(Jeep Renegade). Unpack it and open the `.cfg` file in CANoe to see how a
production-style simulation is assembled. Inside you will find:

| File type | Examples | What it is |
|---|---|---|
| Databases | `P520MY_C1-CAN_R1_01272017_E2A.dbc`, `P520MY_C2-CAN_R1_01272017_E2A.dbc` | DBC network databases for the two CAN buses of the vehicle |
| CAPL source | `P520MY_CAN_R1_01272017_E2A.can` | The CAPL node program(s) driving the simulation |
| Panels | `P520_E3A_R7_CAN.cbf`, `P520MY_CAN_R1_01272017_E2A.cbf` | Panel Editor panels (switches, LEDs, tell-tales) |
| Configurations | `P520_E3A_R7_CAN.cfg`, `P520_E3A_R7_CAN_8.2.cfg`, `.stcfg` | CANoe configuration files tying buses, nodes, panels and databases together |
| Panel graphics | `icone/` (`chiave2stati.png`, `L_green_red.png`, `Renegade.png`, …) | Bitmaps used by the panel controls (2/3-state switches, warning lamps, vehicle image) |

!!! tip "How to use it"
    Load `P520_E3A_R7_CAN.cfg` in CANoe, open the Simulation Setup to see which
    network nodes carry a CAPL program (the pencil icon on the node), then open
    the `.can` file in the CAPL Browser and follow how panel switches write
    environment variables and how the node reacts. It is the fastest way to see
    panels, environment variables and CAPL event procedures working together on
    a real vehicle network.

!!! warning "Confidential content"
    The DBC files in this archive are proprietary OEM network specifications.
    Use them for local training only — do not share or publish them.

!!! success "Key takeaways"
    - This section is optional deepening material, not a new topic.
    - The [WIP](wip/index.md) decks re-teach CAPL fundamentals (part 1) and
      symbolic access, panels and functions (part 2) — read them in order.
    - `ORC.zip` is a complete P520/Renegade CANoe project: two DBCs, CAPL
      source, panels and configurations — open it to see everything connected.

## Sub-sections

- [WIP](wip/index.md)

## Downloads

- :material-file: [ORC](../../../assets/mil2/14_CAPL/CAPL_Other/ORC.zip) — 886.8 KB
