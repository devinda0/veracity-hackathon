# Vector Agents Presentation — Markdown Transcription

This file transcribes the visible content from the provided presentation screenshots and preserves the slide-by-slide structure, including headings, body copy, stats, table content, and brief layout notes.

---

## Slide 01 — The Problem

**Section label:** THE PROBLEM  
**Footer:** 01 · THE PROBLEM

### Headline
**Growth intelligence is broke and scattered.**

### Body copy
The signals that inform great product growth decisions already exist. The problem is they’re scattered across 16+ tools, take weeks to synthesise, and are rarely connected to the specific question a team is trying to answer. By the time there’s an answer, the market has moved.

### Key metrics
- **-50%**  
  SDR recruitment declining from peak
- **16+**  
  Tools the average growth team manages
- **Weeks**  
  To synthesise a single strategic brief

### Quote
> “Teams with bigger research budgets move faster - not because they’re smarter, but because they have more people turning signals into answers.”

### Layout notes
- Light background.
- Small teal section label at top left.
- Large bold black headline.
- Supporting paragraph below headline.
- Three large teal metric blocks across the page.
- Italic quote near the bottom.

---

## Slide 02 — The Challenge / Product Principles

### Left panel
**Section label:** The Challenge

> “What would it look like if any product team could get boardroom-quality growth intelligence in minutes - not weeks?”

The challenge is not to build a better search box.  
It’s to build a system that acts.

### Right panel
#### 01 — One interface
A single conversational page. No dashboards, no navigation between tools. The conversation is the product.

#### 02 — Live intelligence
Grounded in what’s actually happening now - not training data. Every insight sourced and traceable.

#### 03 — Dynamic artifacts
Findings render as interactive UI inside the conversation. Trend maps, heat maps, scorecards - inline.

### Layout notes
- Split layout.
- Left half uses a teal background with large italic quote text in white.
- Right half uses a light background with three numbered principles.
- Thin divider lines separate sections.

---

## Slide 03 — What the System Must Answer

**Section label:** WHAT THE SYSTEM MUST ANSWER  
**Footer:** 02 · THE DOMAINS

### Headline
**Six intelligence domains.**

### Subhead
*All six - not just one.*

### Domains
#### Market & Trend Sensing
Where is the category heading and what are the leading indicators?

#### Competitive Landscape & Feature Bets
Who’s doing what, is there genuine demand, is a given bet worth making?

#### Win / Loss Intelligence
Why are deals being lost? What does the market look like from the buyer’s side?

#### Pricing & Packaging Intelligence
Is the pricing model right, and where is willingness-to-pay shifting?

#### Positioning & Messaging Gaps
Not what to build - how to talk about what already exists.

#### Adjacent Market Collision
What’s coming from outside your category that you’re not watching?

### Layout notes
- Light background.
- Large bold headline with italic grey subhead.
- Six domains arranged in two columns with divider lines.

---

## Slide 04 — Architecture & Constraints

**Section label:** ARCHITECTURE & CONSTRAINTS  
**Footer:** 03 · CONSTRAINTS & ARCHITECTURE

### Left column — Three hard rules
#### 01 — Not a chatbot
Findings render as interfaces inside the conversation - not links, not separate windows.

#### 02 — Not one model call
Genuine multi-agent coordination. Multiple steps, tool calls, parallel threads. Not a single prompt-response.

#### 03 — Live signal only
Insights grounded in what’s happening now. Every claim carries a source trail and confidence level.

### Right column — Technical concepts
#### 7.1 — Signal source diversity
Product pages · Reviews · Job postings · Funding · Keywords · Patents

#### 7.2 — Parallelism & specialisation
Simultaneous threads, specialised scope, synthesis after completion.

#### 7.3 — Deep research — multi-hop
Find → deepen → follow threads → cross-reference → surface with confidence.

#### 7.4 — Lifecycle & failure handling
Spawning, state visibility, graceful degradation, audit trail.

#### 7.5 — Structured outputs
Typed findings, confidence levels, facts separated from interpretation.

