# Current-model availability and parameter parity assessment

**Date:** 2026-08-31  
**Experiment:** `model_sensitivity_2026-08-31` (extension)  
**Probe script:** ad-hoc pre-run probes via existing `OPENAI_API_KEY`

---

## 1. Models probed

| Model ID | Exists / accessible | Notes |
|----------|---------------------|-------|
| `gpt-5.6-terra` | Yes | Returns snapshot `gpt-5.6-terra` |
| `gpt-5.6-sol` | Yes | Returns snapshot `gpt-5.6-sol` |
| `gpt-5.6-luna` | Yes | Returns snapshot `gpt-5.6-luna` |
| `gpt-5.6-terra-medium` | No | 404 model_not_found |
| `gpt-5.6-sol-medium` | No | 404 model_not_found |
| `gpt-5.6-luna-medium` | No | 404 model_not_found |

---

## 2. chat.completions — temperature=0

All three GPT-5.6 models **reject** `temperature=0`:

```
Unsupported value: 'temperature' does not support 0 with this model.
Only the default (1) value is supported.
```

**Implication:** Strict parameter parity with the legacy panel (temperature=0) is **impossible** for GPT-5.6 on this endpoint.

---

## 3. chat.completions — reasoning_effort

| Configuration | gpt-5.6-terra | gpt-5.6-sol | gpt-5.6-luna |
|---------------|---------------|-------------|--------------|
| No parameters (default) | OK; JSON array | OK; JSON array; 22 reasoning tokens | OK; JSON array; 32 reasoning tokens |
| `reasoning_effort='none'` | OK; JSON array | OK; JSON array | OK; JSON array |
| `reasoning_effort='low'` | OK | OK | OK |

**Selected for extension runs:** `reasoning_effort='none'` on every call.

**Temperature for extension runs:** parameter **omitted** (API default = 1).

---

## 4. Responses API (exploratory probe only)

`client.responses.create(model=..., input=prompt, reasoning={'effort': 'none'})` succeeded for all three models and returned JSON-like text.

**Not used for recovery runs** because switching endpoint would change both model family behaviour and API semantics relative to the completed gpt-4o/gpt-4o-mini panel. Documented as non-comparable exploratory path only.

---

## 5. JSON / schema behaviour

Probe with `INQUIRY_PROMPT_TEMPLATE` on short inquiry text:

- All three GPT-5.6 models returned parseable JSON **arrays** of decision objects with four fields.
- No probe parse failures when using `reasoning_effort='none'`.

---

## 6. Panel qualification summary

| Panel | Models | Endpoint | Temperature | Reasoning | Comparable to legacy? |
|-------|--------|----------|-------------|-----------|---------------------|
| **Legacy (complete)** | gpt-4o-mini, gpt-4o | chat.completions | 0 | n/a | Baseline reference |
| **Extended current** | gpt-5.6-terra, sol, luna | chat.completions | omitted (default 1) | none (explicit) | **Partial** — documented caveat |
| **Exploratory** | any via Responses API | responses | n/a | none | **No** — not run |

---

## 7. Luna admission decision

`gpt-5.6-luna` is admitted to the extended panel:

- Same parity profile as terra/sol
- Probe latency and token counts comparable (~490 tokens vs ~445–474 on short text)
- Marginal incremental cost for three repetitions × six excerpts

---

## 8. Legacy rerun requirement

**None.** No technical reason requires rerunning gpt-4o-mini or gpt-4o on the GPT-5.6 parameter profile. Legacy and extended panels are reported separately.

---

## 9. Conclusion

Extension proceeds for **gpt-5.6-terra**, **gpt-5.6-sol**, and **gpt-5.6-luna** under the amended protocol with explicit parameter caveats. No model qualifies for the strict original temperature=0 primary panel beyond the already-completed legacy pair.
