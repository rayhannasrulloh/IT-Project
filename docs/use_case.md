# Use Case Diagram

Actors and use cases for the **Conversational Data Analyst**. The Administrator
inherits every Analyst capability and adds operational/oversight cases. Groq LLM
and Supabase Auth are secondary (system) actors.

```mermaid
flowchart LR
    ANALYST["👤&nbsp;Business&nbsp;Analyst"]
    ADMIN["👤&nbsp;Administrator"]
    LLM["☁️&nbsp;Groq&nbsp;LLM"]
    AUTH["🔐&nbsp;Supabase&nbsp;Auth"]

    subgraph ANA["Analyst Use Cases"]
        direction TB
        UC1(["Log in / Sync profile"])
        UC2(["Ask question in natural language"])
        UC3(["View auto-generated chart"])
        UC4(["Read plain-language explanation"])
        UC5(["Show the generated SQL"])
        UC6(["Answer clarifying question (multi-turn)"])
        UC7(["Manage conversations"])
        UC8(["Upload PDF / CSV"])
        UC9(["View extracted tables"])
        UC10(["Give feedback (thumbs up/down)"])
        UC11(["Export results to CSV"])
        UC12(["Manage business data (CRUD + import)"])
        UC1 ~~~ UC2 ~~~ UC3 ~~~ UC4 ~~~ UC5 ~~~ UC6
        UC7 ~~~ UC8 ~~~ UC9 ~~~ UC10 ~~~ UC11 ~~~ UC12
    end

    subgraph ADM["Admin-only Use Cases"]
        direction TB
        UC13(["View system statistics"])
        UC14(["View / filter query logs"])
        UC15(["Export audit logs (CSV / PDF)"])
        UC16(["Manage user roles (RBAC)"])
        UC17(["Run benchmark evaluation"])
        UC13 ~~~ UC14 ~~~ UC15 ~~~ UC16 ~~~ UC17
    end

    ANALYST --- ANA
    ADMIN --- ADM
    ADMIN -. «inherits» .-> ANALYST

    UC1 -. verifies .-> AUTH
    UC2 -. generates SQL .-> LLM
    UC17 -. scores agent .-> LLM
```

> Note: Mermaid has no native UML use-case notation, so ellipses (`([ ])`) denote
> use cases and the boxes denote the system boundary and actors — semantically
> equivalent to a standard UML use-case diagram. The Administrator association to
> "Analyst Use Cases" is implied by the «inherits» generalization.
