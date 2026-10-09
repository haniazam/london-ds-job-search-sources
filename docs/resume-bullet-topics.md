# Resume Work-Experience Bullet Topics — Dimension Extraction

**Source documents (content used verbatim, nothing invented):**
- `Dimensions.pdf` — *Six Dimensions of a Senior DS Bullet* (the rubric; five content dimensions used here)
- `RN.pdf` — *H1 2026 Performance Review: Hani Azam* (recent Meta work, Jan–May 2026)
- `Hani_Azam_FactBank_WithCandidates.docx` — masked career fact bank + unplaced Meta Senior DS candidate bullets

**The five dimensions (per the rubric):**
1. **Action verb** — ownership-conveying first word (execution-tier vs influence-tier)
2. **Method** — the named technical/analytical technique (the "how")
3. **Scope** — size/reach: team, data volume, market, operational scale, time horizon, regulatory
4. **Quantified metric** — a relative change the work caused (%, ×, pp, ratio, banded)
5. **Business outcome** — the downstream decision/reallocation/strategic shift (the "so what")

**Flag legend:** ✅ present & strong · 🟡 weak/partial · ❌ not available in the source documents

> Note on cross-referencing: several Performance-Review topics have a matching masked **FactBank candidate** that supplies a method or number the review omits. Where that happens it is called out, because the number exists in the documents and only needs to be attached to the topic.

---

## Part 1 — Recent Meta work (H1 2026 Performance Review, enriched by matching FactBank candidates)

These are the rawest topics: the review is rich on context and ownership but thin on quantified metrics, so this is where flagging matters most.

