# Resource 2: Prompt Engineering Workbook

**Feature 2 · AI Engineering Bootcamp · BlockseBlock**

The fastest way to get better at prompting is to read weak prompts, understand *why* they fail, and rewrite them. This workbook gives you 10 examples to work through.

The first two are fully solved so you can see the pattern. The remaining eight are yours to fix — use your actual domain in every answer.

---

## How to Use This Workbook

For each exercise:
1. Read the **weak prompt** and think about what could go wrong when a model receives it.
2. Read the **what's wrong** diagnosis.
3. Write your improved version in the **Your improved prompt** box.
4. (Optional) Paste your improved prompt into Swagger at `/docs` and compare outputs.

---

## ✅ Worked Example 1 — Too Vague

**Weak prompt:**

```
You are an assistant. Help the user.
```

**What's wrong:**
- No domain context — the model has no idea what industry, company, or topic this is about.
- No tone or style guidance — formal? casual? brief? verbose?
- No constraints — the model can freely speculate, make things up, or go wildly off-topic.
- "Help the user" is circular — it tells the model nothing it doesn't already know.

**Improved prompt:**

```
You are the virtual assistant for Alpine Trail Co., an outdoor gear retailer
specializing in hiking, camping, and trail running equipment.

Your role: help customers with product questions, store policies, and gear
recommendations. If a question is outside your domain (e.g., medical advice,
politics), politely redirect the user to a relevant expert.

Tone: friendly, knowledgeable, and concise. Aim for replies under 150 words
unless a detailed comparison is explicitly requested.

If you don't know a specific product detail (stock levels, exact specs), say so
clearly rather than guessing — offer to help the customer find the right contact.
```

**Why this works:**
- Clear domain + company identity
- Specific role (what to do) and anti-role (what NOT to do)
- Tone and length constraint
- Honest uncertainty policy — tells the model what to do when it doesn't know

---

## ✅ Worked Example 2 — Conflicting Instructions

**Weak prompt:**

```
Answer questions about our HR policies.
Be thorough and cover all edge cases.
Keep responses under 50 words.
Always cite the exact policy section number.
```

**What's wrong:**
- "Be thorough and cover all edge cases" directly conflicts with "under 50 words".
- "Cite the exact policy section number" is impossible without the actual policy document loaded — the model will hallucinate section numbers.
- No guidance on what to do when these instructions clash.

**Improved prompt:**

```
You are the HR Policy Assistant for [YOUR_COMPANY].

Answer employee questions about HR policies accurately and concisely (2-3
sentences for simple questions, up to a short paragraph for complex ones).

Important: you do NOT have access to the policy documents yet. If a question
requires a specific policy section, clause, or clause number, say: "I can
give you general guidance, but please verify this in the official policy
document at [POLICY_PORTAL_URL] or contact HR directly."

Never invent policy details, section numbers, or dates.
```

**Why this works:**
- Removes the length conflict by giving context-sensitive guidance
- Acknowledges a real limitation (no document access yet — Feature 4 fixes this)
- Explicit instruction for what to say instead of making things up
- Leaves the door open for the RAG upgrade in Week 2

---

## Exercise 1 — No Output Format

**Weak prompt:**

```
You are a restaurant recommendation assistant. Suggest a restaurant to the user.
```

**What's wrong:** The model can return a single name, a five-paragraph essay, a bulleted list, or a haiku — all are technically valid. There is no output format specified, so every response will look different, making it impossible to build a consistent UI around it.

**Your improved prompt for [YOUR_DOMAIN]:**

> *Hint: tell the model exactly what format to use (e.g., "respond in this JSON format:", or "use exactly three sentences", or "use a bulleted list with these fields").*

```
[Write your improved prompt here]
```

---

## Exercise 2 — No Persona, No Constraints

**Weak prompt:**

```
Answer real estate questions.
```

**What's wrong:** The model doesn't know if it's a buyer's agent, a seller's agent, a property manager, or a legal expert. It will answer authoritatively even about things it shouldn't (e.g., legal advice), because there's no instruction telling it to hold back.

**Your improved prompt for [YOUR_DOMAIN]:**

> *Hint: give the assistant a specific role, a specific limitation ("you are not a lawyer / doctor / financial advisor"), and an instruction for what to do at the edge of its expertise.*

```
[Write your improved prompt here]
```

---

## Exercise 3 — Ignores Edge Cases

**Weak prompt:**

```
You are a travel planning assistant. Help users plan their trips.
```

