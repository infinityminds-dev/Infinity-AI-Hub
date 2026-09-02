🧠 Infinity AI Hub — Self-Learning Conversational AI Engine

""License: MIT" (https://img.shields.io/badge/License-MIT-yellow.svg)" (LICENSE)

Infinity AI Hub is a lightweight Python AI engine built from scratch with an interactive Flask Web Hub UI, live self-learning, multi-query processing, dynamic math solving, automatic engine fallback, and JSON-based persistent memory management.

---

🚀 Core Features & Capabilities

🌐 Interactive Web Interface

"app.py" provides a modern Flask-based Web Hub featuring:

- 🔄 Live model switching between v7.0 Neural and v5.6 Legacy
- 🧠 Real-time JSON memory selection
- 📢 Dynamic engine status notices
- 🧹 Automatic cleanup of empty memory files
- 💬 Browser-based AI chat interface

🧠 Live Interactive Training

When the AI does not understand a query, it can interactively ask the user for the correct response.

Example:

«AI: Mujhe iska matlab nahi pata... toh kya jawab doon?»

The user can provide the desired response, which is then stored in the active JSON memory.

This allows the AI to continuously expand its knowledge through conversations.

⚡ Automatic Engine Fallback

Infinity AI Hub supports automatic fallback between its AI engines.

If required local dependencies such as TensorFlow are unavailable, the system can safely fall back from:

v7.0 Neural → v5.6 Legacy

This helps keep the chat session running instead of failing because of a missing dependency.

🧮 Dynamic Math Solver

The engine can detect arithmetic expressions directly inside normal text queries and calculate them automatically.

Example:

What is 25 + 75?

The engine can detect the mathematical expression and return:

100

🔀 Multi-Sentence / Multi-Query Processing

Complex user messages can be split into smaller queries and processed sequentially.

Example:

Hello, what is AI, how are you?

The engine can process the individual parts instead of treating the entire message as one large query.

🤝 Smart Memory Merging

Training data from multiple JSON memory files can be safely combined into a master memory.

The merger is designed to protect existing priority data while adding new training information.

---

📁 Project Structure

File / Pattern| Purpose| Key Concept
"app.py"| Web Hub Server| Flask server powering the Web Hub UI, model switching, JSON memory selection, and automatic cleanup
"v5_6_AI_engine.py"| v5.6 Legacy Engine| Fast, lightweight rule-based engine with live training and arithmetic solving
"main_engine.py"| v7.0 Neural Engine| TensorFlow-powered engine for advanced intent classification
"merge_memory.py"| Memory Merger| Safely merges multi-user JSON training files into a master memory
"requirements.txt"| Python Dependencies| Lists external Python packages required by Infinity AI Hub
"ai_memory_*.json"| Persistent AI Memory| JSON databases storing trained patterns, intents, and custom user responses
"LICENSE"| Project License| MIT License information

---

🛠️ How to Run & Use

1. ▶️ Start the Web Server

Open a terminal inside the project directory:

python app.py

Then open your browser and navigate to:

http://127.0.0.1:5000

---

2. 🎛️ Features on the Web Hub

🔄 Switch Models

Use the Web Hub header dropdown to switch between:

v7.0 — Neural Engine
v5.6 — Legacy Engine

You can change the active engine directly from the Web Hub.

---

🧠 Select Active Memory

The Web Hub can detect available ".json" memory files.

You can switch between available memory files without restarting the server.

---

➕ Create New JSON Memory

Use the ➕ New JSON option to create a fresh user memory/session.

The Web Hub automatically scans memory files and can clean up empty memory files when required.

---

3. 🧠 Live Training in Chat

Chat naturally with the AI.

If an input is not recognized, the AI can ask:

Mujhe iska matlab nahi pata... toh kya jawab doon?

Simply type the response you want the AI to learn.

The response is then saved into the currently active ".json" memory file.

Learning Flow

User Query
    │
    ▼
AI Understands?
 ┌──┴──┐
YES    NO
 │      │
 ▼      ▼
Reply   Ask User
          │
          ▼
    User Provides Answer
          │
          ▼
     Save to Memory
          │
          ▼
        Learn

---

4. 🧮 Dynamic Math Solver

Infinity AI Hub can detect arithmetic expressions directly inside normal text queries.

Example:

What is 25 + 75?

The engine extracts and evaluates the mathematical expression without requiring a separate calculator mode.

Example

Input:
What is 125 * 8?

Output:
1000

---

5. 🔀 Multi-Sentence Processing

The engine can split complex inputs into multiple smaller queries.

This allows several requests to be processed from a single user message.

Example

Hello, what is AI, how are you?

The engine can process the message as multiple logical queries:

Hello
What is AI
How are you

Each part can then be processed sequentially.

---

6. ⚡ Automatic Engine Fallback

Infinity AI Hub supports two engine versions:

