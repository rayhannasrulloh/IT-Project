# Data Flow Diagram (DFD)

Data flow for the **Conversational Data Analyst**. Processes are numbered per DFD
convention, data stores are cylinders, and external entities are rectangles.

## Level 0 — Context Diagram

The whole system as a single process, showing only the external entities and the
data that crosses the system boundary.

```mermaid
flowchart LR
    ANALYST["👤 Business Analyst"]
    ADMIN["👤 Administrator"]
    LLM["☁️ Groq LLM API"]
    AUTH["🔐 Supabase Auth"]

    SYS((("0<br/>Conversational<br/>Data Analyst<br/>System")))

    ANALYST -- "NL question / PDF-CSV upload" --> SYS
    SYS -- "answer + chart + explanation + SQL" --> ANALYST

    ADMIN -- "view logs / run benchmark / manage roles" --> SYS
    SYS -- "stats, audit logs, benchmark scores" --> ADMIN

    SYS -- "prompt + schema context" --> LLM
    LLM -- "generated SQL / explanation" --> SYS

    SYS -- "JWT to verify" --> AUTH
    AUTH -- "decoded identity + role" --> SYS
```

## Level 1a — Conversational Query Path

The core NL→SQL flow: authenticate, understand the question, generate and guard
the SQL, execute it read-only, then explain and chart the result.

```mermaid
flowchart TD
    ANALYST["👤 Business Analyst"]
    AUTH["🔐 Supabase Auth"]
    LLM["☁️ Groq LLM API"]

    P1(["1.0<br/>Authenticate &<br/>Authorize (JWT/RBAC)"])
    P2(["2.0<br/>Manage<br/>Conversation"])
    P3(["3.0<br/>Detect Intent"])
    P4(["4.0<br/>Generate SQL<br/>(+ clarify)"])
    P5(["5.0<br/>Guardrail<br/>Safety Check"])
    P6(["6.0<br/>Execute SQL<br/>(read-only)"])
    P7(["7.0<br/>Explain +<br/>Build Chart"])
    P8(["8.0<br/>Log & Audit"])

    D1[("D1 profiles")]
    D2[("D2 conversations /<br/>messages / context")]
    D3[("D3 business data")]
    D4[("D4 query_logs")]
    D7[("D7 feedback")]

    ANALYST -->|"login token"| P1
    P1 <-->|"verify JWT"| AUTH
    P1 <-->|"profile + role"| D1
    P1 --> P2

    ANALYST -->|"NL question"| P2
    P2 <-->|"history + messages"| D2
    P2 -->|"fresh message"| P3
    P3 -->|"DATA_QUERY"| P4
    P3 -->|"greeting / out-of-scope reply"| P2

    P4 <-->|"pending clarification"| D2
    P4 <-->|"prompt / SQL"| LLM
    P4 -->|"generated SQL"| P5
    P5 -->|"safe SELECT/WITH"| P6
    P5 -->|"blocked"| P8
    P6 <-->|"read rows"| D3
    P6 -->|"result set"| P7
    P7 <-->|"summarize"| LLM
    P7 -->|"answer + Plotly config"| P2
    P7 -->|"outcome"| P8

    P2 -->|"answer + chart + SQL"| ANALYST
    ANALYST -->|"thumbs up/down"| P2
    P2 -->|"rating"| D7
    P8 -->|"audit row"| D4
```

## Level 1b — Documents & Admin Path

Document intelligence (PDF/CSV parsing) and the administrator's oversight
functions: audit logs, RBAC, and the benchmark evaluation.

```mermaid
flowchart TD
    ANALYST["👤 Business Analyst"]
    ADMIN["👤 Administrator"]
    LLM["☁️ Groq LLM API"]

    P9(["9.0<br/>Document<br/>Intelligence"])
    P10(["10.0<br/>Admin Analytics<br/>& Benchmarking"])
    P4b(["4.0<br/>Generate SQL<br/>(agent under test)"])

    D1[("D1 profiles")]
    D4[("D4 query_logs")]
    D5[("D5 benchmark_results")]
    D6[("D6 documents /<br/>extracted_tables / chunks")]

    ANALYST -->|"upload PDF / CSV"| P9
    P9 -->|"parse + extract"| P9
    P9 <-->|"tables + chunks"| D6
    P9 -->|"parsed tables"| ANALYST

    ADMIN -->|"filter / export logs"| P10
    ADMIN -->|"change role"| P10
    ADMIN -->|"run benchmark"| P10
    P10 <-->|"read audit logs"| D4
    P10 <-->|"read / update users"| D1
    P10 -->|"gold questions"| P4b
    P4b <-->|"prompt / SQL"| LLM
    P4b -->|"generated SQL + score"| P10
    P10 <-->|"store scores"| D5
    P10 -->|"stats · logs · benchmark report"| ADMIN
```

**Legend** — `([ rounded ])` = process · `[( cylinder )]` = data store · `[ box ]` = external entity.
Process **4.0** appears in both paths: live queries (1a) and benchmark scoring (1b).
