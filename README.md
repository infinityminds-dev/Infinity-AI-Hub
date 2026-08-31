# 🧠 Infinity AI Hub - Self-Learning Conversational AI Engine

A lightweight Python AI engine built from scratch with an interactive **Flask Web Hub UI**, live self-learning, multi-query processing, dynamic math solving, and automated JSON memory management.

---

## 🚀 Core Features & Capabilities

* **🌐 Interactive Web Interface (`app.py`):** Modern Flask UI featuring live model switching between **v4.0 Neural** and **v3.6 Legacy**, real-time JSON memory selection, dynamic engine notices, and automated cleanup of empty memory files.

* **🧠 Live Interactive Training:** If the AI doesn't understand a query, it interactively asks for the correct response and updates its persistent memory instantly.

* **⚡ Auto-Fallback Engine:** Seamlessly detects local dependencies such as TensorFlow and safely falls back between **v4.0** and **v3.6** without freezing the session.

* **🧮 Dynamic Math Solver:** Instantly evaluates arithmetic expressions embedded directly within text queries.

* **🔀 Multi-Sentence Splitting:** Breaks down complex user inputs joined by commas or connectors and processes the queries sequentially.

* **🤝 Smart Memory Merging:** Safely merges training data from multiple JSON files into a master memory without data loss.

---

## 📁 Project Structure & Files

| File Name               | Purpose                  | Key Concept                                                                                          |
| :---------------------- | :----------------------- | :--------------------------------------------------------------------------------------------------- |
| **`app.py`**            | **Web Hub Server**       | Flask server powering the Web Hub UI, model switching, JSON memory selection, and automatic cleanup. |
| **`v3_6_AI_engine.py`** | **v3.6 Legacy Engine**   | Fast, lightweight rule-based engine with live training and arithmetic solving.                       |
| **`main_engine.py`**    | **v4.0 Neural Engine**   | TensorFlow-powered engine for advanced intent classification.                                        |
| **`merge_memory.py`**   | **Memory Merger**        | Safely merges multi-user JSON training files into a master memory file.                              |
| **`ai_memory_*.json`**  | **Persistent AI Memory** | JSON databases storing trained patterns, intents, and custom user responses.                         |

---

## 🛠️ How to Run & Use

### 1. ▶️ Start the Web Server

Open your terminal in the project directory and run:

```bash
python app.py
```

Then open your browser and navigate to:

**http://127.0.0.1:5000**

---

### 2. 🎛️ Features on the Web Hub

#### 🔄 Switch Models

Use the header dropdown to switch between:

* **v4.0 — Neural Engine**
* **v3.6 — Legacy Engine**

You can change the active engine directly from the Web Hub.

#### 🧠 Select Active Memory

Switch between available **`.json` memory files** instantly without restarting the server.

#### ➕ Create New JSON

Click **➕ New JSON** to create a fresh user memory/session.

The Web Hub automatically scans memory files and cleans up empty memory files when required.

---

### 3. 🧠 Live Training in Chat

Chat naturally with the AI.

If an input is unrecognized, the AI will ask:

> **"Mujhe iska matlab nahi pata... toh kya jawab doon?"**

Simply type the response you want the AI to learn.

The response is then saved permanently into the **currently active `.json` memory file**.

This allows the AI to continuously expand its knowledge through interaction.

---

### 4. 🧮 Dynamic Math Solver

The AI can detect arithmetic expressions directly inside normal text queries and calculate them automatically.

For example:

```text
What is 25 + 75?
```

The engine can process the mathematical expression and return the result without requiring a separate calculator mode.

---

### 5. 🔀 Multi-Sentence Processing

The engine can split complex inputs into multiple smaller queries.

This allows the AI to process several requests from a single user message instead of treating the entire message as one query.

Example:

```text
Hello, what is AI, how are you?
```

The engine can process the individual parts sequentially.

---

### 6. ⚡ Automatic Engine Fallback

Infinity AI Hub supports two engine versions:

```text
v4.0 Neural Engine
        │
        ▼
TensorFlow Available?
   ┌────┴────┐
  YES       NO
   │         │
   ▼         ▼
v4.0       v3.6
Neural    Legacy
```

If required local dependencies such as **TensorFlow** are unavailable, the system can safely fall back to the **v3.6 Legacy Engine**.

This helps keep the chat session running instead of failing because of a missing dependency.

---

### 7. 🔀 Merge Friend Memories

To combine training data from multiple JSON memory files, place the exported memory files in the project directory and run:

```bash
python merge_memory.py
```

The memory merger combines the training data into the master memory while protecting existing priority data.

---

## 🛠️ Typical Workflow

```text
Run app.py
    │
    ▼
Open http://127.0.0.1:5000 in Browser
    │
    ▼
Select Engine
(v4.0 Neural / v3.6 Legacy)
    │
    ▼
Select Active Memory File
    │
    ▼
Chat with AI
    │
    ├──► Math Query
    │       │
    │       └──► Instant Answer
    │
    ├──► Known Query
    │       │
    │       └──► AI Response
    │
    └──► Unknown Query
            │
            ▼
      AI asks for correct answer
            │
            ▼
      User provides response
            │
            ▼
      Response saved to memory
            │
            ▼
      AI learns from the new data

                │
                ▼

       Merge JSONs when needed
                │
                ▼
       python merge_memory.py
```

---

## 📦 Quick Start

### Step 1 — Start Infinity AI Hub

```bash
python app.py
```

### Step 2 — Open the Web Hub

```text
http://127.0.0.1:5000
```

### Step 3 — Choose Your Engine

```text
v4.0 Neural
     or
v3.6 Legacy
```

### Step 4 — Select Your Memory

Choose an existing `.json` memory file or create a new one.

### Step 5 — Start Chatting

Ask questions, solve math problems, and train the AI with new responses.

### Step 6 — Merge Memories

When you have training data from multiple users:

```bash
python merge_memory.py
```

---

## 🧠 Infinity AI Hub Architecture

```text
                    ┌─────────────────────┐
                    │    Infinity AI Hub  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      app.py         │
                    │    Flask Web Hub     │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐       ┌─────────────────┐
        │ v4.0 Neural     │       │ v3.6 Legacy     │
        │ main_engine.py  │       │ v3_6_AI_engine  │
        └────────┬────────┘       └────────┬────────┘
                 │                           │
                 └─────────────┬─────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ ai_memory_*.json    │
                    │ Persistent Memory    │
                    └──────────┬──────────┘
                               ▲
                               │
                    ┌──────────┴──────────┐
                    │ merge_memory.py     │
                    │ Memory Merger       │
                    └─────────────────────┘
```

---

## 🎯 Project Goal

**Infinity AI Hub** is designed as a lightweight, self-learning conversational AI system that can:

* 💬 Chat with users
* 🧠 Learn from new conversations
* 💾 Store knowledge in JSON memory
* 🔄 Switch between AI engine versions
* ⚡ Automatically fall back when dependencies are unavailable
* 🧮 Solve mathematical expressions
* 🔀 Process multiple queries
* 🤝 Merge knowledge from multiple users
* 🌐 Provide an easy-to-use Flask Web Hub

---

## 📌 Main Commands

Start the Web Hub:

```bash
python app.py
```

Merge AI memories:

```bash
python merge_memory.py
```

---

### ❤️ Built From Scratch

**Infinity AI Hub** is a lightweight AI project focused on experimentation, self-learning, persistent memory, and practical conversational AI development using Python.