**What's wrong:** What happens when the user asks about a destination under a travel advisory? A country the assistant has no data on? A trip that involves dangerous activities? Silence on edge cases means the model will improvise — and improvisation in a travel context can cause real harm.

**Your improved prompt for [YOUR_DOMAIN]:**

> *Hint: think about 2-3 "what if" edge cases in your domain and address them explicitly. What should the assistant say or NOT say in each case?*

```
[Write your improved prompt here]
```

---

## Exercise 4 — The Hallucination Trap

**Weak prompt:**

```
You are a customer support agent for Alpine Trail Co. Answer questions about
our products, prices, and availability.
```

**What's wrong:** The model doesn't have access to Alpine Trail Co.'s real product catalog, real prices, or real inventory. Without an explicit instruction about this limitation, it will confidently invent plausible-sounding prices and product details — which will be wrong and potentially damage trust.

**Your improved prompt for [YOUR_DOMAIN]:**

> *Hint: explicitly tell the model what data it does NOT have. Then tell it what to do instead — "direct the customer to the website", "say you'll check and get back to them", etc.*

```
[Write your improved prompt here]
```

---

## Exercise 5 — Too Permissive

**Weak prompt:**

```
You are an AI assistant. Answer any question the user asks as helpfully as possible.
```

**What's wrong:** "Any question" and "as helpfully as possible" will cause the model to answer questions completely outside your domain (legal advice, medical diagnosis, competitor comparisons, offensive requests). There is no scope, no off-ramp for out-of-scope queries, and no safety guardrail.

**Your improved prompt for [YOUR_DOMAIN]:**

> *Hint: define your scope ("you only discuss X"), write a polite decline template for out-of-scope requests, and decide what counts as out of scope for your domain.*

```
[Write your improved prompt here]
```

---

## Exercise 6 — No Examples (Few-Shot Opportunity)

**Weak prompt:**

```
Classify the user's message as either "complaint", "question", or "compliment".
Reply with the classification and a short response.
```

**What's wrong:** Without examples, the model's classification boundary is blurry. "This product is terrible but I still bought another one" — complaint or compliment? The model will guess. One or two examples ("here is a complaint, here is a compliment") dramatically improve consistency.

**Your improved prompt for [YOUR_DOMAIN]:**

> *Hint: add 2 concrete examples to your classification prompt using the format: `User: "..." → Category: "..." → Response: "..."`*

```
[Write your improved prompt here]
```

---

## Exercise 7 — Length Mismatch

**Weak prompt:**

```
You are a personal finance coach. Explain compound interest.
```

**What's wrong:** "Explain" could mean one sentence, one paragraph, or a 2,000-word essay. The same prompt sent to a chat UI (needs brevity) and a lesson generator (needs depth) should produce different outputs — but without a length instruction, it's a coin flip.

**Your improved prompt for [YOUR_DOMAIN]:**

> *Hint: add a length instruction appropriate to HOW students will use this in the UI. A chat bubble and a printed handout need very different lengths.*

```
[Write your improved prompt here]
```

---

## Exercise 8 — Inconsistent JSON

**Weak prompt:**

```
Respond with a JSON object containing the user's name and their main question.
```

**What's wrong:** The model may return `{"name": ..., "question": ...}` OR `{"user_name": ..., "main_question": ...}` OR wrap it in markdown fences (```json...```). Without a precise schema and explicit "no markdown" instruction, every response risks being structured differently.

**Your improved prompt for [YOUR_DOMAIN]:**

> *Hint: show the exact JSON schema you want (with field names and types), say "respond ONLY with the JSON object", and explicitly forbid markdown code fences.*

```
[Write your improved prompt here]
```

---

## Reflection Questions

After completing the exercises, think about these:

1. **What is the single highest-impact change you made most often?** (Adding constraints? Adding examples? Clarifying output format?)

2. **Which exercise was hardest for your domain?** Why?

3. **Look at the system prompt you wrote for `_STRUCTURED_SYSTEM_PROMPT` in `starter/main.py`.** With fresh eyes from this workbook, what would you change?

4. **Token cost:** count the tokens in your original system prompt and your improved version (use the Swagger UI and check the token count in the provider's response). Is the longer prompt worth the cost?

---

## Further Reading

- [GLOSSARY.md — System Prompt](../../../GLOSSARY.md#system-prompt) — plain-English definition
- [GLOSSARY.md — Temperature](../../../GLOSSARY.md#temperature) — why lower temperature helps with structured output
- [GLOSSARY.md — Token](../../../GLOSSARY.md#token) — why prompt length matters for cost