### T1. PE Creation Funnel PMF Analysis
- **Context:** Hypothesis-driven roadmap analysis identifying growth levers across the Product Extensions (PE) adoption funnel; cited as the half's biggest achievement and primary archetype work.
- **Narrative:** Decomposed the end-to-end PE creation funnel, formed hypotheses about what drives successful creation, and quantified the drivers — turning a loosely-defined "where do we grow PE?" question into a ranked set of levers that fed the roadmap.
- **Dimensions:**
  - Action verb — ✅ *Decomposed / Quantified / Identified* (analytical-tier; "owned hypothesis-driven modeling")
  - Method — ✅ funnel decomposition + hypothesis-driven modeling, multi-source structured analysis
  - Scope — 🟡 "PE adoption funnel," "across multiple product teams" — qualitative; **no numeric reach** (no # of markets/segments/records)
  - Quantified metric — ❌ no number stated for the levers identified or their size
  - Business outcome — ✅ informed/shaped PE roadmap priorities (decision adoption / strategic redirect)

### T2. PEAR Measurement Framework & Topline Dry Run (canonical ecommerce-ads measurement)
- **Context:** Co-owned the PEAR goaling methodology (*PCA Eligibility as % of Meta Revenue*) and built the H2 2026 topline dry-run plus 3-year projections — described as the canonical measurement source for ecommerce ads.
- **Narrative:** Defined the goaling metric and built the measurement instrument that sets revenue targets for the entire ecommerce-ads org, spanning multiple product teams.
- **Dimensions:**
  - Action verb — ✅ *Established / Defined* (influence-tier; "co-owned the goaling methodology")
  - Method — ✅ measurement-framework design / goaling methodology (PCA Eligibility as % of Meta Revenue); 3-year projection model
  - Scope — ✅ "entire ecommerce ads org," "multiple product teams," "3-year" horizon (org + time-horizon scope, though not a hard number)
  - Quantified metric — ❌ no quantified change (it's a framework that *sets* targets, not one that moved a number)
  - Business outcome — ✅ sets targets for the whole ecommerce-ads org (capability shift / strategy) — strong, but **not attached to a real figure**

### T3. H1'26 Cumulative Revenue Forecast (Promo Ads / CAG iRev)
- **Context:** Built the primary revenue-tracking instrument for the Promo Ads v-team, integrating multiple data sources and maintaining forecast accuracy; owned CAG Promo Ads across H1'26 roadmap planning and the 2026 LRP, including iRev sizing and attribution due diligence.
- **Narrative:** Engineered the forecasting instrument the v-team runs revenue against, folding in multiple sources and keeping it accurate enough to anchor planning.
- **Dimensions:**
  - Action verb — ✅ *Built / Engineered* (execution-tier)
  - Method — ✅ revenue forecasting integrating multiple data sources; (FactBank pairs this work with "bottoms-up models and scenario analysis")
  - Scope — 🟡 "Promo Ads v-team / CAG"; FactBank's adjacent bullet supplies "**400-person organisation, 20+ analysts, two divisions**" if this is framed as the org-wide target-sizing work
  - Quantified metric — 🟡 "maintaining forecast accuracy" is asserted, not quantified; FactBank's related bullet carries "**hundreds of millions of dollars** in revenue commitments" as scope-proxy
  - Business outcome — ✅ primary instrument informing H1 roadmap + 2026 LRP investment decisions
  - *Flag:* the accuracy claim needs a real number (e.g., forecast-error %) to satisfy the metric dimension.

### T4. Promo Ads H1 iRev Goal Deferral / LRP Refresh
- **Context:** Proactively identified that H1 iRev goals were unreachable, built the case, and secured approval to defer — preventing wasted effort and setting realistic H2 targets; also refreshed LRP assumptions shaping multi-half investment priorities. (Review flags it as *reactive/late* — a growth area.)
- **Narrative:** Re-ran the long-range revenue picture, found the targets were badly overstated, and convinced leadership to reset them before more effort was sunk against them.
- **Dimensions:**
  - Action verb — ✅ *Re-prioritised / Secured / Re-oriented* (influence-tier)
  - Method — ✅ cohort-level trajectory modelling + scenario analysis (named in the matching FactBank bullet)
  - Scope — ✅ "three product teams" / multi-half / 2026 LRP horizon (FactBank)
  - Quantified metric — ✅ **7× overestimation in long-range revenue targets** (FactBank candidate — this is the number the review omits)
  - Business outcome — ✅ reset the strategic investment portfolio across product/eng/finance directors (investment reallocation) — very strong
  - *Flag:* fully 5/5 **only when** the FactBank "7×" figure is attached; the Performance Review alone is metric-❌.

### T5. PE Health v2 "Locked-in" Classifier
- **Context:** Designed a modeling approach to segment advertiser adoption maturity, with direct product application. Growth note: not yet scaled to proactive monitoring/alerting (would strengthen the "systematic AI integration" signal).
- **Narrative:** Built a classifier that buckets advertisers by how locked-in / mature their adoption is, so product can target the right cohorts.
- **Dimensions:**
  - Action verb — ✅ *Designed / Modelled* (execution-tier)
  - Method — ✅ classification / segmentation modeling (a named technique like gradient boosting or SHAP attribution would sharpen it — **not specified** in the source)
  - Scope — 🟡 "advertiser adoption maturity" — no count of advertisers/segments given
  - Quantified metric — ❌ no accuracy, precision, or coverage figure stated
  - Business outcome — 🟡 "direct product application" asserted but not named concretely (no decision/reallocation tied to it yet)
  - *Flag:* weakest topic on metric + outcome; currently a capability, not a result.

### T6. Email Capture — Cooldown Experiment, i18n Extraction & Opt-in Funnel
- **Context:** Designed, ran, and read out experiments on the email-capture (opt-in) feature with clear business implications; published on Workplace; supported migration/adoption with funnel diagnostics and launch-criteria analytics. Matching FactBank candidate explicitly covers decomposing the opt-in funnel and running experiments that lifted opt-in rates.
- **Narrative:** Broke down the email opt-in funnel, found the drop-off points, and designed experiments (incl. a cooldown test and i18n extraction) that raised opt-in while holding advertiser-quality guardrails steady.
- **Dimensions:**
  - Action verb — ✅ *Designed / Ran / Decomposed*
  - Method — ✅ A/B experimentation + end-to-end funnel decomposition
  - Scope — 🟡 "email opt-in feature," internationalised (i18n) — reach not quantified
  - Quantified metric — ❌ **[ADD METRIC]** — opt-in lift (pp/%) is required and not present in either document (FactBank tags this candidate "NEEDS NUMBERS · 2/5")
  - Business outcome — 🟡 informed launch criteria / migration-adoption decisions (concrete-ish, but no number behind it)
  - *Flag:* metric is the blocker; this is the lowest-readiness candidate in the bank.

### T7. SEV S634713 Investigation (incident / measurement-anomaly root cause)
- **Context:** Led root-cause analysis of a measurement anomaly (opt-in-rate decline SEV) under time pressure, with financial-impact quantification; documented findings to prevent incorrect result interpretation; maintained SEV monitoring/debug workflow to isolate drivers and confirm recovery.
- **Narrative:** Drove the diagnosis of a production measurement anomaly, sized its financial impact, and wrote it up so the org wouldn't misread the affected results — then kept monitoring until recovery was confirmed.
- **Dimensions:**
  - Action verb — ✅ *Diagnosed / Led* (analytical/leadership-tier)
  - Method — ✅ root-cause analysis / measurement-anomaly diagnosis + monitoring workflow
  - Scope — 🟡 "production incident," "measurement integrity" — severity named (SEV) but no numeric blast-radius
  - Quantified metric — 🟡 "financial impact quantification" is referenced but **the figure itself is not given** in the documents
  - Business outcome — ✅ reduced decision risk / prevented incorrect interpretations (risk avoided) — strong qualitatively
  - *Flag:* the dollar figure exists ("quantified") but isn't in these docs — retrieve it to make the metric ✅.

### T8. Track 3A User-Influence Measurement Strategy (PCA)
- **Context:** Authored the DS Reference Doc, defined the metrics, and ran bi-weekly HPMs — setting measurement direction for a key growth track; drove metrics clarification and aligned targets/definitions across stakeholders.
- **Narrative:** Owned the measurement definition for a growth track end-to-end: wrote the reference doc, set the metrics, and ran the recurring forum that kept stakeholders aligned on targets.
- **Dimensions:**
  - Action verb — ✅ *Defined / Authored / Aligned* (influence-tier)
  - Method — 🟡 metric definition / measurement-strategy design — **no named technical method** (acceptable per rubric for an influence bullet, but worth noting)
  - Scope — 🟡 "a key growth track," cross-stakeholder — not numerically sized
  - Quantified metric — ❌ none stated
  - Business outcome — ✅ set measurement direction + aligned targets/definitions across stakeholders (capability/strategy)
  - *Flag:* a legitimate "method-light" influence bullet; carries on scope+outcome, but both are unquantified.

### T9. Four-Quadrant Addressable TAM Analysis
- **Context:** Sized the total addressable opportunity to inform H2 strategy, identifying where to focus resources. Matching FactBank bullet supplies the figures (redefined market sizing for a key advertiser segment).
- **Narrative:** Independently re-sized the market for a key advertiser segment, exposing how much adoption (and revenue) was being left on the table, and pointed H2 resourcing at it.
- **Dimensions:**
  - Action verb — ✅ *Sized / Estimated / Redefined*
  - Method — ✅ four-quadrant TAM framework + funnel decomposition + cohort modelling (FactBank)
  - Scope — ✅ "a key advertiser segment" (market/segment reach)
  - Quantified metric — ✅ **17pp adoption gap**, **multimillion-dollar unrealised annual revenue** (FactBank, banded)
  - Business outcome — ✅ drove an immediate strategic pivot adopted by product & engineering directors (strategic redirect)
  - *Flag:* 5/5 when fused with the FactBank market-sizing bullet; from the Performance Review alone, metric is ❌.

### T10. Advertiser Co-Creation Program / "What 8 Advertiser Conversations Taught Us" / Extensions Feedback Pipeline
- **Context:** Translated qualitative advertiser signal into quantitative product direction; led the Promo Ads Co-Creation Program bridging external users and internal product teams; built the Extensions escalation/feedback pipeline and published the Q1 summary.
- **Narrative:** Stood up the channel that carries advertiser feedback into product, then turned eight advertiser conversations into ranked, quantitative roadmap input.
- **Dimensions:**
  - Action verb — ✅ *Translated / Synthesised / Established* (communication/leadership-tier)
  - Method — 🟡 qualitative→quantitative synthesis + feedback-pipeline design — **no named technical method**
  - Scope — 🟡 "8 advertiser conversations" works only as a small scope-proxy; pipeline reach not sized
  - Quantified metric — ❌ no outcome metric (8 is an input count, not a result)
  - Business outcome — ✅ influenced PE roadmap priorities (decision adoption)
  - *Flag:* strong story, but metric-❌ and method-light; best framed as an influence/communication bullet.

### T11. AI-Integrated Experimentation Methodology (HBT guides, AIP, guardrail framework)
- **Context:** Used AI to build reusable capabilities (HBT methodology guides, AIP process docs) and published AI-related experiment methodology for the broader team; advanced experimentation methodology (HBT selection, AIP process improvements). Matching FactBank candidate: an experimentation guardrail framework with drift monitoring.
- **Narrative:** Standardised how the team runs experiments — built guardrails that let many A/B tests run concurrently without corrupting measurement, and packaged the method (HBT selection, AIP) as reusable guides for other DSs.
- **Dimensions:**
  - Action verb — ✅ *Standardised / Established* (influence-tier)
  - Method — ✅ experimentation guardrail framework + drift monitoring; HBT (hold-back test) selection methodology
  - Scope — ✅ "**12% of traffic**" / broader team (operational scale) — FactBank
  - Quantified metric — ✅ **~20% increase in experimentation velocity** (FactBank candidate)
  - Business outcome — ✅ preserved measurement integrity + reduced decision risk (capability shift)
  - *Flag:* FactBank marks this "READY · 4/5 · overlaps existing holdout-framework bullet" — strong, but **de-duplicate** against the established holdout-framework bullet (B-Meta-7 below) to avoid reusing a verb/claim.

### T12. PE Spend-Reactivation / Opt-out-Reduction — Behavioural Segmentation & Propensity Models
- **Context:** Built frameworks for PMF segmentation, opt-out reduction, and spend reactivation (RN Projects #1). Matching FactBank candidate: behavioural segmentation + propensity models on advertiser telemetry to flag dormant/anomalous cohorts and guide product & sales interventions.
- **Narrative:** Modeled advertiser telemetry to flag dormant and anomalous accounts, giving product and sales a targeted list to reactivate spend.
- **Dimensions:**
  - Action verb — ✅ *Built / Modelled*
  - Method — ✅ behavioural segmentation + propensity models (anomaly/dormancy flagging)
  - Scope — 🟡 "advertiser telemetry / dormant cohorts" — population not sized
  - Quantified metric — ❌ **[ADD METRIC]** — # accounts reactivated **and** $ incremental revenue both missing (FactBank: "NEEDS NUMBERS · 3/5")
  - Business outcome — 🟡 guides product & sales interventions (named motion, but unquantified)
  - *Flag:* two numbers needed before use.

### T13. Ad-to-Offer Relevance Scoring (mismatched-promotion detection)
- **Context:** FactBank candidate — built a relevance-scoring prototype for ad-to-offer matching that flagged mismatched promotions in code-based vs code-free ads, informing delivery improvements. (Relates to catalog-quality work in RN Projects #5.)
- **Narrative:** Prototyped a scorer that catches when an ad and its promotion don't match, quantifying how often mismatches occur by promo type to point delivery fixes at the worst cases.
- **Dimensions:**
  - Action verb — ✅ *Built / Prototyped*
  - Method — ✅ relevance-scoring model for ad-to-offer matching
  - Scope — 🟡 split by ad type (code-based vs code-free) — descriptive, not sized
  - Quantified metric — 🟡 diagnostic figures present (**16%** of code-based, **45%** of code-free ads flagged) but the **realised delivery improvement is [ADD METRIC]** (FactBank: "NEEDS NUMBERS · 3/5")
  - Business outcome — 🟡 "informing delivery improvements that [ADD METRIC]" — outcome named but not quantified
  - *Flag:* has a strong *diagnostic* number but no *outcome* number; the 16/45% pair is a method-detail, not the impact.

### T14. Commerce-Ads Transaction-Share Quasi-Experiment
- **Context:** FactBank candidate (READY · 5/5) — quasi-experimental analysis on transaction records to quantify how on-platform transaction share drives advertising revenue.
- **Narrative:** Designed a quasi-experiment over hundreds of millions of transactions to isolate the causal link between on-platform transaction share and ad revenue, then used it to re-prioritise multi-year commerce-ads investment.
- **Dimensions:**
  - Action verb — ✅ *Designed*
  - Method — ✅ quasi-experimental analysis (in Spark)
  - Scope — ✅ **>400M transaction records** (data-volume scope)
  - Quantified metric — ✅ **1pp share rise → low-single-digit % ad-revenue uplift** (banded causal estimate)
  - Business outcome — ✅ re-prioritised multi-year commerce-ads investment (investment reallocation)
  - *Flag:* none — all five present and balanced. Strongest unplaced candidate.

---

## Part 2 — Established, already-complete bullets (FactBank placed bullets)

These already satisfy all five dimensions; listed compactly as topics for reuse/tailoring. Flags note only residual weaknesses.

| # | Topic | Action | Method | Scope | Quantified metric | Business outcome | Flag |
|---|-------|--------|--------|-------|-------------------|------------------|------|
| B1 | Advertiser-churn / incentive-removal modelling (Meta Sr DS) | Modelled | cohort survival analysis, 4 incentive-removal scenarios | two organisations | multimillion-dollar revenue exposure (banded) | delayed deprecation + funded personalised-incentive initiative | ✅ all 5 |
| B2 | Multi-armed bandit recommendation validation (Meta Sr DS) | Validated | multi-armed bandit + CRO alternatives | billions of daily ad impressions | +1.2% relevance score | multimillion-$ annualised revenue claim approved | ✅ all 5 |
| B3 | Personalised-ads A/B tests w/ holdouts (Meta Sr DS) | Designed/Executed | A/B tests w/ holdout controls | 20+ audience segments | 3.1% incremental sales lift (vs 2.6% target) | informed GTM strategy adopted by product/eng | 🟡 "lift" is a banned synonym per rubric → reword to *raised/grew* |
| B4 | First holdout-based experimentation framework (Meta Sr DS) | Established | holdout-based experimentation framework | three product teams | +43% statistical power; 9.2pp adoption (vs 7pp) | enabled measurement capability | 🟡 overlaps T11 (guardrail framework) — pick one |
| B5 | Advertiser-facing quality-preview tool (Meta Sr DS) | Delivered/Launched | causal inference on ad-creative signals | ~50K advertisers | 0.15% ROAS lift (+0.26% further opp) | secured continued product investment | ✅ all 5 |
| B6 | Feature-adoption → GMV analysis (Meta DS) | Identified | correlation + segmentation analysis | ~30K active merchants | ~18% GMV; ~12% projected topline | new product team + platform redesign funded | ✅ all 5 |
| B7 | Merchant-churn cohort analysis (Meta DS) | Quantified | cohort retention analysis | four team roadmaps | 10% active attrition rate | VP reprioritised retention + tracking dashboards | ✅ all 5 |
| B8 | Acquisition-to-adoption funnel definition (Meta DS) | Defined | stakeholder mapping + metric decomposition | 6+ teams, two orgs | hundreds of millions $ targets (scope-proxy) | goal framework VP used for annual targets | 🟡 metric is scope-proxy, not a caused change |
| B9 | License→subscription propensity model (Adobe) | Developed | propensity modelling | ~8K enterprise accounts | 15% above-baseline conversion; ~$3m ARR | first-year ARR contribution | ✅ all 5 |
| B10 | Activation metrics + in-app messaging A/B (Adobe) | Defined/Validated | A/B testing of in-app messaging | ~200K enterprise users | 5pp MAU lift | scaled programme to all N.A. accounts | 🟡 "lift" wording |
| B11 | Time-series forecasting across KPIs (Adobe) | Engineered | time-series forecasting + anomaly detection | 12 product KPIs | 7pp forecast-error reduction; days→hours | faster exec response (time recovered) | ✅ all 5 |
| B12 | GTM account-ranking propensity model (Adobe) | Built | gradient-boosted propensity model + feature importance | enterprise accounts | 3% pipeline increase | sales prioritisation | 🟡 scope not numerically sized |
| B13 | Customer-journey data pipelines (Adobe BI) | Architected | pipeline integration (Salesforce/SAP/Hadoop/D&B) | 10+ source systems | 70% weekly reporting-time cut | self-serve dashboards replace manual | ✅ all 5 |
| B14 | Product-analytics function from scratch (Adobe BI) | Established | activation-metric definition + 10+ user interviews | 1K alpha users | 60% week-one activation | secured full GA investment | ✅ all 5 |
| B15 | NLP nonprofit-matching pipeline (Berkeley) | Engineered | NLP matching pipeline | 1K+ nonprofits | +30pp corporate engagement | CSR-to-mission matching | ✅ all 5 |
| B16 | Funding-prioritisation ranking model (Berkeley) | Developed | R-based ranking model | ~40 student orgs, $1.8M | 8h→1h/week reconciliation | automated budget tracking (time compression) | ✅ all 5 |
| B17 | Occupation recommendation system (Delta project) | Led | TF-IDF/fastText + hierarchical taxonomy | 4-person team; ~15K users | ~40% precision improvement | expanded career-guidance coverage | ✅ all 5 |
| B18 | Homelessness rehab predictors (C4SF project) | Developed | logistic regression | ~5K client records | ~78% accuracy | policy recs adopted by 3 administrators | 🟡 accuracy is a model stat, not a business metric |
| B19 | Nonprofit data integration (ShelterTech project) | Delivered | ETL pipelines + dashboards | three teams | 5 days → same-day reporting | enabled weekly data-driven reviews | ✅ all 5 (time compression) |

---

## Summary of dimension gaps (where to focus before drafting)

**Topics missing a quantified metric (highest priority to fill):**
- T1 PE Creation Funnel PMF — no size on the levers identified
- T2 PEAR framework — framework that *sets* targets; no caused change
- T5 PE Health v2 classifier — no accuracy/coverage/outcome number
- T6 Email Capture opt-in — opt-in lift `[ADD METRIC]`
- T8 Track 3A strategy — no number; also method-light
- T10 Co-Creation / 8 conversations — no outcome metric
- T12 Dormant-account reactivation — # accounts + $ revenue both `[ADD METRIC]`

**Topics where the number exists in the FactBank but isn't in the Performance Review** (just attach it):
- T4 Goal deferral / LRP → **7× overestimation**
- T9 TAM → **17pp gap, multimillion-$**
- T11 Experimentation methodology → **12% of traffic, ~20% velocity**

**Method-light topics** (acceptable for influence bullets per the rubric, but flagged): T8, T10 — carry on scope + outcome, no named technical method.

**De-duplication / wording flags:** T11 ↔ B4 overlap (holdout/guardrail framework — keep one); B3/B10 use the banned word "lift" → reword to *raised/grew/increased*; the rubric also requires each action verb to appear at most once across the whole resume, so the verb choices above will need a final pass when these topics are assembled into one document.
