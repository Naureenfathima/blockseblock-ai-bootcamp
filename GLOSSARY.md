# Glossary

**AI Engineering Bootcamp · BlockseBlock**

Plain-English definitions for every technical term used in this course. Each entry includes an analogy to help the idea stick. Terms are listed alphabetically.

---

## Agent

An AI setup where the model doesn't just answer a single question — it decides what to do next, takes an action, looks at the result, and then decides what to do after that. The model keeps going until the task is done or it gets stuck.

**Analogy:** A travel agent who doesn't just tell you flight options — they actually book the ticket, arrange the hotel, and email you the itinerary, all without you lifting a finger after the first request.

---

## API (Application Programming Interface)

A defined way for two pieces of software to talk to each other. One program makes a "request" (asking for something), and the other sends back a "response" (the answer). APIs let you use someone else's service — like an LLM — from inside your own application.

**Analogy:** A restaurant menu is an API. You don't go into the kitchen and cook — you place an order (request) using the menu's defined options, and the kitchen sends out a plate (response).

---

## Chunking

The process of splitting a large document into smaller, overlapping pieces before storing it in a vector database. Models can only process so much text at once (see *Context Window*), so we cut documents into bite-sized pieces that can each fit.

**Analogy:** When you prepare index cards for studying, you don't copy the whole textbook onto one card — you write one idea per card so you can find the right one quickly. Chunking is making those cards.

---

## Context Window

The maximum amount of text (measured in *tokens*) that a model can see and reason about in a single interaction. Text outside the window is invisible to the model — it simply doesn't exist from the model's perspective.

**Analogy:** Imagine you can only read one page of a book at a time, with a piece of paper blocking everything else. Whatever's on that page is your context. If you want the model to know something, it has to be on that page.

---

## Deployment

The process of making your application available to other people, usually by putting it on a server on the internet. A deployed app runs 24/7 without your laptop needing to be open.

**Analogy:** Writing a recipe is development. Cooking it at home and letting your family taste it is testing. Opening a restaurant so strangers can order it is deployment.

---

## Docker

A tool that packages your application and all its dependencies into a self-contained "container" — a lightweight virtual box. Anyone with Docker installed can run your container and get the exact same environment you developed in, regardless of their operating system.

**Analogy:** A shipping container. You load everything your app needs inside it (code, libraries, settings), seal it up, and ship it. Whoever receives it can unpack and run it without worrying about what tools they have installed.

---

## Embedding

A way of converting text (a word, sentence, or whole paragraph) into a list of numbers that captures its meaning. Text with similar meanings will have numbers that are close together, which lets a computer find related content mathematically.

**Analogy:** Imagine plotting cities on a map. London and Paris are close together (geographically similar); London and Tokyo are far apart. Embeddings do the same thing for meaning — "happy" and "joyful" end up near each other; "happy" and "invoice" end up far apart.

---

## Endpoint

A specific URL in your API that performs a specific action. Each endpoint does one thing: `/chat` handles chat messages, `/documents/upload` accepts file uploads, `/health` checks if the server is alive.

**Analogy:** Each department in a company has its own phone extension. The main number is the API; each extension (endpoint) connects you to a different function: sales, support, billing.

---

## Health Check

A simple endpoint (usually `GET /health`) that returns "I'm alive and working" when the server is healthy. Monitoring systems ping this endpoint regularly to detect outages automatically.

**Analogy:** The "are you there?" message you send a friend when you haven't heard from them. If they reply, great. If not, something's wrong and you need to investigate.

---

## JSON (JavaScript Object Notation)

A text format for representing structured data using curly braces `{}`, square brackets `[]`, colons `:`, and commas `,`. It's the most common format for sending data between web applications and APIs.

**Analogy:** A form you fill out. Fields have names ("First Name:") and values ("Naureen"). JSON is just that form, written in a format computers can read: `{"first_name": "Naureen"}`.

---

## LLM (Large Language Model)

A type of AI model trained on enormous amounts of text that can understand and generate human language. It works by predicting the most likely next word (or token) given everything that came before — billions of times, very fast.

**Analogy:** An incredibly well-read person who has absorbed most of the text ever written and can continue any conversation, write any style, and answer most questions — but who sometimes confidently says things that aren't true, so you should always verify important facts.

---

## MCP (Model Context Protocol)

A standard way for AI models to connect to external tools, data sources, and services. Instead of building a custom integration for every tool, MCP provides a shared "plug" that any compatible tool can use to connect to any compatible model.

**Analogy:** The USB standard. Before USB, every device had its own unique plug. USB created one standard connector that works for keyboards, mice, cameras, and phones. MCP is USB for AI tools.

---

## NFR (Non-Functional Requirement)

A requirement about *how* the system should behave rather than *what* it should do. Examples: "must respond in under 2 seconds", "must handle 1,000 users simultaneously", "must be available 99.9% of the time". These are easy to forget and expensive to add later.

