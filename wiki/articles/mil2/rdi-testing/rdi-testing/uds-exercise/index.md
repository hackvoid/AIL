# UDS Exercise

This hands-on exercise closes the RDI Testing lessons on diagnostics: you first
**write scripts that simulate an ECU answering UDS requests**, then you **read
real request/response traces line by line and hunt down the errors planted in
them**. It is where the theory from [Diagnosis](../../../diagnosis/index.md) —
services, sessions, negative responses, multi-frame transport — stops being a
table in a slide deck and becomes something you can produce and debug yourself.

## Goal

- Build the request/response pairs for the core UDS services by hand:
  `ReadDataByIdentifier` (0x22), `WriteDataByIdentifier` (0x2E),
  `ReadDTCInformation` (0x19), `RoutineControl` (0x31) and
  `DiagnosticSessionControl` (0x10).
- Apply the diagnostic session rules while doing it.
- Explain multi-frame (ISO-TP) transfers with consecutive frames.
- Analyze complete traces, including a full `SecurityAccess` (0x27)
  seed & key sequence, and identify protocol-level mistakes.

## What you need to remember

### UDS message anatomy

Every diagnostic exchange is a request from the **tester** and a reply from the
**ECU**:

- A request starts with the **Service Identifier (SID)**.
- A **positive response** echoes `SID + 0x40` (e.g. `22` → `62`).
- A **negative response** is always `7F <SID> <NRC>` — three bytes, where NRC is
  the Negative Response Code telling you *why* the request was refused.

| NRC | Name | When you see it |
|---|---|---|
| 0x13 | incorrectMessageLengthOrInvalidFormat | Wrong number of bytes in the request |
| 0x24 | requestSequenceError | Steps executed in the wrong order |
| 0x31 | requestOutOfRange | Unknown DID/RID or bad parameter value |
| 0x33 | securityAccessDenied | Service locked behind SecurityAccess |
| 0x35 | invalidKey | Wrong key sent during SecurityAccess |
| 0x7F | serviceNotSupportedInActiveSession | Service not allowed in the current session |

### Session control rules

The exercise uses these transition rules (footnote (1) of the exercise sheet):

```mermaid
stateDiagram-v2
    [*] --> Default
    Default --> Extended: 10 03
    Extended --> Programming: 10 02
    Extended --> Default: 10 01
    Programming --> Default: 10 01
    note right of Programming
        Reachable only from Extended,
        never directly from Default
    end note
```

- Default → Extended is allowed; **Programming is reachable only from Extended**.
- **Default can always be reached**, from any session.

### Multi-frame messages (ISO-TP)

When a diagnostic payload does not fit in one CAN frame, ISO-TP splits it:

```mermaid
sequenceDiagram
    participant T as Tester
    participant E as ECU
    T->>E: First Frame (PCI 0x1N): total length + first bytes
    E->>T: Flow Control (PCI 0x30): block size + separation time
    T->>E: Consecutive Frame (PCI 0x21): bytes 7..13
    T->>E: Consecutive Frame (PCI 0x22): bytes 14..20
    Note over T,E: CF sequence number rolls 0x21..0x2F, then wraps to 0x20
```

The high nibble of the first byte identifies the frame type: `0` = single frame,
`1` = first frame, `2` = consecutive frame, `3` = flow control.

## Setup

- **CANalyzer** (or CANoe) with a diagnostic-capable configuration — the same
  environment used in the [CANalyzer](../../../canalyzer/index.md) lessons.
- The diagnostic description **CDD file** for the target ECU
  (`D2956_IPC_E2A_R10_332BEV.cdd` — the instrument panel cluster of the 332 BEV
  platform), loaded into the configuration so requests are interpreted as
  services and DIDs instead of raw bytes.
- A **CAPL script** implementing a simulated ECU node (the [CAPL](../../../capl/index.md)
  lessons cover the language): on each incoming diagnostic request the script
  builds and sends the required response.

## Part 1 — Build the conversations

Write the script (and the byte sequences it exchanges) for each scenario.

**1. Read vehicle speed from DID `AA AA`.**
The tester sends a `ReadDataByIdentifier` for the DID, the ECU answers
positively with the speed set to 100 km/h:

| Direction | Bytes | Meaning |
|---|---|---|
| Tx | `22 AA AA` | Read DID 0xAAAA |
| Rx | `62 AA AA 64` | Positive response; 0x64 = 100 km/h (1 km/h per unit) |

**2. Write `XX XX` to DID `BB BB` — allowed only in the Extended session.**
You must change the session first, otherwise the ECU should reject the write
with NRC 0x7F (serviceNotSupportedInActiveSession):

| Direction | Bytes | Meaning |
|---|---|---|
| Tx | `10 03` | Switch to Extended session |
| Rx | `50 03` | Session changed |
| Tx | `2E BB BB XX XX` | Write DID 0xBBBB |
| Rx | `6E BB BB` | Positive response echoes SID+0x40 and the DID |

**3. Ask how many DTCs are stored.**
Use `ReadDTCInformation` with subfunction 0x01
(reportNumberOfDTCByStatusMask) and a status mask of `FF` (any status). The
positive response carries the availability mask, the DTC format and the 2-byte
count — here, 4 DTCs:

