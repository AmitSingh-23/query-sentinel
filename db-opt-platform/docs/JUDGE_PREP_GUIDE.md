# 🏆 QuerySentinel — Complete Judge Preparation Guide

> **What is it in one line?** QuerySentinel is a privacy-aware, AI-assisted PostgreSQL performance optimization platform that diagnoses slow queries, recommends indexes/rewrites/partitioning using GNN + RL + LangGraph agents, simulates them safely with HypoPG, and generates staging migrations — all without ever exposing raw data to AI.

---

## Table of Contents

1. [THE BIG PICTURE — How it Works End-to-End](#1-the-big-picture)
2. [PRIVACY & SECURITY — The Judge Will Definitely Ask](#2-privacy--security)
3. [GNN — Graph Neural Network (Exact Algorithm Details)](#3-gnn--graph-neural-network)
4. [RL — Reinforcement Learning (Exact Algorithm Details)](#4-rl--reinforcement-learning)
5. [LangGraph — Multi-Agent System](#5-langgraph--multi-agent-system)
6. [HypoPG Sandbox — How Simulation Works](#6-hypopg-sandbox)
7. [Blast Radius — Write Impact Analysis](#7-blast-radius)
8. [Reverse Mapping — How Pseudonymisation Works](#8-reverse-mapping--pseudonymisation)
9. [SQL Rewriting — What Rewrites Are Done](#9-sql-rewriting)
10. [Partitioning & Sharding Advisory](#10-partitioning--sharding)
11. [Evidence Chain — How Trust Is Built](#11-evidence-chain)
12. [Dashboard — What Each Tab Shows](#12-dashboard--what-each-tab-shows)
13. [BYOD — Bring Your Own Data](#13-byod--bring-your-own-data)
14. [Results You Can Quote](#14-results-you-can-quote)
15. [Likely Judge Questions & Best Answers](#15-likely-judge-questions--best-answers)
16. [Quick Glossary of Technical Terms](#16-quick-glossary)

---

## 1. THE BIG PICTURE

### What problem does it solve?

A DBA (Database Admin) manually reads `EXPLAIN` output to figure out why a query is slow. They guess an index, hope it doesn't slow writes, and if they use AI for help, they risk **exposing customer emails, IDs, and amounts** to the AI model.

### End-to-End Flow (memorize this!)

```
User gives: SQL query / NL question / historical logs
    ↓
① SECURITY GATEWAY — Only single read-only SELECT allowed
    ↓
② PII PRE-FILTER — Detects emails, UUIDs, phone numbers, JWT tokens
    ↓
③ PRIVACY VAULT — Replaces all literals ($1, $2...) + HMAC pseudonyms (orders → tbl_a31f7c)
    ↓
④ SCHEMA INSPECTOR — Reads catalog metadata (no rows), pseudonymises it
    ↓
⑤ EXPLAIN — Runs EXPLAIN (FORMAT JSON) in READ ONLY transaction
    ↓
⑥ PLAN → GRAPH — Converts execution plan tree to PyTorch Geometric graph
    ↓
⑦ GNN ANALYSIS — GCN classifies the bottleneck (or deterministic rules fallback)
    ↓
⑧ LANGGRAPH SUPERVISOR — Routes to specialist agents (fan-out):
    ├── SQL Rewriter (rewrites slow patterns)
    ├── Schema Expert (partition/shard advice)
    └── Index Strategist (proposes indexes)
    ↓
⑨ RL OPTIMIZER — Q-learning agent ranks and selects best action
    ↓
⑩ RECOMMENDATION VALIDATOR — Translates pseudonyms back, validates DDL
    ↓
⑪ HYPOPG SANDBOX — Creates hypothetical indexes, compares EXPLAIN before/after
    ↓
⑫ BLAST RADIUS — Checks write workload impact of proposed indexes
    ↓
⑬ FINAL REPORT — Evidence chain + staging migration + rollback script
```

### Six Questions It Answers

1. **Why is this query slow?** → Plan parsing + GNN diagnosis
2. **What optimization strategies are candidates?** → Index strategist + SQL rewriter + Schema expert
3. **Which strategies have evidence?** → Evidence chain + validator
4. **What does PostgreSQL estimate if the proposed index exists?** → HypoPG sandbox
5. **What's the write impact?** → Blast-radius analysis
6. **What should a DBA review before staging?** → Migration + rollback + limitations

---

## 2. PRIVACY & SECURITY

### If the judge asks: "How do you protect data?"

**Three layers of protection:**

#### Layer 1: AST Parameterisation (using `pglast` library)
- **What it does:** Parses SQL into an Abstract Syntax Tree, replaces ALL literal values with `$1`, `$2`, `$3`...
- **Example:** `WHERE email = 'amit@example.com' AND amount > 5000` → `WHERE email = $1 AND amount > $2`
- The algorithm is **pglast AST visitor** — walks every `A_Const` node and replaces with `ParamRef`
- GROUP BY 1 / ORDER BY 2 are kept because they are structural ordinals, not data

#### Layer 2: Structural Pseudonymisation (HMAC-SHA256)
- **What it does:** Replaces table/column names with deterministic pseudonyms
- **Algorithm:** `HMAC-SHA256(name, secret_key)` → take first 6 hex chars → `tbl_a31f7c`
- **Example:** `orders → tbl_a31f7c`, `tenant_id → col_c81d44`
- **Why HMAC?** Deterministic (same input = same output, so workload history stays comparable) but **NOT reversible** without the key

#### Layer 3: Outgoing Payload Guard (`llm_guard.py`)
- Before ANY text goes to an LLM, it's scanned for:
  - PII patterns (email, phone, UUID, JWT, API keys, passwords, connection strings)
  - Raw literals from the original query
  - Real identifiers from the reverse map
- **Any hit → BLOCKS the call**, writes a `PRIVACY_BLOCK` audit event

### The Reverse Map (IMPORTANT — judges love asking this)

- A `RequestVault` object stores: `forward` (original → pseudonym), `reverse` (pseudonym → original), `literals` ($n → value)
- It lives **in-memory on the trusted backend only**
- It is **NEVER** returned by the API, never logged, never sent to LLM
- It has a **TTL** (30 min default) and is explicitly cleared when the request ends
- Used ONLY at step ⑩ (validator) to translate recommendations back to real names

### Security Gateway
- Uses `pglast` to parse SQL into AST
- Accepts EXACTLY one `SelectStmt`
- Rejects: DDL, DML, COPY, SET, ALTER SYSTEM, VACUUM, SELECT INTO, FOR UPDATE
- Blocks dangerous functions: `pg_read_file`, `pg_sleep`, `dblink`, `lo_*`, `set_config`, `nextval` (50+ functions)
- Blocks credential catalogs: `pg_authid`, `pg_shadow`, `pg_user_mappings`
- **User SQL is NEVER executed.** Only `EXPLAIN (FORMAT JSON)` runs, in a READ ONLY transaction

---

## 3. GNN — Graph Neural Network

### If the judge asks: "What GNN architecture do you use?"

**Answer:** GCN — Graph Convolutional Network (Kipf & Welling, 2017), specifically using PyTorch Geometric's `GCNConv` layers.

### Architecture (memorize this)

```
GCNConv(32 → 32) → ReLU → GCNConv(32 → 16) → ReLU → global_max_pool → Linear(16 → 4)
```

- **Input:** 32 features per node
- **Output:** 4 classes (softmax probabilities)
- **Graph readout:** `global_max_pool` — takes the max across all node embeddings to get one graph-level vector

### The 4 Bottleneck Classes

| Class ID | Name | Meaning |
|----------|------|---------|
| 0 | Unindexed Sequential Scan | Table being scanned without an index |
| 1 | High-Cost Nested Loop / Join | Expensive join operation |
| 2 | Heavy Sort / Aggregation | Costly sorting or grouping |
| 3 | Efficient / No Major Bottleneck | Query is already fine |

### How the Plan Becomes a Graph

1. **Nodes** = plan operators (Seq Scan, Hash Join, Sort, etc.)
2. **Edges** = parent↔child links (added in BOTH directions so message passing goes up AND down)
3. **32 Node Features:**
   - 13 one-hot for operator type (Seq Scan=0, Index Scan=1, ... Materialize=11, Other=12)
   - 4 one-hot for operator family (scan, join, sort_agg, other)
   - log1p of: startup cost, total cost, rows, width, exclusive cost, loops
   - effective cost share, depth, has_filter, has_index_cond, is_parallel, is_subplan
   - is_top_effective_cost, share_gap_to_max, log_plan_total_cost

### Cost Attribution (key innovation)

- **SubPlan children:** Charged per outer row (correlated subquery runs once per parent row)
- **Nested Loop inner side:** Charged per outer row
- **LIMIT children:** Charged only for the fraction consumed (LIMIT total / child total)
- This is why Scenario C's 319M cost is correctly attributed to the inner Seq Scan running ~4,668 times

### GATv2 (Optional upgrade, behind feature flag `QS_FEATURE_GATV2`)

- **Algorithm:** GATv2Conv — Graph Attention Network v2 (Brody, Alon & Yahav, 2021)
- Architecture: `GATv2Conv(32→16, 2 heads) → ELU → GATv2Conv(32→16, 2 heads, concat=False) → ELU → global_max_pool → Linear(16→4)`
- Uses **edge features** (8-dim): flow direction, Outer/Inner relationship, is parent a join, join type
- **Attention is exposed** for interpretability — shows which edges the model "pays attention to"
- Attention is labelled as "structural importance signal (interpretability aid, not causal proof)"

### Training

- Trained on **synthetic labelled plans** (no public labelled plan corpus exists)
- Generator creates PostgreSQL-shaped EXPLAIN plans for each class
- Cheap distractor operators are added for robustness
- **Results:** Held-out accuracy 100%, unseen plan shapes 83.5%

### Fallback Mode

- If checkpoint is missing/corrupt → switches to **deterministic rule-based analysis**
- Rules check cost share, operator types, loop counts
- Fallback says `rule:high`, never reports a fake probability
- The API and dashboard ALWAYS say which mode was used

---

## 4. RL — Reinforcement Learning

### If the judge asks: "What RL algorithm do you use?"

**Answer:** Hierarchical Tabular Q-Learning with invalid-action masking.

### Algorithm Details

| Parameter | Value |
|-----------|-------|
| Algorithm | Tabular Q-learning |
| Learning rate (α) | 0.2 |
| Discount factor (γ) | 0.9 |
| Exploration | ε-greedy, starts at 1.0, decays by 0.993 per episode, minimum 0.05 |
| Update rule | Q(s,a) ← Q(s,a) + α × (reward + γ × max_a' Q(s',a') - Q(s,a)) |
| Episodes | Multi-step, up to 3 actions per episode |

### Why "Hierarchical"?

Two levels of Q-tables:

1. **High-level Q-table** `Q_high[state][high_action]` → chooses the TYPE of action:
   - `ADD_INDEX` | `REWRITE_SQL` | `PARTITION` | `SHARD_ADVISORY` | `NO_CHANGE`

2. **Low-level Q-table** `Q_low[state|high][signature]` → chooses the SPECIFIC action:
   - For ADD_INDEX: `composite:eq+range`, `single:join`, `partial:range|partial`, `covering:eq+range+inc`
   - For REWRITE_SQL: `correlated_count_subquery_to_left_join`

### State Encoding (discretised, identifier-free)

The state is a string like `bc0|cb4|cr1|ss1|jn0|sa0|sp0|eq2|rg1|ns0|ix0|ts2|wf0|pt0|ia0`

| Code | Feature | Values |
|------|---------|--------|
| bc | Bottleneck class (from GNN) | 0-3 |
| cb | Cost bucket (log10 planner cost) | 0-7 |
| cr | Cardinality bucket (log10 rows) | 0-7 |
| ss | Has sequential scan | 0/1 |
| jn | Has join | 0/1 |
| sa | Has sort/aggregate | 0/1 |
| sp | Has subplan | 0/1 |
| eq | Number of equality filters | 0-2 |
| rg | Has range filter | 0/1 |
| ns | Has non-sargable predicate | 0/1 |
| ix | Existing index coverage | 0 none, 1 partial, 2 full |
| ts | Table size bucket | 0-3 |
| wf | Write frequency bucket | 0-2 |
| pt | Partition suitable | 0/1 |
| ia | Indexes added in episode | 0-3 |

### Invalid-Action Masking (if judge asks: "How do you prevent invalid actions?")

Before the policy sees the action set, these are removed:
- Actions referencing nonexistent identifiers
- Duplicate/redundant indexes
- Already-taken actions within the episode
- Safety-policy violations

### Reward Formula

```
reward = w_freq × normalized_planner_cost_reduction
         − storage_penalty − write_penalty − redundancy_penalty − risk_penalty
```

- `w_freq = 1 + log10(1 + workload_calls)` — frequent queries matter more
- `storage_penalty = 0.10 × min(1, index_bytes / table_bytes)`
- `write_penalty = 0.04 × index_columns × write_factor` (0.25/0.6/1.0)
- `redundancy_penalty = 0.30` if redundant, `0.02` if <1% cost change
- `risk_penalty`: PARTITION 0.05, SHARD 0.08, rewrite 0.02 (verified) / 0.20 (unverified)

### Generalisation for Unseen States

Three-level backoff:
1. **Exact state key** → use Q-values directly
2. **Coarse key** → simpler key with only the most predictive features
3. **State-marginal values** → average Q-value across all states for that action (reported as backoff)

### Results

- Seen templates: trained 0.599 vs rule fallback 0.512 (reward)
- **Unseen templates: trained 0.767 vs rule fallback 0.511** (key selling point!)
- Recommendation validity: 100% for both

---

## 5. LANGGRAPH — Multi-Agent System

### If the judge asks: "How does the agent system work?"

**Answer:** It's a compiled LangGraph `StateGraph` with conditional routing.

### The Graph

```
START → security → privacy → schema → explain → plan_to_graph → gnn
  → supervisor (ROUTES based on diagnosis):
      ├── sql_rewriter (SKIPPED if no rewrite applies)
      ├── schema_expert (always runs)
      └── index_strategist (SKIPPED if plan is efficient)
  → supervisor_merge → rl_optimizer → recommendation_validator
  → hypopg_sandbox (SKIPPED if nothing valid)
  → blast_radius (SKIPPED if planner didn't use the indexes)
  → final_report → END
```

### Key Conditional Routing

| Condition | What happens |
|-----------|-------------|
| SQL rewriter has no applicable pattern | SKIPPED |
| GNN says "efficient" AND no dominant scan | Index strategist SKIPPED |
| No valid candidates after validation | HypoPG sandbox SKIPPED |
| Planner didn't use the virtual indexes | Blast radius SKIPPED |
| Rewrite has HIGH semantic risk | Rewrite BLOCKED |
| Any error at any stage | All subsequent stages → SKIPPED, goes to final_report |

### Agents

| Agent | What it does |
|-------|-------------|
| **SQL Rewriter** | 4 deterministic rewrite operators (correlated subquery → LEFT JOIN, non-sargable cast → range, etc.) |
| **Schema Expert** | Analyses schema for partitioning/sharding opportunities using table size, correlation, predicates |
| **Index Strategist** | Proposes single/composite/partial/covering indexes based on access patterns |
| **Supervisor** | Routes to the right agents based on the GNN diagnosis |

### LLM Integration (optional)

- LLM is **optional** — everything works without it using deterministic agents
- When enabled, LLM proposes additional rewrites/indexes
- Every LLM payload is checked by the `llm_guard` before sending
- Labelled `ANALYTIC FALLBACK` when no LLM, `LLM RECOMMENDATION` when LLM is used

---

## 6. HYPOPG SANDBOX

### If the judge asks: "How do you simulate index performance?"

**Answer:** Using HypoPG — a PostgreSQL extension for hypothetical indexes.

### How it works (step by step)

1. **Baseline EXPLAIN** — get the current plan cost
2. **Create hypothetical index** — `SELECT * FROM hypopg_create_index('CREATE INDEX ON orders(tenant_id, order_date)')`
3. **EXPLAIN again** — get the new plan cost with the virtual index
4. **Per-candidate attribution** — test each index alone first
5. **Combined experiment** — keep only indexes the planner actually used AND that cut cost by ≥1%
6. **Capture size** — `hypopg_relation_size()` for storage estimate
7. **CLEANUP** — `hypopg_reset()` in a `finally` block (ALWAYS runs even on failure)

### Key safety features

- Everything runs in ONE connection inside a **READ ONLY** transaction
- Hypothetical indexes are **backend-local** (only visible on that connection)
- `hypopg_reset()` is in a `finally` block — always cleans up
- Cost reduction = `((before − after) / before) × 100` — labelled as **PLANNER ESTIMATE, NOT RUNTIME**

### Rewrite simulation

- If a SQL rewrite exists, EXPLAIN it too (without and with indexes)
- If combining rewrite + indexes is WORSE than the best single option, it says "deploy one or the other, not both"

---

## 7. BLAST RADIUS

### If the judge asks: "How do you assess write impact?"

**Answer:** Two methods — heuristic estimation from pg_stat_statements AND direct timing on a temp copy.

### Method 1: Heuristic from pg_stat_statements

1. Fetch INSERT/UPDATE/DELETE statements from `pg_stat_statements`
2. Parse with pglast, match to the index's target table
3. Rank by call frequency, analyse top 3
4. Per operation:
   - INSERT: adds one index entry per row
   - UPDATE: extra work ONLY if it modifies an indexed column (also loses HOT eligibility)
   - DELETE: leaves dead entries for VACUUM

### Method 2: Write Latency Simulation (`structural_sim.py`)

1. Create temp copy with ~20,000 sampled rows + existing indexes
2. Insert 4,000 rows, measure median time (7 trials)
3. **A-B-A pattern**: baseline → add proposed index → measure → remove index → baseline again
4. This cancels timing drift
5. Result: **ms per 1,000 inserted rows** and **ms per single-row write**
6. Labelled **SIMULATED** (order-of-magnitude estimate)

### Risk Classification

- **LOW:** < 100 write calls, no indexed column updates
- **MEDIUM:** > 100 write calls OR touches indexed columns
- **HIGH:** > 1,000 calls AND touches indexed columns, OR index > 50MB and size ratio > 50%

---

## 8. REVERSE MAPPING — How Pseudonymisation Works

### The full cycle:

```
REAL: SELECT * FROM orders WHERE customer_email = 'amit@example.com' AND amount > 5000

MASKED: SELECT * FROM tbl_a31f7c WHERE col_c81d44 = $1 AND col_8f2b11 > $2

(Only the trusted backend knows: tbl_a31f7c = orders, col_c81d44 = customer_email, $1 = 'amit@example.com')

AI / LLM only ever sees the MASKED version
```

### How it works technically:

1. **pglast** parses SQL into AST (Abstract Syntax Tree)
2. `_LiteralCollector` visitor walks all `A_Const` nodes → replaces with `ParamRef($n)`
3. `_IdentifierRewriter` visitor walks all `RangeVar`, `ColumnRef`, `Alias` → replaces with HMAC pseudonyms
4. The vault stores forward+reverse maps
5. At recommendation validation (step ⑩), pseudonyms are translated BACK using the reverse map
6. The reverse map is NEVER exposed to the API or LLM

### Why HMAC-SHA256?

- **Deterministic:** Same input always produces the same pseudonym → workload history stays comparable
- **Not reversible:** You cannot go from `tbl_a31f7c` back to `orders` without the secret key
- **Collision handling:** If two names produce the same token within a request, the hash length is increased by 2

---

## 9. SQL REWRITING

### 4 Deterministic Rewrite Operators:

| Operator | Before | After |
|----------|--------|-------|
| Correlated COUNT subquery → LEFT JOIN | `WHERE (SELECT COUNT(*) ...) > 0` | `LEFT JOIN ... WHERE ... IS NOT NULL` |
| Non-sargable date cast → range | `WHERE CAST(col AS DATE) = '2026-01-01'` | `WHERE col >= '2026-01-01' AND col < '2026-01-02'` |
| IN with large list → VALUES join | `WHERE id IN (1,2,...,100)` | `JOIN (VALUES (1),(2),...) AS v ON id = v.column1` |
| Redundant DISTINCT on unique | `SELECT DISTINCT id FROM ... WHERE pk = ...` | `SELECT id FROM ...` |

### Semantic Diff (`sql_semantic_diff.py`)

- After rewriting, checks that the structural shape is preserved
- Not a formal proof of equivalence
- HIGH risk rewrites are **blocked** automatically
- All rewrites labelled "requires human review"

---

## 10. PARTITIONING & SHARDING

### Partitioning Advisory

**Evidence used:** table size, range predicates on date/timestamp, physical correlation, equality access on tenant-like keys, n_distinct, skew

### Partition Simulation

1. Create temp sample copy (60,000 rows) — flat
2. Create temp PARTITIONED copy (monthly range OR 8 hash partitions)
3. ANALYZE both
4. EXPLAIN a representative query on both
5. Report: partitions scanned vs total, cost on each
6. **Example result:** Scenario B scans 1 of 36 monthly partitions, −94% planner cost

### Always labelled: "Advisory - Requires isolated design/benchmark validation"
### NEVER included in migration scripts — needs design work

---

## 11. EVIDENCE CHAIN

Every recommendation carries a chain of evidence with labels:

| Label | Meaning | Example |
|-------|---------|---------|
| POSTGRES OBSERVED | Real data from PostgreSQL catalogs | Table has 1M rows |
| PLANNER ESTIMATE | From EXPLAIN | Total cost = 23,103 |
| HYPOPG SIMULATION | Virtual index experiment | Cost dropped 21% |
| SIMULATED | Temp copy timing | +1.09 ms per 1,000 rows |
| ANALYTIC FALLBACK | Rule-based, not ML | "seq scan bottleneck" |
| TRAINED GNN | From the trained model | "class 0, confidence 0.92" |
| RL POLICY | From the trained RL agent | "chose ADD_INDEX" |
| HEURISTIC ESTIMATE | Calculated from known inputs | "medium write risk" |
| MEASURED SANDBOX | From opt-in benchmark | "57ms → 30ms" |

---

## 12. DASHBOARD — What Each Tab Shows

| Tab | What it shows |
|-----|-------------|
| **Privacy Audit** | Raw SQL (marked SENSITIVE) vs anonymised SQL (marked SAFE), PII types found, literal count, pseudonym count |
| **Execution Plan / GNN** | Plan tree with bottleneck in red, operator cost chart, GNN class probabilities |
| **LangGraph Agents** | Agent status tree (QUEUED/RUNNING/COMPLETED/SKIPPED/REJECTED), live SSE event stream |
| **Optimization** | Original vs rewritten SQL with diff, proposed indexes, partition advice, RL action with Q-values |
| **HypoPG** | Before vs after planner cost, virtual indexes, storage and write overhead, blast radius |
| **Deployment Review** | Staging migration SQL, rollback SQL, rationale, human-review banner |
| **Evidence Chain** | Full chain with provenance labels |
| **Workload Intelligence** | File upload, pg_stat_statements collector, regressions, drift chart, index hygiene |
| **Benchmark Lab** | Different modes (baseline/index_only/rewrite_only/gnn_assisted/rl_assisted/full) and ablations |

---

## 13. BYOD — Bring Your Own Data

### Two data sources:

1. **Demo Database** — pre-seeded `public` schema (never modified)
2. **Upload Dataset (CSV, JSON)** — loaded into `qs_dynamic` schema

### Upload flow:

- **Preview** → detects format, column types, warnings (nothing written yet)
- **Commit** → loads in one transaction
- Re-uploads only ADD nullable columns; incompatible files are rejected with bad values and row numbers

### Ask Your Database (NL-to-SQL):

- Plain English → ONE SELECT statement
- 10-stage safety gate: parse, SELECT-only, catalog check, relation/column check, function allowlist, EXPLAIN cost cap, row cap, read-only restricted role
- Works WITHOUT LLM (template generator, labelled ANALYTIC FALLBACK)
- With LLM, failed validations are fed back for repair

---

## 14. RESULTS YOU CAN QUOTE

| Scenario | What happened | Result |
|----------|-------------|--------|
| A (join) | Seq Scan on order_items → added order_items(product_sku) + orders(tenant_id, order_date) | **−72.8% planner cost** |
| B (weekly report) | Bitmap scan → added orders(tenant_id, order_date) | **−21.3% planner, −47.6% runtime** (57→30ms) |
| C (correlated subquery) | Inner Seq Scan ×4,668 → FK index + LEFT JOIN rewrite | **−99.98% planner cost** (319M → 49K) |
| D (cast + email) | Non-sargable cast → range rewrite + email index | **−99.9% planner, −99.98% runtime** (44ms → 0.009ms) |
| E (efficient) | Already fast | No change recommended ✓ |

**GNN:** Held-out 100%, unseen plan shapes 83.5%
**RL:** Unseen templates reward 0.767 vs 0.511 for rules (50% better!)
**Privacy:** 100% of literals masked, zero raw data exposed

---

## 15. LIKELY JUDGE QUESTIONS & BEST ANSWERS

### Q: "What is the GNN doing exactly?"
**A:** "We use a GCN (Graph Convolutional Network) that takes the PostgreSQL execution plan tree as a graph — each operator is a node with 32 features, edges connect parent-child operators bidirectionally. Two GCN layers with a global max pool produce a graph-level embedding, then a linear layer classifies into 4 bottleneck types. We also have an optional GATv2 upgrade that uses attention to show WHICH edges in the plan the model focuses on."

### Q: "What RL algorithm and why tabular instead of deep?"
**A:** "We use hierarchical tabular Q-learning because the state space is compact and discrete — about 15 features each with 2-8 values. A deep network would need much more training data than we have. The hierarchy (high-level action type, then low-level signature) keeps the action space manageable. For unseen states, we back off from exact → coarse → marginal values, which gives good generalization — unseen template reward is 0.767 vs 0.511 for the rule baseline."

### Q: "How is reverse mapping done?"
**A:** "The RequestVault keeps a forward map (real → pseudonym) and reverse map (pseudonym → real) in memory on the trusted backend. When the AI recommends CREATE INDEX ON tbl_a31f7c(col_c81d44), the validator uses the reverse map to translate it back to CREATE INDEX ON orders(tenant_id). The vault is NEVER sent over the API, never logged, and has a 30-minute TTL."

### Q: "How do you ensure the AI never sees real data?"
**A:** "Three layers: (1) pglast AST parameterisation removes ALL literals, (2) HMAC-SHA256 replaces all identifiers, (3) an outgoing payload guard scans every LLM message for PII, secrets, raw literals, and real identifiers — any hit blocks the call. We also never execute user SQL — only EXPLAIN runs, in a READ ONLY transaction."

### Q: "Is HypoPG a real performance improvement?"
**A:** "HypoPG gives us PLANNER ESTIMATES, not runtime. The cost reduction percentage is from EXPLAIN costs. For actual runtime proof, we have an opt-in benchmark mode that runs EXPLAIN ANALYZE on a disposable database. In Scenario B, the planner estimated −21.3% but measured runtime was −47.6%."

### Q: "What if the GNN or RL model isn't available?"
**A:** "Both have explicit fallback modes. The GNN falls back to deterministic cost-share rules (e.g., 'seq scan with >30% cost share = unindexed scan bottleneck'). The RL falls back to a rule-based policy. The API and dashboard ALWAYS say which mode is active — trained or analytic_fallback. They never fake a probability."

### Q: "How is this different from just using ChatGPT to optimize queries?"
**A:** "Three critical differences: (1) Privacy — ChatGPT sees your real data; we anonymise everything before AI touches it. (2) Evidence — ChatGPT gives opinions; we give evidence (HypoPG cost reduction, blast radius, write latency, measured benchmarks). (3) Safety — ChatGPT might suggest changes you blindly apply; we generate staging migrations with rollback scripts and say 'human review required'."

### Q: "What's novel about this project?"
**A:** "(1) The privacy-preserving pipeline — AST parameterisation + HMAC pseudonymisation + outgoing guard is a complete privacy chain purpose-built for SQL. (2) GNN on execution plan graphs — treating EXPLAIN output as a graph classification problem with cost attribution for subplans. (3) Hierarchical RL with invalid-action masking that only proposes actions grounded in schema evidence. (4) The end-to-end evidence chain where every number carries its provenance."

### Q: "What are the limitations?"
**A:** Be honest: "Planner estimates ≠ runtime. GNN is trained on synthetic plans. RL workload is small (15 templates). Only 4 rewrite operators. PII detection is pattern-based. Write latency is timed on small temp copies. The vault is in-memory/single-process. We're transparent about all of this in our report."

---

## 16. QUICK GLOSSARY

| Term | What it means |
|------|-------------|
| **pglast** | Python library that parses PostgreSQL SQL into an AST (Abstract Syntax Tree) |
| **HMAC-SHA256** | Hash-based Message Authentication Code — deterministic but irreversible hash |
| **GCN** | Graph Convolutional Network — a type of GNN |
| **GATv2** | Graph Attention Network v2 — GNN with attention weights |
| **PyTorch Geometric** | Library for graph neural networks on top of PyTorch |
| **Q-learning** | RL algorithm that learns a value (Q) for each state-action pair |
| **ε-greedy** | Exploration strategy: random action with probability ε, best action otherwise |
| **LangGraph** | Framework for building multi-agent workflows as state machines |
| **StateGraph** | LangGraph's graph type — nodes are functions, edges have conditions |
| **HypoPG** | PostgreSQL extension for hypothetical (virtual) indexes |
| **EXPLAIN** | PostgreSQL command that shows the query execution plan without running the query |
| **EXPLAIN ANALYZE** | Actually runs the query and shows real timing (only used in opt-in benchmark) |
| **pg_stat_statements** | PostgreSQL extension that tracks query execution statistics |
| **Blast radius** | The impact of adding an index on write performance |
| **HOT update** | Heap-Only Tuple — fast PostgreSQL update that doesn't touch indexes |
| **SARGABLE** | "Search ARGument ABLE" — a predicate that can use an index |
| **Non-sargable** | Can't use an index (e.g., CAST(col AS DATE) = ...) |
| **Covering index** | Index that includes extra columns in INCLUDE clause to avoid table lookup |
| **Partial index** | Index with a WHERE clause — only indexes matching rows |
| **Composite index** | Index on multiple columns |
| **CREATE INDEX CONCURRENTLY** | Creates index without locking the table for writes |
| **SSE** | Server-Sent Events — real-time streaming of pipeline progress |
| **Provenance** | Where a number came from (observed, estimated, simulated, measured) |

---

> **Remember:** Always be honest about limitations. Say "planner estimate, not runtime" when talking about HypoPG results. Say "synthetic training data" when talking about GNN. The judges will respect honesty more than overclaiming.