#### 7.6 — Conversational memory
Each follow-up builds on established context. New signals update conclusions.

### Layout notes
- Two-column layout.
- Left column presents product rules.
- Right column lists technical concepts with numbered items.
- Light background with teal accents and divider lines.

---

## Slide 05 — APIs & Signal Sources

**Section label:** APIS & SIGNAL SOURCES  
**Footer:** 04 · APIS & SOURCES

### Headline
**Recommended stack.**

### Subhead
*Free tiers sufficient for day-one prototyping. Use Playwright as the fallback for any site without an API.*

### Stack items
#### Meta Ad Library API — FREE
Official structured JSON. Political + EU ads, spend ranges, demographics. ~200 calls/hr. Complete identity verification before the event.

#### LinkedIn Ad Library — FREE
Public access. Use Firecrawl or Playwright to extract. Full sponsored content per advertiser.

#### SerpAPI — FREE TIER
Google Ads Transparency, Trends, and News as structured JSON. 100 searches/month free. No scraping.

#### Firecrawl — RECOMMENDED
500 free credits. Any page to LLM-ready markdown. Has an official MCP server — plugs directly into Claude. The best backbone.

#### Playwright / Puppeteer — ALTERNATIVE
The fallback when no API exists. JS-heavy sites, auth flows, dynamic content. Use for BigSpy, Google Ads Transparency.

#### Reddit + HN Algolia + Patents — OPEN DATA
Reddit (free OAuth2) for real user voice. HN Algolia (free, no key). USPTO patents for pre-launch technical signal.

### Layout notes
- Two-column list of tools and data sources.
- Each entry includes a right-aligned status label such as FREE, FREE TIER, RECOMMENDED, ALTERNATIVE, or OPEN DATA.
- Light background with divider lines.

---

## Slide 06 — Demo Scenario / Reference Product

**Section label:** DEMO SCENARIO · REFERENCE PRODUCT

### Product
# Vector Agents

*vectoragents.ai · AI-powered digital workers automating business functions end-to-end*

### Prompt block
**Run your system against real questions:**

> “Is Lilian competitive in the AI SDR market right now? Where does Vector stand?”

> “Is the digital workers category accelerating or consolidating - and what does that mean for Vector’s roadmap?”

> “What should Vector Agents build or reposition over the next six months to capture emerging demand?”

### Note
*The solution must generalise to any product. Vector Agents is the example, not the constraint.*

### Layout notes
- Full teal background.
- Very large white product name.
- Italic subtitle and italic question prompts.
- Divider lines between sections.

---

## Slide 07 — Evaluation Criteria

**Section label:** EVALUATION CRITERIA  
**Footer:** 05 · EVALUATION

### Headline
**What we’re judging.**

### Subhead
*Five dimensions. Use the right column to calibrate your build before the demo.*

### Evaluation table
| Criterion | Weight | What excellent looks like |
|---|---:|---|
| Core Algorithm (Multi-Agent System) | 25% | 6+ coordinated agents, parallelism, lifecycle management, tool / MCP usage. Not a wrapper. |
| Product Design Strategy | 25% | Dynamic inline artifacts, clarification chips, seamless UX. Feels designed, not assembled. |
| Intelligence Quality & Grounding | 20% | Multi-source, confidence-scored, facts vs interpretation separated. Grounded, not hallucinated. |
| Scalability & Cost Efficiency for GTM | 15% | Cloud-deployable, cost-per-query estimated, horizontal scale considered. |
| Demo Strength & Generalisability | 15% | Live on Vector Agents + demonstrated generalisation to another product or context. |

### Layout notes
- Light background.
- Large bold headline.
- Large evaluation table with black header row.
- Weight column highlighted with teal percentages.

---

## Overall visual style observed

- Presentation alternates between **light slides with teal accents** and **full teal slides with white text**.
- Typography uses **large bold sans-serif headlines**, smaller section labels, and italic emphasis for quotes or framing lines.
- Most slides use **thin horizontal divider lines** to separate sections.
- Footers include slide numbering and section names on the light slides.
