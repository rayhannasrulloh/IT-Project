# Flowchart — Natural-Language Query Pipeline

End-to-end control flow of `POST /api/v1/chat/query` (`backend/app/api/v1/chat.py`),
the core path that turns a natural-language question into an answer.

```mermaid
flowchart TD
    START([User submits NL question]) --> AUTH{JWT valid?}
    AUTH -- No --> R401[/401 Unauthorized/]
    AUTH -- Yes --> CONV[Resolve or create conversation]
    CONV --> HIST[Load recent message history + prior SQL]
    HIST --> SAVEU[Save user message]
    SAVEU --> PEND{Pending clarification<br/>for this conversation?}

    PEND -- Yes --> MERGE[Merge original question<br/>+ user's answer] --> GEN
    PEND -- No --> INTENT[Detect intent]

    INTENT --> ISDATA{intent == DATA_QUERY?}
    ISDATA -- No --> CANNED[Return canned reply<br/>greeting / help / out-of-scope]
    CANNED --> LOG1[Log query<br/>success or failed] --> RET1([Return assistant message])

    ISDATA -- Yes --> GEN[LLM generates SQL<br/>schema-aware prompt]
    GEN --> AMB{Ambiguous?}
    AMB -- Yes --> SETP[Save pending context] --> ASK[Ask clarifying question]
    ASK --> LOGA[Log failed: ambiguous] --> RET2([Return clarification])

    AMB -- No --> EMPTY{SQL empty?}
    EMPTY -- Yes --> ERRC[Return compile-error message] --> LOGE[Log failed] --> RET3([Return])

    EMPTY -- No --> SAFE{Guardrail:<br/>SELECT/WITH only?}
    SAFE -- No --> BLOCK[Block execution] --> LOGB[Log failed: guardrail] --> RET4([Return block notice])

    SAFE -- Yes --> EXEC[Execute SQL read-only<br/>LIMIT 100 wrap]
    EXEC --> OK{Success and<br/>rows > 0?}
    OK -- No --> FAILMSG[Return error / no-data message] --> LOGF[Log failed] --> RET5([Return])

    OK -- Yes --> EXPL[LLM explanation +<br/>Plotly chart config]
    EXPL --> SAVEA[Save assistant message<br/>+ results + viz]
    SAVEA --> LOGS[Log success + duration]
    LOGS --> RET6([Return answer + chart + SQL + explanation])

    style START fill:#0f766e,color:#fff
    style RET6 fill:#2a9d8f,color:#fff
    style R401 fill:#dc2626,color:#fff
    style BLOCK fill:#dc2626,color:#fff
```