- v7.0 Neural Engine
- v5.6 Legacy Engine

Fallback Logic

        v7.0 Neural Engine
                 │
                 ▼
       TensorFlow Available?
            ┌────┴────┐
           YES        NO
            │          │
            ▼          ▼
          v7.0       v5.6
         Neural      Legacy

If required local dependencies such as TensorFlow are unavailable, the system can safely use the v5.6 Legacy Engine.

This provides a fallback path instead of terminating the chat session because of a missing dependency.

---

7. 🔀 Merge Friend Memories

Training data from multiple users can be combined into a master memory.

Place the exported JSON memory files inside the project directory and run:

python merge_memory.py

The memory merger combines the training data while protecting existing priority data.

Memory Merge Flow

User Memory 1 ──┐
                │
User Memory 2 ──┼──► merge_memory.py ──► Master Memory
                │
User Memory 3 ──┘

---

🛠️ Typical Workflow

Run app.py
    │
    ▼
Open http://127.0.0.1:5000
    │
    ▼
Select Engine
(v7.0 Neural / v5.6 Legacy)
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
      AI learns from new data
            │
            ▼
       Merge JSONs when needed
            │
            ▼
   python merge_memory.py

---

📦 Quick Start

Step 1 — Install Dependencies

Install the required Python packages:

pip install -r requirements.txt

---

Step 2 — Start Infinity AI Hub

python app.py

---

Step 3 — Open the Web Hub

Open:

http://127.0.0.1:5000

---

Step 4 — Choose Your Engine

Choose between:

v7.0 Neural

or:

v5.6 Legacy

---

Step 5 — Select Your Memory

Choose an existing ".json" memory file or create a new one.

---

Step 6 — Start Chatting

Ask questions, solve mathematical problems, and train the AI with new responses.

---

Step 7 — Merge Memories

When you have training data from multiple users:

python merge_memory.py

---

🧠 Infinity AI Hub Architecture

                    ┌─────────────────────┐
                    │   Infinity AI Hub   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       app.py        │
                    │    Flask Web Hub    │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐       ┌─────────────────┐
        │  v7.0 Neural    │       │  v5.6 Legacy    │
        │  main_engine.py │       │v5_6_AI_engine.py │
        └────────┬────────┘       └────────┬────────┘
                 │                           │
                 └─────────────┬─────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   ai_memory_*.json  │
                    │  Persistent Memory  │
                    └──────────┬──────────┘
                               ▲
                               │
                    ┌──────────┴──────────┐
                    │   merge_memory.py   │
                    │    Memory Merger    │
                    └─────────────────────┘

---

🎯 Project Goal

Infinity AI Hub is designed as a lightweight, self-learning conversational AI system that can:

- 💬 Chat with users
- 🧠 Learn from new conversations
- 💾 Store knowledge in JSON memory
- 🔄 Switch between AI engine versions
- ⚡ Automatically fall back when dependencies are unavailable
- 🧮 Solve mathematical expressions
- 🔀 Process multiple queries
- 🤝 Merge knowledge from multiple users
- 🌐 Provide an easy-to-use Flask Web Hub

---

📌 Main Commands

Start the Web Hub

python app.py

Merge AI Memories

python merge_memory.py

Install Dependencies

pip install -r requirements.txt

---

🔧 Engine Versions

Engine| Version| File| Description
🧠 Neural Engine| v7.0| "main_engine.py"| TensorFlow-powered advanced intent classification
⚡ Legacy Engine| v5.6| "v5_6_AI_engine.py"| Lightweight rule-based conversational engine

«Note: v5.6 acts as the lightweight fallback engine when the v7.0 environment cannot use its required dependencies.»

---

💾 Memory System

Infinity AI Hub uses JSON files for persistent conversational memory.

Example:

ai_memory_user1.json
ai_memory_user2.json
ai_memory_friend.json

These files can contain trained patterns, intents, and custom responses.

Multiple memory files can later be merged using:

python merge_memory.py

---

🔐 Lightweight & Local

Infinity AI Hub is designed around a lightweight local architecture.

The project focuses on:

- 🐍 Python
- 🌐 Flask
- 🧠 Local AI engines
- 💾 JSON-based memory
- 🔄 Modular engine switching
- ⚡ Dependency-aware fallback

---

❤️ Built From Scratch

Infinity AI Hub is a lightweight AI project focused on experimentation, self-learning, persistent memory, and conversational AI development.

Built from scratch with the goal of creating an AI system that can learn, remember, and improve through interaction.

---

📜 License

Infinity AI Hub is licensed under the MIT License.

See the ""LICENSE"" (LICENSE) file for the full license text.

---

⭐ Project

If you find Infinity AI Hub interesting, consider giving the repository a ⭐ on GitHub.

Infinity AI Hub — Learn. Remember. Evolve. 🧠♾️
