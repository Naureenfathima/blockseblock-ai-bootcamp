# Pick Your Domain

**AI Engineering Bootcamp · BlockseBlock**

One of the most valuable things you can do before Week 1 starts is to choose the domain your AI assistant will serve. The course uses **Alpine Trail Co.** (a fictional outdoor gear retailer) as its built-in example — but you'll learn more, and your final project will be more impressive, if you replace it with something meaningful to you.

Spend 10 minutes reading through the options below, then fill in your choice in your `.env` file:

```
ASSISTANT_NAME=<your assistant's name>
ASSISTANT_DESCRIPTION=You are a helpful assistant for <your domain>. <one sentence describing its purpose.>
```

---

## How to Use This Guide

For each domain you'll find:

- **The pitch** — one sentence on why this assistant is useful
- **Week 2 documents** — three documents you would upload in Feature 4–6 (RAG week)
- **Week 3 agent actions** — three functions you'd add in Features 7–9 (tool calling / agent week)

These aren't exhaustive — they're starting points to help you imagine what *your* version looks like.

---

## Domain 1: Healthcare Clinic FAQ

**The pitch:** Patients ask the same 50 questions over and over ("Do you accept my insurance?", "How do I request a referral?") — this assistant frees up front-desk staff to focus on care.

**Week 2 — Documents to upload:**
1. Patient intake FAQ (PDF)
2. Insurance accepted list (PDF or text)
3. Appointment and cancellation policy (text)

**Week 3 — Agent actions:**
1. `check_appointment_availability(date, provider_name)` — query a calendar API
2. `lookup_insurance_status(insurance_provider_name)` — check an accepted-plans list
3. `send_appointment_reminder(patient_email, appointment_time)` — send a confirmation email

---

## Domain 2: HR Policy Assistant

**The pitch:** "How many vacation days do I have left?", "What's the parental leave policy?" — answers are buried in 200-page handbooks. This assistant finds them in seconds.

**Week 2 — Documents to upload:**
1. Employee handbook (PDF)
2. Benefits summary (PDF)
3. Expense reimbursement policy (PDF)

**Week 3 — Agent actions:**
1. `lookup_employee_pto_balance(employee_id)` — query an HR system API
2. `submit_leave_request(employee_id, start_date, end_date, type)` — submit a form
3. `find_hr_contact(topic)` — route the question to the right HR team member

---

## Domain 3: E-Commerce Customer Support

**The pitch:** Automate first-line support for an online store — handle order status, returns, and product questions without a human in the loop.

**Week 2 — Documents to upload:**
1. Return and refund policy (text)
2. Shipping FAQ (text)
3. Product catalog excerpt (PDF or CSV)

**Week 3 — Agent actions:**
1. `get_order_status(order_id)` — call an orders API
2. `initiate_return(order_id, reason)` — start the returns process
3. `check_product_availability(product_sku)` — query inventory

---

## Domain 4: Education Tutor

**The pitch:** A patient, always-available study assistant that answers curriculum-specific questions, explains concepts multiple ways, and quizzes students on demand.

**Week 2 — Documents to upload:**
1. Course syllabus and learning objectives (PDF)
2. Lecture notes or textbook chapter excerpts (PDF)
3. Past exam questions and solutions (PDF)

**Week 3 — Agent actions:**
1. `generate_quiz(topic, num_questions)` — generate practice questions
2. `explain_concept(concept_name, level)` — give a simple/intermediate/advanced explanation
3. `track_student_progress(student_id, topic)` — update a learning tracker

---

## Domain 5: Real Estate Advisor

**The pitch:** Buyers and renters have thousands of questions before they commit. This assistant handles the early research phase — property details, neighbourhood info, process questions — so agents focus on closing.

**Week 2 — Documents to upload:**
1. Sample property listings (PDF or text)
2. Neighbourhood guide (text)
3. First-time buyer FAQ (PDF)

**Week 3 — Agent actions:**
1. `search_listings(location, max_price, bedrooms)` — query a listings API
2. `schedule_viewing(property_id, preferred_date)` — book a viewing slot
3. `calculate_mortgage_estimate(price, down_payment, rate)` — run a calculation

---

## Domain 6: Restaurant Recommender

**The pitch:** A local food concierge that knows the menu, ambiance, and availability of every restaurant in your area — and makes a recommendation in under 10 seconds.

**Week 2 — Documents to upload:**
1. Sample menus (PDFs or text)
2. Restaurant profiles / about pages (text)
3. Allergy and dietary information sheets (text)

**Week 3 — Agent actions:**
1. `search_restaurants(cuisine, location, price_range)` — query a restaurant database
2. `check_availability(restaurant_id, party_size, date_time)` — check OpenTable-style availability
3. `make_reservation(restaurant_id, party_size, date_time, contact_email)` — book a table

---

## Domain 7: Travel Planner

**The pitch:** Planning a trip involves dozens of decisions and tabs. This assistant holds the whole itinerary in mind and helps build it piece by piece — flights, hotels, activities, budget.

**Week 2 — Documents to upload:**
1. Travel destination guide (PDF)
2. Sample itineraries for the destination (text)
3. Visa and entry requirements (text)

**Week 3 — Agent actions:**
1. `search_flights(origin, destination, date, num_passengers)` — call a flight search API
2. `search_hotels(location, check_in, check_out, guests)` — call a hotel search API
3. `convert_currency(amount, from_currency, to_currency)` — perform a live conversion

---

## Domain 8: Personal Finance Coach

**The pitch:** Most people know they should budget — they just don't have a patient, judgment-free helper who can explain concepts, run the numbers, and answer embarrassing questions at midnight.

**Week 2 — Documents to upload:**
1. Personal budgeting guide (text or PDF)
2. Explanation of common financial products (text)
3. Sample spending categories and benchmarks (text)

**Week 3 — Agent actions:**
1. `calculate_savings_goal(target_amount, monthly_contribution, interest_rate)` — compound interest calculation
2. `categorize_transaction(description, amount)` — classify a bank transaction
3. `generate_budget_summary(income, expenses_by_category)` — produce a formatted summary

---

## Your Turn

None of these quite fit? Here are some other ideas to spark your thinking:

- Legal document explainer ("plain-English summary of my lease")
- Internal IT helpdesk
- Government services navigator
- Museum or cultural institution guide
- Non-profit donor FAQ

Whatever you choose, the code you write is identical — only the system prompt, the documents you upload, and the tool functions you define will change.

**Once you've decided, update `.env` and start Week 1.**