**Analogy:** When you hire a restaurant chef, the job description (cook meals) is the functional requirement. The NFRs are: must wear a hairnet, must wash hands, must not take more than 20 minutes per table. They don't define *what* they cook — they define the *quality standards* around the cooking.

---

## Local Model

An AI model that runs entirely on your own computer rather than on a remote server. Local models require no API key and send no data over the internet, which is great for privacy. The trade-off is that they need significant computing resources (RAM, GPU) and are generally less capable than the largest hosted models.

**Analogy:** A cookbook on your shelf vs. calling a professional chef. The cookbook (local model) is always available, free, and private — but the chef (hosted model) can handle more complex recipes.

---

## Provider

In this course, "provider" means the company or service whose AI models you're calling: for example, OpenAI, Anthropic, Cohere, or a model running locally via Ollama. The course is designed to be provider-agnostic — you configure your provider in `.env` and all feature code works unchanged regardless of which one you pick.

**Analogy:** A cloud provider for electricity. Whether you're on one utility company or another, your appliances (code) work the same way — you just plug into a different socket (provider) by changing a setting.

---

## RAG (Retrieval-Augmented Generation)

A technique where, before the model generates an answer, the system first searches a database for relevant documents and includes them in the prompt. This grounds the model's answer in real, specific information rather than just its training data.

**Analogy:** Open-book exam vs. closed-book exam. A closed-book LLM answers purely from memory. RAG lets the model take the exam with the textbook open — it searches for the relevant pages first, then writes the answer using what it found.

---

## Rate Limiting

A protection mechanism that caps how many requests a user (or your app) can make to an API within a time window. This prevents overuse, abuse, and runaway costs.

**Analogy:** An all-you-can-eat buffet with a rule: you can visit the food stations up to 3 times per 10 minutes. The restaurant still feeds you generously — it just prevents one person from monopolising the food.

---

## Session

A period of interaction between a user and the app that is tracked as a continuous conversation. A session has a start (first message) and an end (user closes the window, or the session times out). Session data lets the model remember earlier messages.

**Analogy:** A phone call. Everything said during the call is part of the same session. When you hang up and call back later, the assistant doesn't automatically remember the previous call unless you remind them.

---

## STT (Speech-to-Text)

Technology that converts spoken audio into written text. The user speaks into a microphone; STT turns the audio waveform into a string of words the AI can process.

**Analogy:** A court stenographer who transcribes everything spoken aloud into a written record. You speak; they type exactly what you said.

---

## System Prompt

A special instruction given to the model at the start of every conversation that sets its persona, rules, and purpose. Users don't see the system prompt — it shapes how the model behaves without the user having to repeat instructions every time.

**Analogy:** An employee handbook given to a new hire on their first day. It tells them who the company is, what they're allowed to say, how to handle complaints, and what tone to use. The customer never reads the handbook, but it shapes every interaction they have with that employee.

---

## Temperature

A setting that controls how creative (unpredictable) or focused (predictable) the model's responses are. A temperature of 0 means the model nearly always picks the most likely next word. Higher temperatures increase variety and surprise.

**Analogy:** A dimmer switch for creativity. Turn it down (temperature 0) and you get the same, safe, reliable output every time — like a chef who only makes the house special. Turn it up and the chef starts improvising, which can be brilliant or occasionally weird.

---

## Token

The basic unit the model reads and writes. A token is roughly ¾ of a word — "hamburger" might be two tokens ("ham" + "burger"), and a short sentence might be 10–20 tokens. Token counts matter because they determine both the cost of an API call and how much the model can read at once.

**Analogy:** A taxi meter that charges per 0.1 km, not per km. "Km" is a word, but the taxi charges for the smaller unit. Tokens are the taxi's charging unit for language.

---

## Tool Calling

A capability that lets the model "call" functions defined in your code, similar to how a human assistant might say "let me look that up" and go do a web search. The model decides when a tool is needed, formats the call, and the result comes back for the model to use in its reply.

**Analogy:** Giving a research assistant a list of reference books and saying "you may use these". When they don't know something, they pull the right book, find the answer, and incorporate it. You define which books (tools) exist; the assistant decides when to use them.

---

## TTS (Text-to-Speech)

Technology that converts written text into spoken audio. The app sends a string of text; TTS turns it into a human-sounding voice recording that plays in the browser.

**Analogy:** An audiobook narrator who reads any text you give them aloud. You provide the script; they provide the voice.

---

## Vector Database

A specialised database designed to store and search *embeddings* (see *Embedding*). Instead of searching by exact keyword match, a vector database finds items by semantic similarity — it can find documents that *mean* the same thing as your query, even if they use different words.

**Analogy:** A library where books are arranged by topic rather than title. You don't need to know the exact book name — you describe what you're looking for ("something about managing grief") and the librarian points you to the relevant shelf. The arrangement is by meaning, not alphabet.
