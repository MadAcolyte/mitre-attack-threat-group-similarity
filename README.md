# mitre-attack-threat-group-similarity

## Data

| File | Description |
| --- | --- |
| `data/incidents_strict.json` | MITRE ATT&CK-derived incident dataset (662 incidents) |
| `data/incidents_example.json` | Small example of the same incident shape |
| `data/examples.json` | Example analysis request/response payloads |

`incidents_strict.json` matches the `incidents_example.json` shape: `incident_id`, `group`, `techniques`, `description`.

## MITRE ATT&CK® copyright

`data/incidents_strict.json` is derived from [MITRE ATT&CK®](https://attack.mitre.org/). Per MITRE's terms of use, the copyright designation ships with this data:

> © 2026 The MITRE Corporation. This work is reproduced and distributed with the permission of The MITRE Corporation.

The MITRE Corporation (MITRE) hereby grants you a non-exclusive, royalty-free license to use ATT&CK® for research, development, and commercial purposes. Any copy you make for such purposes is authorized provided that you reproduce MITRE's copyright designation and this license in any such copy.

See [MITRE ATT&CK Terms of Use](https://attack.mitre.org/resources/legal-and-branding/terms-of-use/) and the [attack-stix-data LICENSE](https://github.com/mitre-attack/attack-stix-data/blob/master/LICENSE.txt).

## UMLs

### PlantUML Component diagram

```plantuml
@startuml
actor "External System / SIEM" as Client

rectangle "Threat Actor Analysis API" {

    component "REST API\nPOST /analyze" as API

    component "Query Processor" as Query

    component "RAG Retriever" as RAG

    component "Vector Index" as Index

    component "Gemini API" as Gemini

    component "Result Generator" as Result
}

database "Threat Intelligence\nKnowledge Base" as DB

cloud "GitHub Repository" as GitHub


Client --> API : MITRE technique IDs\n["T1059.001", "T1071.001", "T1105"]

API --> Query : Validate & process\ntechniques

Query --> RAG : User query

RAG --> Index : Retrieve similar\nhistorical incidents

Index --> RAG : Relevant incidents

RAG --> DB : Get incident details

DB --> RAG : Group + techniques +\ndescription

RAG --> Gemini : Query + retrieved incidents

Gemini --> Result : Top 3 groups +\nmatch scores + evidence + reasoning

Result --> API : Structured result

API --> Client : JSON response

GitHub --> DB : Knowledge base
@enduml
```

![image](https://private-user-images.githubusercontent.com/125881377/662413614-e6ef33c3-b1d4-4ecf-856f-941daba9a7bc.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3OTA3OTE1MjYsIm5iZiI6MTc5MDc5MTIyNiwicGF0aCI6Ii8xMjU4ODEzNzcvNjYyNDEzNjE0LWU2ZWYzM2MzLWIxZDQtNGVjZi04NTZmLTk0MWRhYmE5YTdiYy5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwOTMwJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDkzMFQxODAwMjZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1mNjI5ODk3NzkwZjM0Y2MyMjNhZGRmYzNmNTU4MjQ4Zjk3Y2IyNmJmMjg3ZjZiNTA2YzBjZGE0OGU2NDZmYzRkJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.U67ZIc4j2yC2aBqEc95EMzG9ar6NVp36UKXKSRtcjb8)

---

### Mermaid UML

```mermaid
flowchart LR

    Client["External System / SIEM"]

    subgraph API_System["Threat Actor Analysis API"]
        API["REST API<br/>POST /analyze"]
        Query["Query Processor"]
        RAG["RAG Retriever"]
        Index["Vector Index"]
        Gemini["Gemini API"]
        Result["Result Generator"]
    end

    DB[("Threat Intelligence<br/>Knowledge Base")]
    GitHub["GitHub Repository"]

    Client -->|"MITRE technique IDs<br/>[T1059.001, T1071.001, T1105]"| API

    API -->|"Validate & process<br/>techniques"| Query

    Query -->|"User query"| RAG

    RAG -->|"Retrieve similar<br/>historical incidents"| Index

    Index -->|"Relevant incidents"| RAG

    RAG -->|"Get incident details"| DB

    DB -->|"Group + techniques +<br/>description"| RAG

    RAG -->|"Query + retrieved incidents"| Gemini

    Gemini -->|"Top 3 groups +<br/>match scores + evidence + reasoning"| Result

    Result -->|"Structured result"| API

    API -->|"JSON response"| Client

    GitHub -->|"Knowledge base"| DB
```
### PlantUML Sequence diagram
```
@startuml
actor "External System / SIEM" as Client

participant "REST API\n/analyze" as API
participant "Query Processor" as Query
participant "RAG Retriever" as RAG
database "Vector Index" as Index
database "Threat Intelligence\nKnowledge Base" as DB
participant "Gemini API" as Gemini
participant "Result Generator" as Result

Client -> API : POST /analyze\nMITRE technique IDs
API -> Query : Validate & process techniques
Query --> API : Validated techniques

API -> RAG : User query
RAG -> Index : Retrieve similar historical incidents
Index --> RAG : Relevant incident IDs

RAG -> DB : Get incident details
DB --> RAG : Group + techniques + description

RAG -> Gemini : Query + retrieved incidents
Gemini -> Gemini : Analyze evidence
Gemini -> Gemini : Identify top 3 groups
Gemini -> Gemini : Generate evidence + reasoning
Gemini --> Result : Analysis result

Result --> API : Structured result
API --> Client : JSON response

@enduml
```
<img width="1406" height="686" alt="image" src="https://github.com/user-attachments/assets/2eb945cb-cd8a-4a2b-815b-e34245f0f723" />

### Mermaid UML

```mermaid
sequenceDiagram
    actor Client as External System / SIEM
    participant API as REST API /analyze
    participant Query as Query Processor
    participant RAG as RAG Retriever
    participant Index as Vector Index
    participant DB as Threat Intelligence Knowledge Base
    participant Gemini as Gemini API
    participant Result as Result Generator

    Client->>API: POST /analyze<br/>MITRE technique IDs
    API->>Query: Validate & process techniques
    Query-->>API: Validated techniques

    API->>RAG: User query
    RAG->>Index: Retrieve similar historical incidents
    Index-->>RAG: Relevant incident IDs

    RAG->>DB: Get incident details
    DB-->>RAG: Group + techniques + description

    RAG->>Gemini: Query + retrieved incidents
    Gemini->>Gemini: Analyze evidence
    Gemini->>Gemini: Identify top 3 groups
    Gemini->>Gemini: Generate evidence + reasoning
    Gemini-->>Result: Analysis result

    Result-->>API: Structured result
    API-->>Client: JSON response
```

## Colab prototype

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MadAcolyte/mitre-attack-threat-group-similarity/blob/main/notebooks/threat_group_similarity_gemini.ipynb)

[`notebooks/threat_group_similarity_gemini.ipynb`](notebooks/threat_group_similarity_gemini.ipynb) is an end-to-end Google Colab prototype of the architecture above. Each notebook section is one UML component: GitHub knowledge base load, Query Processor, Vector Index, RAG Retriever, Gemini API, Result Generator, and `POST /analyze`.

**How to run:** open the badge, add a Colab Secret named `GEMINI_API_KEY` (🔑 Secrets panel), then Runtime → Run all. Without a key the notebook still runs: Gemini embedding/generation cells are skipped and a TF-IDF/Jaccard fallback produces the same JSON shape as `y` in `data/examples.json`.

To refresh `data/examples.json` from **real** Gemini outputs (this will not write placeholder data), set `GEMINI_API_KEY` and run:

```bash
python scripts/regenerate_examples.py
```
