# CANalyzer Exercise — Trace Filters & IG Stimulation (Cluster)

Time to get your hands on the bus. In this exercise you will put the whole
CANalyzer analysis chain to work on the **instrument panel cluster (IPC)** of
the P332 battery electric vehicle (BEV) platform — the ECU that drives the
warning lamps behind your steering wheel.

By the end, you'll be able to build a two-channel measurement setup, filter a
busy bus down to just the messages you care about, impersonate other ECUs with
the Interactive Generator (IG) block, and *prove* — with timestamps and
screenshots — that the cluster reacts to failure states exactly as the network
specification says it should. This is the day-to-day workflow of every E/E
test engineer, so the skills transfer directly to your first real project.

## Goal

Work through six steps and come out able to:

- configure **one Trace window per CAN channel** with channel-specific
  pass/stop filters,
- **stimulate signals** with the IG block and confirm them in a Graphic window,
- verify **closed-loop behavior**: a stimulated input signal must produce the
  expected output signal from the IPC,
- **log selected traffic** and replay it in offline mode to measure time
  deltas,
- document your work in a report with screenshots of every step.

**What you'll practice:** filtering, stimulation, stimulus–response
verification, logging, and offline time analysis — the five core moves of
bus-level testing.

## Setup

| Item | Details |
|---|---|
| Tool | Vector CANalyzer |
| Databases | `P332BEV_BH_CAN_...E2A_plus_CR14698_14830_14888.dbc` (BH channel), `P332BEV_C1_CAN_...E2A_plus_CR14698_14830_14888.dbc` (C1 channel) |
| Channels | CAN 1 = BH (body high), CAN 2 = C1 |
| Stimulation | IG (Interactive Generator) block |
| Analysis | Trace windows, Graphic windows, logging block, offline mode |

The two **DBC (Database CAN)** files describe the same vehicle platform on two
different CAN channels. Assign each database to its own channel so that message
names, signals and value tables decode correctly in the trace — with no
database attached, a trace is just raw identifiers and hex bytes.

!!! tip "Screenshot everything"
    This exercise is graded on evidence: after each step, paste a screenshot of
    the relevant window into your report document. Do it as you go — hunting
    for proof at the end always costs more time than it saves.

## Step 1 — Per-channel Trace windows and filters

Create **two Trace blocks** in the measurement setup, one per channel, and name
them `Trace BH` and `Trace C1`. Then give each one a different filter policy:

- **Trace BH → pass filter for IPC.** Show *only* messages transmitted or
  received by the IPC node. This is the classic "watch one ECU" setup you will
  reach for constantly when debugging a single controller on a busy bus.
- **Trace C1 → stop filter for BSM.** *Drop* all messages transmitted by the
  BSM node and leave everything else visible — the standard trick for silencing
  a chatty node that would otherwise flood your trace.

```mermaid
flowchart LR
    subgraph BH["CAN channel BH"]
        BHBUS[("BH bus")] --> F1{"Pass filter:<br>only IPC Tx/Rx"}
        F1 --> T1[Trace BH window]
    end
    subgraph C1["CAN channel C1"]
        C1BUS[("C1 bus")] --> F2{"Stop filter:<br>drop BSM Tx"}
        F2 --> T2[Trace C1 window]
    end
```

!!! warning "Pass vs. stop filter"
    A **pass filter** is a whitelist: only matching messages get through. A
    **stop filter** is a blacklist: matching messages are discarded and all
    others pass. Swapping the two is the most common reason a trace shows
    "nothing" or "everything" — if your window looks wrong, check the filter
    type first.

## Step 2 — Stimulate signals with the IG block

Add an **IG block** to the measurement setup and configure it to transmit these
four signals:

| Message | Signal | Value | Meaning |
|---|---|---|---|
| `AIRBAG1` | `AirBagFailSts` | `1` | Fail_not_Present_Lamp_Flashing |
| `BRAKE1` | `VehicleSpeedVSOSignal` | `40 km/h` | Vehicle speed |
| `BCM_COMMAND` | `CmdIgnSts` | `RUN` | Ignition in RUN |
| `ENGINE1` | `PowertrainPrplsnActv` | `1` | Powertrain propulsion active |

Notice the pattern: you are building a **plausible vehicle state** — ignition
on, powertrain active, vehicle rolling at 40 km/h — and then injecting an
airbag failure on top. This is not arbitrary: ECUs like the IPC often gate
their behavior on the ignition and speed signals, so a "failure" injected into
a car that looks switched off will simply be ignored.

## Step 3 — Verify the stimulation in a Graphic window

Before trusting any response, trust your stimulus. Open a **Graphic window**,
drag in the four signals above, and check that each trace settles on the value
you set in the IG block: `AirBagFailSts = 1`, speed at 40 km/h,
`CmdIgnSts = RUN`, `PowertrainPrplsnActv = 1`.

This confirms the IG block is actually transmitting and the DBC decodes the
frames as expected. Experienced engineers *always* verify the stimulus before
judging the system's reaction to it — it saves you from debugging a fault that
lives in your test setup, not in the ECU.

## Step 4 — Closed-loop checks: how the IPC reacts

Now the real test. The IPC listens to failure-status signals from other ECUs
and drives its lamp-status signals in the `CLUSTER2` message accordingly.
Stimulate each input with the IG block and watch the IPC answer in a Graphic
window:

| Stimulated input (IG) | Expected IPC response |
|---|---|
| `AIRBAG1.AirBagFailSts = 0` | `CLUSTER2.AirBagLamp_FailSts = 0` |
| `AIRBAG1.AirBagFailSts = 1` | `CLUSTER2.AirBagLamp_FailSts = 3` |
| `BRAKE8.ABSFailSts = 1` | `CLUSTER2.ABSLamp_FailSts = 2` |

```mermaid
sequenceDiagram
    participant IG as IG block (tester)
    participant IPC as IPC ECU
    participant GW as Graphic window
    IG->>IPC: AIRBAG1.AirBagFailSts = 1
    IPC-->>GW: CLUSTER2.AirBagLamp_FailSts = 3
    IG->>IPC: BRAKE8.ABSFailSts = 1
    IPC-->>GW: CLUSTER2.ABSLamp_FailSts = 2
```

This is the essence of **stimulus–response testing**: you impersonate one ECU
(the airbag or brake controller) and check that another ECU (the cluster)
translates the failure status into the correct lamp command. The encoded
values (`0`, `2`, `3`) come from the value tables in the DBC — e.g. `3` for
the airbag lamp means "lamp flashing" rather than a simple on/off, which is
why a raw on/off expectation would mislead you.

## Step 5 — Logging and offline time analysis

1. Pick **10 signals**, each from a *different* message, and configure a
   **logging block** so only those signals are recorded (reuse a pass filter
   to restrict the log).
2. Start the measurement and the log, then **change the signals one at a
   time** in the IG block while logging.
3. Stop, switch CANalyzer to **offline mode**, and load the log file as the
   source. Step through the trace and read the timestamps of your edits.
4. Measure the delta times between signal changes:
   - first change → third change: expected **Δt ≈ 4.35 s**,
   - first change → last change: expected **Δt ≈ 9.16 s**.

Your exact deltas depend on how fast you clicked, so don't chase the numbers —
landing in this ballpark means you did it right. The real goal of this step is
learning to read absolute and relative timestamps in an offline trace, a skill
you will use in every real log analysis from here on.

## Step 6 — Report

Assemble a single report with the screenshot evidence and measured values for
every step: the two filtered traces, the IG configuration, the Graphic-window
verifications, the logged file, and the two delta-time measurements. Treat it
as a rehearsal for real test documentation — "it worked on my screen" is not
evidence.

## Common mistakes

- **Wrong filter type** — using a stop filter where a pass filter is needed
  (or vice versa) in Step 1; the trace then shows everything or nothing.
- **DBC on the wrong channel** — BH and C1 databases swapped, so signals
  decode to garbage or not at all.
- **Trusting the IG without checking** — skipping the Graphic-window
  verification in Step 3, then wondering why the IPC does not react (the IG
  generator may not even be started).
- **Unrealistic vehicle state** — forgetting `CmdIgnSts = RUN`; many ECUs
  ignore failure inputs when the ignition is off.
- **Logging the whole bus** — the exercise wants a log containing *only* the
  10 chosen signals; without a filter, offline analysis becomes a
  needle-in-a-haystack search.
- **Reading absolute time instead of delta** — Step 5 wants the *difference*
  between timestamps, not the timestamps themselves.

!!! success "Key takeaways"
    - One Trace window per channel keeps multi-bus analysis readable; pass
      filters whitelist, stop filters blacklist.
    - The IG block lets you impersonate ECUs: stimulate a realistic vehicle
      state (ignition RUN, speed 40 km/h) plus the failure you want to test.
    - Always verify the stimulus in a Graphic window before judging the
      response — you've now got the habit that separates fast debuggers from
      frustrated ones.
    - Closed-loop check passed? `AirBagFailSts = 1` →
      `CLUSTER2.AirBagLamp_FailSts = 3` and `ABSFailSts = 1` →
      `CLUSTER2.ABSLamp_FailSts = 2` mean you just ran a real
      stimulus–response test.
    - Log only what you need, then use offline mode to measure delta times
      (≈ 4.35 s and ≈ 9.16 s between your edits) — you're ready for real log
      analysis.

---

## Source material

This article was distilled from the academy lesson materials:

- :material-file-pdf-box: [CANalyzer Exercise IGTrace](../../../../assets/mil2/12_CANalyzer/CANalyzer_Exercise/CANalyzer_Exercise_IGTrace/CANalyzer_Exercise_IGTrace.pdf) — PDF, 103.8 KB

## Downloads

- :material-file: [P332BEV BH CAN R1 20200902 E2A plus CR14698 14830 14888](../../../../assets/mil2/12_CANalyzer/CANalyzer_Exercise/CANalyzer_Exercise_IGTrace/P332BEV_BH_CAN_R1_20200902_E2A_plus_CR14698_14830_14888.dbc) — 457.8 KB
- :material-file: [P332BEV C1 CAN R1 20200902 E2A plus CR14698 14830 14888](../../../../assets/mil2/12_CANalyzer/CANalyzer_Exercise/CANalyzer_Exercise_IGTrace/P332BEV_C1_CAN_R1_20200902_E2A_plus_CR14698_14830_14888.dbc) — 388.8 KB
