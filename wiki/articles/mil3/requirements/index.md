# Requirements Management

Every ECU project starts long before anyone writes a line of code or wires up a
HIL rig: it starts with **requirements** — the formal statements of what the
system must do and how well it must do it. In the automotive industry,
requirements are not an informal to-do list. They are contract-relevant
engineering artifacts that are elicited, analyzed, reviewed, versioned and
traced through the whole development lifecycle.

This article covers the three pillars you need for the rest of MIL3 and MIL4:

- **Automotive SPICE (ASPICE)** — the process framework that defines *who*
  produces requirements and *how* their quality is assessed,
- **the anatomy of a good requirement** — the quality rules every single
  requirement must satisfy,
- **IBM Rational DOORS** — the industry-standard tool used to store, structure
  and trace requirements in real projects.

## Automotive SPICE

**Automotive SPICE** (Software Process Improvement and Capability
dEtermination) is a domain-specific variant of the international standard
**ISO/IEC 15504 (SPICE)**. Its purpose is to **improve and evaluate the
development processes of ECU suppliers** in the automotive industry: when an
OEM audits a supplier, the ASPICE model defines which processes are examined
and how their capability is rated.

ASPICE organizes its processes onto the V-model you already know from
[the V-Cycle](../../mil1/v-cycle/index.md). Three of them sit at the very top
of the left leg and define the requirements chain:

![ASPICE process groups on the V-model: requirement elicitation (SYS.1), system requirements analysis (SYS.2) and software requirements analysis (SWE.1)](img/aspice-v-model.webp)

| Process | Name | What it does |
|---|---|---|
| **SYS.1** | Requirements Elicitation | Gather, process and track evolving stakeholder needs and requirements throughout the product lifecycle |
| **SYS.2** | System Requirements Analysis | Transform the defined stakeholder requirements into a set of system requirements that will guide the design of the system |
| **SWE.1** | Software Requirements Analysis | Transform the software-related parts of the system requirements into a set of software requirements |

The key idea is **progressive refinement with traceability**: each level
transforms the level above it, and every derived requirement must be linkable
back to its parent.

```mermaid
flowchart TD
    A["Stakeholder needs<br/>(SYS.1 elicitation)"] --> B["System requirements<br/>(SYS.2 analysis)"]
    B --> C["Software requirements<br/>(SWE.1 analysis)"]
    C --> D["Software architecture &amp; unit design<br/>(SWE.2 / SWE.3)"]
    A -. "traced to" .-> B
    B -. "traced to" .-> C
    C -. "verified by" .-> E["Tests<br/>(SWE.4–SWE.6, SYS.4–SYS.5)"]
```

!!! note "Why you care as a test engineer"
    ASPICE traceability is bidirectional: a requirement must trace *down* to
    design and code, and every requirement must be *verifiable* by a test or
    analysis on the right leg of the V. When you later write test cases in the
    [Test Cases](../testcases/index.md) lesson and run them in
    [Verification](../../mil4/verification/index.md), each test will reference
    the requirement IDs it covers.

## Functional vs. non-functional requirements

Requirements come in two fundamental flavors:

- **Functional requirements** — what the system **shall do**. Example: "If the
  driver presses the brake pedal, the brake lights shall illuminate."
- **Non-functional requirements** — what the system **shall be**: qualities and
  constraints such as timing, memory consumption, temperature range,
  reliability, maintainability or compliance with a standard. Example: "The
  function shall execute within 10 ms" or "The ECU shall operate from −40 °C to
  +85 °C."

Both kinds must follow the same quality rules below — a vague non-functional
requirement ("the system shall be fast") is just as defective as a vague
functional one.

## Anatomy of a good requirement

A requirement is only useful if it can be understood one way, built within
real constraints, and proven at the end. Six characteristics define a
well-formed requirement:

