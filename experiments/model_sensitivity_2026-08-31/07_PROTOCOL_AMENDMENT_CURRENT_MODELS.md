# Protocol amendment — current-generation OpenAI models

**Registered:** 2026-08-31 (before any new comparative recovery results were examined)  
**Amends:** `00_PROTOCOL.md`  
**Experiment:** `model_sensitivity_2026-08-31`

---

## 1. Why the experiment is being extended

The original model-sensitivity run (2026-08-31) compared `gpt-4o-mini` and `gpt-4o` under fixed 7/2 extraction with `temperature=0`. To broaden the robustness check to **current-generation OpenAI models** without rerunning or altering completed legacy results, this amendment adds a bounded excerpt-level panel for GPT-5.6 models.

Purpose remains supplementary robustness only — **not** model benchmarking or corpus-wide model selection.

---

## 2. Models proposed

| Model | Role in extension |
|-------|-------------------|
| `gpt-4o-mini` | Original production baseline — **already complete; not rerun** |
| `gpt-4o` | Legacy higher-tier comparison — **already complete; not rerun** |
| `gpt-5.6-terra` | Current balanced model — **new runs** |
| `gpt-5.6-sol` | Current flagship model — **new runs** |
| `gpt-5.6-luna` | Optional current model — **new runs if admitted** |

---

## 3. Current OpenAI model IDs (verified by pre-run probe)

| Requested ID | Accessible | Returned snapshot |
|--------------|------------|-----------------|
| `gpt-5.6-terra` | Yes | `gpt-5.6-terra` |
| `gpt-5.6-sol` | Yes | `gpt-5.6-sol` |
| `gpt-5.6-luna` | Yes | `gpt-5.6-luna` |

---

## 4. API parity findings (pre-run; no recovery results inspected)

### Endpoint

| Model family | Endpoint tested | Result |
|--------------|-----------------|--------|
| gpt-4o / gpt-4o-mini (original) | `chat.completions.create` | Used in completed runs |
| GPT-5.6 (proposed) | `chat.completions.create` | **Works** with JSON-array output |
| GPT-5.6 | `responses.create` | Works but **not adopted** — would change API surface alongside model |

**Decision:** GPT-5.6 extension uses **`chat.completions`** only, matching the legacy runs' endpoint class.

### Temperature

| Model | `temperature=0` | Behaviour |
|-------|-----------------|-----------|
| gpt-4o-mini / gpt-4o | Supported | Used in original protocol |
| gpt-5.6-terra / sol / luna | **Rejected** | API error: only default temperature (1) supported |

**No silent substitution.** Temperature parameter is **omitted** for GPT-5.6 runs; API default applies. This is a **documented parameter difference** from the legacy panel.

### Reasoning configuration

| Setting | Result |
|---------|--------|
| `reasoning_effort='none'` (chat.completions kwarg) | **Accepted**; preferred setting |
| Default (no explicit effort) | May allocate reasoning tokens (observed on sol/luna probes) |
| `reasoning_effort='low'` | Accepted but **not used** — would increase reasoning divergence |

**Chosen setting for GPT-5.6 runs:** `reasoning_effort='none'` explicitly on every call.

### Structured / JSON output

All three GPT-5.6 models returned valid JSON arrays matching the inquiry-mode schema on probe text when using `reasoning_effort='none'`.

### Prompt / message semantics

Unchanged: single user message with `INQUIRY_PROMPT_TEMPLATE.format(text=chunk)`.

---

## 5. Qualification for panels

### Strict primary comparable panel (original protocol: temp=0)

| Model | Status |
|-------|--------|
| gpt-4o-mini | **Complete** (3/6 · 3/6 · 3/6) — preserved |
| gpt-4o | **Complete** (0/6 · 1/6 · 2/6) — preserved |
| gpt-5.6-terra | **Not qualified** — temperature=0 incompatible |
| gpt-5.6-sol | **Not qualified** — temperature=0 incompatible |
| gpt-5.6-luna | **Not qualified** — temperature=0 incompatible |

### Extended current-model panel (amended protocol)

Models admitted under documented caveats (same endpoint, same prompt/schema/matching; **reasoning_effort=none**; temperature omitted):

| Model | Admitted |
|-------|----------|
| gpt-5.6-terra | **Yes** |
| gpt-5.6-sol | **Yes** |
| gpt-5.6-luna | **Yes** — probe cost/latency comparable; adds breadth at marginal incremental runtime |

GPT-5.6 results are reported in **separate extended outputs** (`09_*`–`13_*`) and must not be merged numerically with the temp=0 legacy panel without explicit caveat.

### Exploratory / non-comparable

| Item | Status |
|------|--------|
| Responses API path | Documented only; not run for recovery comparison |
| GPT-5.6 with default/medium reasoning | Not run — would confound model with reasoning level |

---

## 6. Unchanged elements

- Six excerpts; six frozen manual decisions
- 7/2 window; inquiry prompt; preprocessing; schema; traceability; deduplication
- Deterministic automated matching (chunk/overlap experiment logic)
- Three independent repetitions per **new** model
- All existing metrics and interpretation rules
- Historical Phase 1 **5/6** safeguard
- 414-entry dataset frozen
- No inferential significance testing

---

## 7. Repetition plan (extension only)

| Model | Repetitions | Rerun legacy? |
|-------|-------------|---------------|
| gpt-5.6-terra | 3 | No |
| gpt-5.6-sol | 3 | No |
| gpt-5.6-luna | 3 | No |
| gpt-4o-mini | — | **No** (preserve existing) |
| gpt-4o | — | **No** (preserve existing) |

Raw outputs: `raw_responses_extended/{model}/rep{n}/` — separate from legacy `raw_responses/`.

---

## 8. Decision rules (unchanged plus extension caveat)

- Do not claim best/superior/optimal model
- Do not equate automated recovery with historical 5/6 human triangulation
- When comparing across panels, state explicitly: legacy panel used temperature=0; extended GPT-5.6 panel used reasoning_effort=none with API-default temperature

---

*This amendment was written before examining GPT-5.6 comparative recovery results.*
