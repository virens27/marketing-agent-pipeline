# Marketing Agent Pipeline Architecture

## System Overview

The Marketing Agent Pipeline follows a sequential multi-agent architecture where each agent consumes the output of the previous stage and generates structured data for the next stage.

```text
Accounts + Contacts
        │
        ▼
Research Agent V2
        │
        ▼
Research Cache
        │
        ▼
Analysis Agent V2
        │
        ▼
Challenge Map
        │
        ▼
Content Agent V2
        │
        ▼
Draft Content
        │
        ▼
Review Agent V2
        │
        ▼
Review Queue
        │
        ▼
Execution Agent V2
        │
        ▼
Campaign Tracker
```

---

## Agent Responsibilities

### 1. Research Agent V2

Inputs:

* Accounts Sheet
* Contacts Sheet

Processing:

* Analyze company profile
* Identify industry trends
* Generate research insights

Outputs:

* Research Cache Sheet

---

### 2. Analysis Agent V2

Inputs:

* Research Cache

Processing:

* Identify business challenges
* Evaluate impact level
* Determine hypothesis strength
* Recommend solutions

Outputs:

* Challenge Map Sheet

---

### 3. Content Agent V2

Inputs:

* Challenge Map
* Contacts

Processing:

* Generate outreach content
* Create value proposition
* Personalize messaging
* Generate CTA

Outputs:

* Draft Content Sheet

---

### 4. Review Agent V2

Inputs:

* Draft Content

Processing:

* Review messaging quality
* Evaluate personalization
* Score draft quality
* Approve or reject draft

Outputs:

* Review Queue Sheet

---

### 5. Execution Agent V2

Inputs:

* Approved Drafts

Processing:

* Simulate campaign launch
* Generate engagement metrics
* Create campaign status
* Define next actions

Outputs:

* Campaign Tracker Sheet

---

## Data Flow

### Step 1

Accounts + Contacts

↓

Research Agent V2

↓

Research Cache

---

### Step 2

Research Cache

↓

Analysis Agent V2

↓

Challenge Map

---

### Step 3

Challenge Map + Contacts

↓

Content Agent V2

↓

Draft Content

---

### Step 4

Draft Content

↓

Review Agent V2

↓

Review Queue

---

### Step 5

Review Queue

↓

Execution Agent V2

↓

Campaign Tracker

---

## External Services

### Groq API

Purpose:

* Research generation
* Challenge analysis
* Content creation
* Review evaluation
* Campaign simulation

---

### Google Sheets API

Purpose:

* Data persistence
* Agent communication layer
* Workflow tracking

---

## Design Principles

### Modular Agents

Each agent operates independently and can be executed separately.

### Sheet-Based Communication

Google Sheets acts as a shared memory layer between agents.

### Structured Outputs

Each agent produces structured records for downstream consumption.

### Traceability

Every output can be traced back to:

* Account
* Contact
* Challenge
* Draft
* Campaign

---

## Current Workflow Status

Implemented:

* Research Agent V2
* Analysis Agent V2
* Content Agent V2
* Review Agent V2
* Execution Agent V2
* Google Sheets Integration

Pipeline Status:
END-TO-END OPERATIONAL