| Characteristic | Rule |
|---|---|
| **Clear and unambiguous** | Only one way to interpret it |
| **Testable (verifiable)** | Can be checked by inspection, analysis, demonstration or test |
| **Feasible** | Doable within existing constraints (cost, timing, technology) |
| **Consistent** | No conflicts with other requirements; avoid redundancy |
| **Atomic** | A single statement — no conjunctions bundling several requirements |
| **Traceable** | Its level and its correlation with other requirements are known |

The easiest way to internalize these is through bad → good rewrites.

### Clear and unambiguous

> ❌ *The system shall not accept password longer than 15 characters.*

What does "not accept" mean — ignore it? truncate it? crash? A reader can
interpret this in several ways. The fixed version states the observable
behavior:

> ✅ *If the user inserts a password longer than 15 characters, then the system
> shall display an error message and shall ask the user to correct it.*

### Testable

> ❌ *The system must refresh the data reasonably quickly.*

"Reasonably quickly" cannot be verified by anyone. A requirement is testable
only if it contains a measurable criterion:

> ✅ *The system must refresh the data each 0.5 ms.*

There are four recognized verification methods: **inspection** (review the
artifact), **analysis** (calculate or simulate), **demonstration** (operate and
observe) and **test** (stimulate with defined inputs and compare outputs). Pick
the method per requirement — and write the requirement so that at least one
method applies.

### Feasible

> ❌ *The replacement control system shall be installed with no disruption of
> the production.*

Zero disruption is usually physically impossible, so the requirement sets the
project up to fail. A feasible version quantifies what the business can
actually accept:

> ✅ *The replacement control system shall be installed causing no more than
> 2 days of production disruption.*

### Consistent

Requirements must not contradict each other. In this pair, REQ2 silently
forbids exactly what REQ1 demands:

> ❌ REQ1: *If A != B, then initialization shall be triggered.*
> ❌ REQ2: *The request for initialization shall be sent permanently with the
> value 0 ('kein_init').*

The conflict is resolved by keeping the single, agreed behavior:

> ✅ *The request for initialization shall be sent permanently with the value
> 0 ('kein_init').*

!!! warning "Redundancy is also a consistency problem"
    If the same behavior is stated in two places, a later change to one copy
    creates a hidden contradiction. Say it once, link to it everywhere.

### Atomic

Conjunctions are a smell. One requirement, one statement:

> ❌ *In case of overtemperature, overcurrent and overvoltage the system shall
> abort the charge.*

Split it so each condition can be traced, implemented and tested individually:

> ✅ REQ1: *In case of overtemperature the system shall abort the charge.*
> ✅ REQ2: *In case of overcurrent the system shall abort the charge.*
> ✅ REQ3: *In case of overvoltage the system shall abort the charge.*

### Traceable

It must always be possible to know **which level a requirement belongs to**
(stakeholder, system, software) and **how it correlates with other
requirements** — which parent it refines, which siblings it depends on, and
which tests verify it. Traceability is not a property of the sentence but of
the requirement *management*: it lives in the tool, which brings us to DOORS.

## Managing requirements in IBM Rational DOORS

**IBM Rational DOORS** (Dynamic Object-Oriented Requirements System) is the
de-facto standard requirements management tool in the automotive industry. A
Word document or Excel sheet cannot maintain thousands of linked, versioned
requirements — DOORS can.

### The data hierarchy

DOORS organizes a database into three levels you will see immediately in its
two main windows:

![DOORS main views: the database explorer (projects and formal modules) and an open formal module showing requirement objects with their attributes](img/doors-main-views.webp)

| Level | What it is |
|---|---|
| **Project / folder** | A container in the database explorer, grouping related work (e.g. one vehicle project) |
| **Formal module** | A structured document inside a project — e.g. "User Requirements", "System Requirements", "Verification Methods" |
| **Object** | One row inside a formal module: a requirement, a heading, or explanatory text |

Each object carries an absolute number, a heading hierarchy (the numbered
outline you see in the module), and a set of **attributes**.

### Attributes