| Direction | Bytes | Meaning |
|---|---|---|
| Tx | `19 01 FF` | Count DTCs matching any status |
| Rx | `59 01 FF 01 00 04` | Mask FF, format 0x01, count = 0x0004 (4 DTCs) |

**4. Start routine `CC CC` — expect a negative response for wrong length.**
Send a malformed `RoutineControl` start request (e.g. missing routine control
option bytes) and answer with NRC 0x13:

| Direction | Bytes | Meaning |
|---|---|---|
| Tx | `31 01 CC CC` | startRoutine, RID 0xCCCC, length not as expected |
| Rx | `7F 31 13` | incorrectMessageLengthOrInvalidFormat |

**5. Explain consecutive frames.**
Give an example where a response longer than 7 bytes is split: the ECU sends a
First Frame announcing the total length, the tester returns a Flow Control, and
the remaining bytes travel in Consecutive Frames numbered 0x21, 0x22, … (see the
diagram above).

## Part 2 — Read the traces, find the mistakes

Each trace below is printed exactly as given in the exercise. For every line
say what it means, then decide whether it is correct; if not, state what the
bytes should have been.

### Trace 1 — read, write, read again

| Dir | Bytes |
|---|---|
| Tx | `22 F1 AB` |
| Rx | `62 F1 AB 04` |
| Tx | `2E F1 AB 07` |
| Rx | `6E F1 AB` |
| Tx | `22 F1 AB` |
| Rx | `62 F1 AB 04` |

What to check: the ECU stores DID 0xF1AB = 0x04, the tester overwrites it with
0x07 and reads it back. Is the final response consistent with the write that
just succeeded?

### Trace 2 — a refused read

| Dir | Bytes |
|---|---|
| Tx | `22 F1 8` |
| Rx | `7F 22 33` |

What to check: NRC 0x33 means securityAccessDenied — but first look at the
request itself: a DID is always **two** bytes. Is the request even well formed,
and would 0x33 (or rather 0x13) be the right refusal?

### Trace 3 — SecurityAccess seed & key

| Dir | Bytes |
|---|---|
| Tx | `22 AA AA` |
| Rx | `7F 22 24 33` |
| Tx | `27 11` |
| Rx | `67 12 SS SS SS SS` |
| Tx | `27 12 KK KK KK KK` |
| Rx | `7F 27 35` |
| Tx | `27 11 SS SS SS SS` |
| Rx | `67 11 SS SS SS SS` |
| Tx | `27 12 KK KK KK KK` |
| Rx | `27 11` |
| Tx | `67 11 00 00 00 00` |
| Rx | `22 AA AA` |
| Tx | `62 AA AA XX` |

This trace is full of planted errors. The correct seed & key flow is:

1. Tester requests the seed: `27 <odd subfunction>`, e.g. `27 11` — **no extra
   data bytes**.
2. ECU replies `67 <same subfunction> <seed>`.
3. Tester computes the key and sends it: `27 <subfunction+1> <key>`.
4. ECU validates and replies `67 <subfunction+1>`; on a wrong key it answers
   `7F 27 35` (invalidKey).

Compare the trace against this flow and check at least:

- the negative response after the first read (how many NRC bytes are there?),
- the subfunction echoed in the first seed response (`67 12` after a `27 11`
  request?),
- the second seed request, which carries unexpected payload bytes,
- the reply to the second key attempt — does a request ever get answered by
  another request?
- the last three lines: who is the tester and who is the ECU here?

### Trace 4 — session control

| Dir | Bytes |
|---|---|
| Tx | `10 01` |
| Rx | `50 01` |
| Tx | `10 03` |
| Rx | `50 03` |

What to check: against the session rules (Default is always reachable; Extended
from Default; Programming only from Extended), is this sequence legal?

## Common mistakes

- Forgetting the **session precondition**: writing a DID that requires the
  Extended session while still in Default — the ECU must answer `7F 2E 7F`.
- Mixing up the subfunction echo in SecurityAccess: `requestSeed` uses the odd
  level (0x11), `sendKey` uses level+1 (0x12), and the positive response must
  echo the **same** subfunction as the request.
- Negative responses with more or fewer than three bytes — the format is fixed:
  `7F <SID> <NRC>`.
- Role confusion in traces: requests (0x22, 0x27, 0x10…) come from the tester,
  responses (0x62, 0x67, 0x50, 0x7F…) from the ECU. Any line breaking that is
  an error.
- Miscounting DID length: a DID is two bytes, so `22 F1 8` is not a valid
  request.
- Consecutive-frame numbering errors: CF sequence numbers start at 0x21 and
  wrap after 0x2F back to 0x20.

!!! success "Key takeaways"
    - Positive response = SID + 0x40; negative response = `7F SID NRC`, always
      three bytes — learn the common NRCs (0x13, 0x33, 0x35, 0x7F) by heart.
    - Session transitions are constrained: Programming only from Extended,
      Default from anywhere; services may be refused per session.
    - SecurityAccess is strictly requestSeed (odd level) → sendKey (level+1),
      and responses echo the request's subfunction.
    - Payloads over 7 bytes ride ISO-TP: First Frame, Flow Control, then
      Consecutive Frames 0x21…0x2F.
    - Reading a trace means checking *every* byte: direction, SID, subfunction,
      length, and consistency with what happened before.
