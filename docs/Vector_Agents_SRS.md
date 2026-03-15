# Software Requirements Specification

## Vector Agents — AI-Powered Growth Intelligence Platform

**Document Version:** 1.1
**Date:** March 15, 2026
**Prepared by:** Devinda, Torch Labs
**Product URL:** vectoragents.ai

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [Intelligence Domains](#3-intelligence-domains)
4. [System Architecture & Constraints](#4-system-architecture--constraints)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [External Interfaces & Data Sources](#7-external-interfaces--data-sources)
8. [User Interface Requirements](#8-user-interface-requirements)
9. [Evaluation & Acceptance Criteria](#9-evaluation--acceptance-criteria)
10. [Assumptions & Dependencies](#10-assumptions--dependencies)
11. [Glossary](#11-glossary)

> **Changelog — v1.1:** Added business context input formats (FR-5.1.6–5.1.8); strengthened inline-only artifact constraint to explicitly prohibit external URLs (FR-5.3.4); expanded conversational memory with persistent cross-session history (FR-4.7.4–4.7.6); added new Section 4.8 (A2A Inter-Agent Protocol); added NFR-6.6 (Agent Observability); added NFR-6.7 (System Quality Attributes); updated Glossary.

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification defines the functional, non-functional, and architectural requirements for **Vector Agents**, an AI-powered growth intelligence platform. The system delivers boardroom-quality strategic insights to product and growth teams in minutes rather than weeks by coordinating multiple specialised AI agents against live data sources.

### 1.2 Scope

Vector Agents is a multi-agent intelligence system that automates the research, synthesis, and presentation of growth-related insights across six strategic domains. It replaces the fragmented workflow of 16+ separate tools with a single conversational interface that produces grounded, source-backed, interactive intelligence artifacts.

The platform is designed to generalise to any product or company context — Vector Agents itself serves as the reference product for demonstration purposes, but the system must not be hard-coded to any single domain.

### 1.3 Problem Statement

Growth intelligence today is broken and scattered. The signals that inform great product growth decisions already exist, but they are distributed across 16+ tools, take weeks to synthesise, and are rarely connected to the specific question a team is trying to answer. By the time an answer surfaces, the market has moved. Key indicators of this problem include:

- **-50%** decline in SDR recruitment from peak, signalling a shift in go-to-market strategy across the industry.
- **16+** tools managed by the average growth team, creating fragmentation and context-switching overhead.
- **Weeks** required to synthesise a single strategic brief under current workflows.

### 1.4 Design Philosophy

> "What would it look like if any product team could get boardroom-quality growth intelligence in minutes — not weeks?"

The challenge is not to build a better search box. It is to build a system that acts. Three product principles guide every design decision:

1. **One Interface** — A single conversational page. No dashboards, no navigation between tools. The conversation is the product.
2. **Live Intelligence** — Grounded in what is actually happening now, not training data. Every insight is sourced and traceable.
3. **Dynamic Artifacts** — Findings render as interactive UI inside the conversation. Trend maps, heat maps, scorecards — all inline.

---

## 2. Overall Description

### 2.1 Product Perspective

Vector Agents is a standalone, cloud-deployable web application. It operates as a conversational intelligence system backed by a multi-agent orchestration layer. It is not a chatbot wrapper around a single LLM call; it is a coordinated system of specialised agents that perform parallel research, synthesis, and presentation tasks.

### 2.2 User Classes and Characteristics

| User Class | Description | Key Needs |
|---|---|---|
| Product Managers | Leads making roadmap and feature-bet decisions | Competitive intelligence, market trends, positioning gaps |
| Growth / GTM Teams | Teams responsible for go-to-market execution | Win/loss intelligence, pricing insights, messaging gaps |
| Founders / Executives | Strategic decision-makers requiring board-level briefs | High-level synthesis across all six domains, confidence scoring |
| Analysts / Researchers | Users who need deep-dive, source-verified intelligence | Multi-hop research trails, structured outputs, citation chains |

### 2.3 Operating Environment

The system shall be deployable to standard cloud infrastructure (AWS, GCP, or Azure) and accessible through modern web browsers (Chrome, Firefox, Safari, Edge — latest two major versions). No client-side installation shall be required beyond a browser.

### 2.4 Constraints

- All intelligence must be grounded in live, real-time signals — never in stale training data alone.
- Every claim produced by the system must carry a source trail and confidence level.
- The system must generalise to any product or company; it must not be hard-coded to a single domain.
- Day-one prototyping must be achievable using free-tier APIs and open data sources.

---

## 3. Intelligence Domains

The system must be capable of answering questions across six intelligence domains. All six must be supported — not a subset.

### 3.1 Market & Trend Sensing

**Core question:** Where is the category heading and what are the leading indicators?

**Requirements:**
- FR-3.1.1: The system shall identify and track macro-level market trends relevant to a given product category.
- FR-3.1.2: The system shall surface leading indicators (funding rounds, job postings, patent filings, keyword volume shifts) that signal directional changes.
- FR-3.1.3: The system shall present trend data as interactive timeline or trend-map artifacts within the conversation.

### 3.2 Competitive Landscape & Feature Bets

**Core question:** Who is doing what, is there genuine demand, and is a given feature bet worth making?

**Requirements:**
- FR-3.2.1: The system shall identify and profile competitors in a given product category.
- FR-3.2.2: The system shall track competitor feature releases, product updates, and strategic moves.
- FR-3.2.3: The system shall assess genuine demand signals (reviews, community discussion, search trends) for specific feature bets.
- FR-3.2.4: The system shall produce comparative scorecards ranking competitors across relevant dimensions.

### 3.3 Win / Loss Intelligence

**Core question:** Why are deals being lost? What does the market look like from the buyer's side?

**Requirements:**
- FR-3.3.1: The system shall analyse buyer-side signals from reviews, forums, and community discussions to surface common objections and loss patterns.
- FR-3.3.2: The system shall identify recurring themes in competitive win/loss scenarios.
- FR-3.3.3: The system shall present win/loss findings with attributed sources and confidence scoring.

### 3.4 Pricing & Packaging Intelligence

**Core question:** Is the pricing model right, and where is willingness-to-pay shifting?

**Requirements:**
- FR-3.4.1: The system shall track competitor pricing models, tiers, and packaging structures.
- FR-3.4.2: The system shall identify shifts in willingness-to-pay signals from market data and community sentiment.
- FR-3.4.3: The system shall compare pricing strategies across the competitive landscape and surface anomalies or opportunities.

### 3.5 Positioning & Messaging Gaps

**Core question:** Not what to build — how to talk about what already exists.

**Requirements:**
- FR-3.5.1: The system shall analyse competitor messaging, ad copy, and positioning statements.
- FR-3.5.2: The system shall identify gaps between a product's capabilities and its public messaging.
- FR-3.5.3: The system shall surface messaging opportunities informed by buyer language and community terminology.

### 3.6 Adjacent Market Collision

**Core question:** What is coming from outside your category that you are not watching?

**Requirements:**
- FR-3.6.1: The system shall monitor adjacent and converging markets for products or trends that may disrupt the target category.
- FR-3.6.2: The system shall identify cross-category signals such as new entrants, technology convergence, and regulatory shifts.
- FR-3.6.3: The system shall assess the threat or opportunity level of adjacent market movements with supporting evidence.

---

## 4. System Architecture & Constraints

### 4.1 Hard Rules

These are inviolable constraints that define the system's identity.

| Rule | ID | Description |
|---|---|---|
| Not a chatbot | AR-01 | Findings render as interfaces inside the conversation — not links, not separate windows. The system produces dynamic inline artifacts, not plain text responses. |
| Not one model call | AR-02 | Genuine multi-agent coordination is required. Multiple steps, tool calls, and parallel threads. The system must not be a single prompt-response wrapper. |
| Live signal only | AR-03 | Insights must be grounded in what is happening now. Every claim carries a source trail and confidence level. |

### 4.2 Signal Source Diversity (TC-7.1)

The system shall pull intelligence from a diverse range of signal sources, including but not limited to: product pages, user reviews, job postings, funding announcements, search keyword data, and patent filings. No single source type shall be treated as the sole ground truth.

### 4.3 Parallelism & Specialisation (TC-7.2)

- FR-4.3.1: The system shall support simultaneous execution of multiple agent threads.
- FR-4.3.2: Each agent shall have a specialised scope (e.g., one agent handles competitive research, another handles pricing analysis).
- FR-4.3.3: A synthesis step shall combine outputs from parallel agents into a coherent, unified response after individual threads complete.

### 4.4 Deep Research — Multi-Hop (TC-7.3)

- FR-4.4.1: The system shall perform multi-hop research: find an initial signal → deepen it → follow related threads → cross-reference across sources → surface findings with a confidence score.
- FR-4.4.2: The research depth shall be adaptive — simple questions receive quick answers, while complex strategic queries trigger deeper multi-hop chains.

### 4.5 Agent Lifecycle & Failure Handling (TC-7.4)

- FR-4.5.1: The system shall manage the full agent lifecycle: spawning, execution, state tracking, completion, and teardown.
- FR-4.5.2: Agent state shall be visible to the user (e.g., "Researching competitors…", "Analysing pricing data…").
- FR-4.5.3: The system shall degrade gracefully — if one agent or data source fails, remaining agents continue and the system reports partial results with appropriate caveats.
- FR-4.5.4: A full audit trail shall be maintained for every agent run, including inputs, tool calls, intermediate findings, and final outputs.

### 4.6 Structured Outputs (TC-7.5)

- FR-4.6.1: All findings shall be returned as typed, structured objects (not freeform text) with defined schemas.
- FR-4.6.2: Each finding shall include a confidence level (e.g., high / medium / low, or a numeric score).
- FR-4.6.3: Facts shall be explicitly separated from interpretation in all outputs.

### 4.7 Conversational Memory (TC-7.6)

- FR-4.7.1: Each follow-up query shall build on established context from the current session.
- FR-4.7.2: New signals or data retrieved during a follow-up shall update prior conclusions where appropriate, with change attribution visible to the user.
- FR-4.7.3: The system shall maintain session context across a reasonable conversation length without degradation of coherence.
- FR-4.7.4: **Temporary (in-session) memory** — all messages, findings, artifacts, and business context within a session shall be held in memory and used to personalise every subsequent query within that same session.
- FR-4.7.5: **Persistent (cross-session) memory** — when a new session is initiated by the same user, the system shall reload prior conversation history, established business context, and prior findings. Responses in the new session shall be informed by this persistent context, enabling a continuously personalised experience rather than a cold-start with every visit.
- FR-4.7.6: Users shall be able to view, label, and selectively delete past sessions. Persistent history shall be stored securely and scoped to the authenticated user account.

### 4.8 A2A Inter-Agent Protocol

All communication between agents in the multi-agent system shall use the **Agent-to-Agent (A2A) protocol** as the standard messaging interface. This ensures agents remain loosely coupled, independently testable, and auditable.

- FR-4.8.1: Every inter-agent message shall conform to the A2A message schema, which shall include at minimum: `sender_id`, `receiver_id`, `task_type`, `payload` (typed, structured), `priority`, and `timestamp`.
- FR-4.8.2: Agents shall not communicate through shared mutable state or direct LLM prompt chaining. All coordination shall pass through the A2A message bus managed by the orchestrator.
- FR-4.8.3: The A2A protocol shall support three interaction patterns: **request/response** (an agent requests a result from another), **broadcast** (the orchestrator fans out a task to multiple agents simultaneously), and **publish/subscribe** (an agent emits a finding that subscribing agents consume to update their own context).
- FR-4.8.4: All A2A messages shall be logged by the orchestrator as part of the audit trail (see FR-4.5.4), enabling full reconstruction of agent coordination for any given query.
- FR-4.8.5: The A2A message bus shall enforce schema validation on all incoming messages. Malformed or unexpected messages shall be rejected with a structured error response, not silently dropped.

---

## 5. Functional Requirements

### 5.1 Conversational Interface

| ID | Requirement | Priority |
|---|---|---|
| FR-5.1.1 | The system shall provide a single-page conversational interface as the sole interaction surface. | Must-have |
| FR-5.1.2 | Users shall be able to ask natural-language questions about any of the six intelligence domains. | Must-have |
| FR-5.1.3 | The system shall support follow-up questions that refine, deepen, or redirect a prior query. | Must-have |
| FR-5.1.4 | The interface shall display clarification chips — suggested follow-up prompts — to guide the user toward richer intelligence. | Should-have |
| FR-5.1.5 | The system shall accept a target product or company as context input and generalise all intelligence gathering to that target. | Must-have |
| FR-5.1.6 | The system shall allow users to provide business context as **free-text** (typed description of their product, market, and goals). | Must-have |
| FR-5.1.7 | The system shall allow users to upload **documents** (PDF, DOCX, TXT) as business context. Uploaded documents shall be parsed and their content indexed as part of the user's business profile for the session. | Must-have |
| FR-5.1.8 | The system shall allow users to provide one or more **website URLs** as business context. The system shall crawl and parse those URLs (using Firecrawl or equivalent) and ingest the content as part of the user's business profile. | Must-have |
| FR-5.1.9 | Business context provided via text, documents, or URLs shall persist for the duration of the session and, when cross-session history is enabled, shall be reloaded in subsequent sessions. All agent intelligence tasks shall be personalised against this context. | Must-have |

### 5.2 Multi-Agent Orchestration

| ID | Requirement | Priority |
|---|---|---|
| FR-5.2.1 | The system shall coordinate six or more specialised agents to handle a single user query. | Must-have |
| FR-5.2.2 | Agents shall execute in parallel where their tasks are independent. | Must-have |
| FR-5.2.3 | The orchestrator shall manage agent spawning, routing, state, and result aggregation. | Must-have |
| FR-5.2.4 | The system shall integrate with external tools and MCP (Model Context Protocol) servers for live data retrieval. | Must-have |
| FR-5.2.5 | The orchestrator shall not be a single LLM prompt-response wrapper; it must demonstrate genuine multi-step, multi-tool coordination. | Must-have |

### 5.3 Dynamic Artifact Rendering

| ID | Requirement | Priority |
|---|---|---|
| FR-5.3.1 | The system shall render findings as interactive UI components inline within the conversation stream. | Must-have |
| FR-5.3.2 | Supported artifact types shall include (at minimum): trend maps, heat maps, scorecards, comparison tables, and timeline visualisations. | Must-have |
| FR-5.3.3 | Artifacts shall be interactive — users shall be able to hover, filter, or drill down where appropriate. | Should-have |
| FR-5.3.4 | Artifacts shall **never** open in, link to, or redirect to separate windows, tabs, or external URLs. All rendering must occur inline within the conversation stream. No finding, chart, scorecard, or result shall be delivered via an external link or a new browser context of any kind. | Must-have |
| FR-5.3.5 | Each artifact shall include an inline confidence indicator (e.g., a colour-coded badge or percentage) showing the evidence strength behind the rendered finding. | Must-have |

### 5.4 Source Grounding & Citation

| ID | Requirement | Priority |
|---|---|---|
| FR-5.4.1 | Every factual claim shall include a traceable source reference. | Must-have |
| FR-5.4.2 | Each finding shall carry an explicit confidence level. | Must-have |
| FR-5.4.3 | The system shall clearly label which parts of a response are factual evidence and which are interpretation or inference. | Must-have |
| FR-5.4.4 | Users shall be able to inspect the source trail for any individual finding. | Should-have |

### 5.5 Generalisation

| ID | Requirement | Priority |
|---|---|---|
| FR-5.5.1 | The system shall accept any product, company, or market category as input — not only Vector Agents. | Must-have |
| FR-5.5.2 | Intelligence pipelines, agent logic, and artifact templates shall not contain hard-coded references to a specific product. | Must-have |
| FR-5.5.3 | The demo shall demonstrate generalisation by running against at least two distinct product contexts. | Must-have |

---

## 6. Non-Functional Requirements

### 6.1 Performance

| ID | Requirement | Target |
|---|---|---|
| NFR-6.1.1 | Time to first visible result (initial agent status or partial finding) | ≤ 10 seconds |
| NFR-6.1.2 | Time to complete a standard single-domain query | ≤ 60 seconds |
| NFR-6.1.3 | Time to complete a full six-domain strategic brief | ≤ 5 minutes |

### 6.2 Scalability & Cost Efficiency

| ID | Requirement | Target |
|---|---|---|
| NFR-6.2.1 | The system shall be deployable to standard cloud infrastructure. | Must-have |
| NFR-6.2.2 | Cost-per-query shall be estimated and documented. | Must-have |
| NFR-6.2.3 | The architecture shall support horizontal scaling of agent workers. | Should-have |
| NFR-6.2.4 | Day-one prototyping shall be achievable on free-tier API quotas. | Must-have |

### 6.3 Reliability

| ID | Requirement | Target |
|---|---|---|
| NFR-6.3.1 | The system shall degrade gracefully when individual data sources are unavailable. | Must-have |
| NFR-6.3.2 | Partial results shall be presented with clear caveats when full data retrieval fails. | Must-have |
| NFR-6.3.3 | Agent failures shall be logged and shall not crash the overall orchestration. | Must-have |

### 6.4 Auditability

| ID | Requirement | Target |
|---|---|---|
| NFR-6.4.1 | Every agent run shall produce a full audit trail (inputs, tool calls, intermediate results, final output). | Must-have |
| NFR-6.4.2 | Audit trails shall be retrievable for inspection post-session. | Should-have |

### 6.5 Security & Privacy

| ID | Requirement | Target |
|---|---|---|
| NFR-6.5.1 | The system shall not persist user queries or results beyond the session unless explicitly opted in. | Must-have |
| NFR-6.5.2 | API keys and credentials shall be stored securely and never exposed in client-side code or logs. | Must-have |

### 6.6 Agent Observability

The system must provide full observability into agent behaviour at runtime and post-hoc. This is required for debugging, quality assurance, and user trust.

| ID | Requirement | Target |
|---|---|---|
| NFR-6.6.1 | **Structured Logs** — Every agent action (spawn, tool call, data fetch, intermediate finding, completion, failure) shall emit a structured log entry with fields: `timestamp`, `agent_id`, `action_type`, `input_summary`, `output_summary`, `duration_ms`, `status`. | Must-have |
| NFR-6.6.2 | **Distributed Traces** — Each user query shall generate a root trace with child spans for every agent invoked. Spans shall capture start time, end time, parent agent, tool calls made, and final status. Trace IDs shall be linkable back to A2A messages. | Must-have |
| NFR-6.6.3 | **Real-Time Status Panel** — The UI shall display a live agent activity panel during query execution, showing which agents are active, their current task, and elapsed time (e.g., "Market Sensing Agent — scanning job boards… 8s"). | Must-have |
| NFR-6.6.4 | **Post-Query Trace Viewer** — Users shall be able to expand a completed response to view the full agent trace: which agents ran, what tools they called, what sources they retrieved, and how long each step took. | Should-have |
| NFR-6.6.5 | **Error Logs** — All agent failures, tool call errors, and data source timeouts shall be logged with full context. Error logs shall be queryable by session ID and agent ID. | Must-have |
| NFR-6.6.6 | **Confidence Trail** — Every response surface shall include a traceable confidence score derived from the structured outputs of individual agents (see FR-4.6.2). The confidence trail must be viewable per claim, not only at the summary level. | Must-have |

### 6.7 System Quality Attributes

The system shall be designed and evaluated against four core quality dimensions: **Effectiveness**, **Safety**, **Efficiency**, and **Robustness**.

#### 6.7.1 Effectiveness

| ID | Requirement | Target |
|---|---|---|
| NFR-6.7.1 | Intelligence responses shall demonstrably answer the user's stated question using live, multi-source data — not generic or hallucinated content. | Must-have |
| NFR-6.7.2 | Responses shall address all six intelligence domains when a broad strategic query is submitted; domain coverage shall be verifiable in the agent trace. | Must-have |
| NFR-6.7.3 | The system shall use the user's business context (text, documents, URLs) to personalise responses — generic responses that ignore provided context are a quality failure. | Must-have |

#### 6.7.2 Safety

| ID | Requirement | Target |
|---|---|---|
| NFR-6.7.4 | The system shall never fabricate citations, source URLs, or confidence scores. If a source cannot be verified, the finding shall be flagged as unverified rather than presented as grounded. | Must-have |
| NFR-6.7.5 | Agents shall not execute destructive actions (e.g., modifying external systems, submitting forms, or clicking interactive page elements) when scraping or crawling data sources. Read-only access only. | Must-have |
| NFR-6.7.6 | User-uploaded documents and business context shall be processed in isolated, sandboxed compute environments to prevent code injection or data leakage across user accounts. | Must-have |
| NFR-6.7.7 | The system shall display clear disclaimers when confidence is low or when a finding is based on a single source without corroboration. | Should-have |

#### 6.7.3 Efficiency

| ID | Requirement | Target |
|---|---|---|
| NFR-6.7.8 | Agents shall execute in parallel wherever task dependencies allow, minimising end-to-end query latency. Sequential execution of parallelisable tasks is a design defect. | Must-have |
| NFR-6.7.9 | The system shall cache intermediate research results within a session (e.g., competitor profiles) to avoid redundant API calls on follow-up queries about the same entities. | Should-have |
| NFR-6.7.10 | LLM token consumption per query shall be tracked and reported. Prompt designs shall be optimised to avoid unnecessary verbosity in agent-to-agent communication. | Should-have |
| NFR-6.7.11 | Cost-per-query estimates shall be surfaced in the observability dashboard, broken down by agent and tool call type. | Should-have |

#### 6.7.4 Robustness

| ID | Requirement | Target |
|---|---|---|
| NFR-6.7.12 | The system shall handle unexpected or ambiguous user queries without crashing or returning empty responses. Unclear queries shall trigger a clarification prompt rather than a silent failure. | Must-have |
| NFR-6.7.13 | The system shall remain functional when one or more data sources are unavailable, returning partial results with explicit coverage gaps noted. | Must-have |
| NFR-6.7.14 | The system shall implement retry logic with exponential backoff for transient API failures before marking a data source as unavailable for a given query. | Must-have |
| NFR-6.7.15 | Agent timeouts shall be configurable per agent type. A timed-out agent shall return a partial result or a graceful failure notice rather than blocking the synthesis step indefinitely. | Must-have |

---

## 7. External Interfaces & Data Sources

### 7.1 Recommended API Stack

The following data sources form the recommended integration layer. Playwright serves as the universal fallback for any site without a structured API.

| Source | Type | Details | Rate Limits / Notes |
|---|---|---|---|
| **Meta Ad Library API** | FREE | Official structured JSON. Political + EU ads, spend ranges, demographics. | ~200 calls/hr. Requires identity verification. |
| **LinkedIn Ad Library** | FREE | Public access. Extract via Firecrawl or Playwright. Full sponsored content per advertiser. | Scraping-based; no official API. |
| **SerpAPI** | FREE TIER | Google Ads Transparency, Trends, and News as structured JSON. | 100 searches/month free. |
| **Firecrawl** | RECOMMENDED | Any page to LLM-ready markdown. Official MCP server available — plugs directly into Claude. | 500 free credits. Recommended as primary backbone. |
| **Playwright / Puppeteer** | FALLBACK | JS-heavy sites, auth flows, dynamic content. Use for BigSpy, Google Ads Transparency. | No rate limits (self-hosted), but respect robots.txt. |
| **Reddit API** | OPEN DATA | Free OAuth2 access. Real user voice for sentiment and demand signals. | Standard Reddit API rate limits. |
| **HN Algolia API** | OPEN DATA | Free, no API key required. Tech community sentiment and discussion tracking. | No key required. |
| **USPTO Patents** | OPEN DATA | Pre-launch technical signal. Patent filings for competitive technology intelligence. | Public data, no key required. |

### 7.2 Integration Requirements

- FR-7.2.1: The system shall support MCP (Model Context Protocol) server integration for tool and data-source connectivity.
- FR-7.2.2: New data sources shall be addable without requiring changes to core orchestration logic (plugin architecture).
- FR-7.2.3: Each data source adapter shall handle its own authentication, rate limiting, and error recovery.
- FR-7.2.4: Firecrawl shall serve as the primary web-to-data backbone, with Playwright/Puppeteer as the fallback for pages Firecrawl cannot process.

---

## 8. User Interface Requirements

### 8.1 Core UX Principles

- **Single page, no navigation.** The conversation is the entire product surface. There are no dashboards, settings pages, or tool-switching panels.
- **Inline artifacts.** All visualisations, scorecards, and interactive elements render inside the conversation stream.
- **Clarification chips.** Suggested follow-up queries appear as tappable chips to lower the barrier to deeper exploration.
- **Agent state visibility.** While agents are working, the user sees real-time status indicators (e.g., "Scanning competitor pricing…", "Cross-referencing patent data…").
- **Designed, not assembled.** The overall experience should feel like a polished product, not a stitched-together demo. Transitions, typography, and layout should be intentional.

### 8.2 Artifact Types (Minimum Viable Set)

| Artifact | Description |
|---|---|
| Trend Map | Interactive timeline showing market or category trajectory with annotated inflection points. |
| Heat Map | Colour-coded matrix showing intensity across dimensions (e.g., competitor features vs. demand signals). |
| Scorecard | Structured comparison table with weighted scoring across defined criteria. |
| Comparison Table | Side-by-side feature or attribute comparison across competitors or options. |
| Timeline | Chronological view of events (funding rounds, launches, pivots) with source links. |
| Confidence Panel | Per-finding breakdown showing evidence, source links, and confidence score. |

---

## 9. Evaluation & Acceptance Criteria

The system shall be evaluated across five weighted dimensions. These criteria serve as the acceptance test for the delivered system.

| # | Criterion | Weight | What "Excellent" Looks Like |
|---|---|---|---|
| 1 | Core Algorithm (Multi-Agent System) | 25% | 6+ coordinated agents, parallelism, lifecycle management, tool/MCP usage. Not a wrapper. |
| 2 | Product Design Strategy | 25% | Dynamic inline artifacts, clarification chips, seamless UX. Feels designed, not assembled. |
| 3 | Intelligence Quality & Grounding | 20% | Multi-source, confidence-scored, facts vs. interpretation separated. Grounded, not hallucinated. |
| 4 | Scalability & Cost Efficiency for GTM | 15% | Cloud-deployable, cost-per-query estimated, horizontal scale considered. |
| 5 | Demo Strength & Generalisability | 15% | Live on Vector Agents + demonstrated generalisation to another product or context. |

### 9.1 Reference Demo Scenarios

The following prompts shall be supported as baseline acceptance tests:

1. *"Is [Competitor X] competitive in the AI SDR market right now? Where does [Product] stand?"*
2. *"Is the [category] accelerating or consolidating — and what does that mean for [Product]'s roadmap?"*
3. *"What should [Product] build or reposition over the next six months to capture emerging demand?"*

Each prompt must produce a multi-agent, multi-source, artifact-rich response grounded in live data.

---

## 10. Assumptions & Dependencies

### 10.1 Assumptions

- Users have a modern web browser and stable internet connection.
- Free-tier API quotas are sufficient for prototyping and initial demonstration, though production deployment may require paid tiers.
- Target product/company information is publicly available on the web.
- The LLM provider (e.g., Anthropic Claude) supports tool-use and MCP integration at the time of development.

### 10.2 Dependencies

- **Firecrawl** as the primary web-scraping backbone and MCP connector.
- **SerpAPI** for structured Google data (Trends, Ads Transparency, News).
- **Meta Ad Library API** for advertising intelligence (requires pre-approved identity verification).
- **LLM Provider** (e.g., Anthropic Claude) for agent reasoning, synthesis, and natural language generation.
- **Cloud Infrastructure** (AWS / GCP / Azure) for deployment and horizontal scaling.

---

## 11. Glossary

| Term | Definition |
|---|---|
| **A2A Protocol (Agent-to-Agent)** | The standardised inter-agent messaging protocol used for all communication between agents in the multi-agent system. Messages carry a defined schema including sender/receiver IDs, task type, typed payload, priority, and timestamp. |
| **Agent** | An autonomous AI sub-process with a specialised scope (e.g., competitive analysis, pricing research) that executes tool calls and returns structured findings. |
| **Agent Observability** | The set of logging, tracing, and monitoring capabilities that make agent behaviour visible and auditable — including structured logs, distributed traces, real-time status panels, and post-query trace viewers. |
| **Artifact** | An interactive UI component (chart, table, map, scorecard) rendered inline within the conversation. Artifacts never open in external windows, tabs, or URLs. |
| **Business Context** | User-provided information about their product, company, and market, supplied in any combination of free-text, uploaded documents, or website URLs. Business context personalises all agent intelligence tasks. |
| **Clarification Chip** | A suggested follow-up query displayed as a tappable UI element to guide the user toward deeper intelligence. |
| **Confidence Level** | A score or label (high / medium / low) attached to every finding indicating the strength of supporting evidence. Surfaced per-claim in the Confidence Trail. |
| **Confidence Trail** | The per-claim breakdown of evidence, sources, and confidence scores that supports a finding — viewable inline within an artifact or response. |
| **Cross-Session Memory** | Persistent storage of a user's conversation history, business context, and prior findings that is reloaded when a new session is initiated, enabling a continuously personalised experience. |
| **Distributed Trace** | A root trace and set of child spans generated for every user query, capturing the full timeline of agent invocations, tool calls, and data fetches with timing and status. |
| **Firecrawl** | A web-scraping service that converts any webpage into LLM-ready markdown, with an official MCP server for direct Claude integration. |
| **Grounding** | The practice of tying every AI-generated insight to a verifiable, real-time data source rather than relying on training data. |
| **MCP (Model Context Protocol)** | A protocol for connecting LLMs to external tools and data sources in a standardised way. |
| **Multi-Hop Research** | A research pattern where an initial finding is deepened by following related threads, cross-referencing sources, and iteratively building confidence. |
| **Orchestrator** | The central coordination layer that spawns, routes, monitors, and synthesises the outputs of multiple specialised agents via the A2A protocol. |
| **Signal Source** | Any external data input (API, website, database) that provides raw intelligence signals to the system. |
| **Source Trail** | The chain of references linking a final insight back to the raw data sources that support it. |

---

*End of Document*