Attributes characterize every requirement object, support the process, and
allow efficient, rational administration of large requirement sets. Typical
attributes include the object ID, status, priority, verification method, and
any **customized attributes** your project defines (e.g. "ASIL", "Variant",
"Source"). DOORS distinguishes:

- **predefined attributes** — built-in system data (creation date, author,
  absolute number, …),
- **customized attributes** — project-specific columns with defined types
  (enumeration, integer, date, text, …).

Attributes are also scriptable: DOORS ships with its own extension language,
**DXL**, which is used for automation such as loading a standard view onto the
current module:

```text
Module m = current
Object o = current
Filter f
load view "Standard view"
```

### Filtering

To work inside a module of 5 000 requirements you need filters. DOORS can
filter objects by:

- names and IDs,
- **links through modules** (e.g. show only objects linked to a given test
  module),
- wildcards and full **regular expressions**,
- predefined and customized attribute values,

and multiple conditions can be combined in one filter.

!!! warning "Filters have no memory"
    A DOORS filter is not saved as part of the module by default — close the
    module and your carefully built multi-condition filter is gone. Save your
    working configurations as named **views** so they survive (and so they can
    be used for exports).

### Baselines, links and history

The features that make DOORS a *management* tool rather than a text editor:

- **Links for traceability** — objects in one module link to objects in
  another (system requirement → software requirement → test case). DOORS
  visualizes and analyzes link coverage, and can report orphan requirements or
  tests that verify nothing.
- **Baselines** — immutable snapshots of a module at a defined point (e.g.
  "System Requirements v3.3" released to the supplier). You can always diff
  the current state against any baseline.
- **Defined views for exports** — saved column/filter/sort configurations,
  used to generate consistent documents for reviews and customers.
- **Easy import/update of attributes** — bulk changes (e.g. setting a new
  status on hundreds of objects) via import instead of manual editing.
- **History** — every change to every object is recorded with author and
  timestamp, so audits can reconstruct who changed what and when.

```mermaid
flowchart LR
    subgraph DOORS database
        M1["Module:<br/>Stakeholder reqs"] -->|"link"| M2["Module:<br/>System reqs"]
        M2 -->|"link"| M3["Module:<br/>Software reqs"]
        M3 -->|"link"| M4["Module:<br/>Test cases"]
    end
    M2 -.->|"baseline v3.3"| B["Frozen release<br/>snapshot"]
```

!!! tip "Practical habit"
    Before editing anything in a shared project, check whether the module is
    baselined and whether a change-management process applies — in many OEM
    projects you may only edit in a working copy, and changes are reviewed
    before they reach the released baseline.

## From requirements to the rest of the bootcamp

Requirements management is the entry point of the whole MIL3/MIL4 chain: the
test cases you will design in [Test Cases](../testcases/index.md) derive their
expected behavior directly from requirement text, and the
[Verification](../../mil4/verification/index.md) and
[Validation](../../mil4/validation/index.md) lessons close the loop by proving
each requirement on the bench or in the vehicle. A requirement that is
ambiguous, untestable or untraceable will surface again as an argument about
test results — which is why the six quality rules above matter to you even if
you never write requirements yourself.

!!! success "Key takeaways"
    - Automotive SPICE (ISO/IEC 15504 for automotive) evaluates ECU supplier
      processes; the requirements chain is SYS.1 elicitation → SYS.2 system
      analysis → SWE.1 software analysis, each level refining the previous one.
    - Functional requirements say what the system *does*; non-functional
      requirements say what it *is* (timing, temperature, memory, …).
    - A good requirement is clear/unambiguous, testable, feasible, consistent,
      atomic and traceable — with a measurable criterion whenever it is
      supposed to be verified.
    - Verification methods: inspection, analysis, demonstration, test.
    - DOORS structures requirements as database → projects → formal modules →
      objects, with attributes, filters, baselines, history and cross-module
      links providing traceability end to end.
