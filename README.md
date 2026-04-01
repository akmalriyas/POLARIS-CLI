# 🌌 POLARIS-CLI

**POLARIS-CLI** is a high-performance, autonomous CLI-based LLM agent designed for developers who need speed and precision. Built on top of the **Groq API**, it leverages ultra-fast inference to execute multi-step tool calls, manage local files, and run terminal commands with near-instant responsiveness.

---

## ✨ Features

- ⚡ **Ultra-Fast Multi-Step Execution:** Powered by Groq's LPU™ Inference Engine.
- 🛡️ **Resilient API Management:** Automatic key rotation and failover for 429 (Rate Limit) and 401 (Unauthorized) errors.
- 🧠 **Autonomous Model Router:** Intelligent task classification to route requests between Heavy (70B+), Vision, and Light (8B) models.
- 🛠️ **Built-in Agentic Tools:**
    - `read_file` / `list_directory`
    - `search_codebase` (Fast grep-style search)
    - `run_terminal_command`
    - `get_system_info`
- 🎨 **Premium Terminal UI:** Beautifully crafted interface using `rich` with ASCII art, status indicators, and syntax-highlighted Markdown.
- 🔒 **Secure Configuration:** Local API key storage with restricted file permissions.

---

## 🚀 Installation

Install via pip:

```bash
pip install polaris-cli
```

---

## 🛠️ Getting Started

### 1. First-Run Setup
On your first run, POLARIS-CLI will guide you through an interactive setup to add your Groq API keys.

```bash
polaris-cli
```

### 2. Managing API Keys
You can add more keys later to increase your rate limit headroom:

```bash
polaris-cli --add-key
```

### 3. Basic Usage
Ask a question or give a command:

```bash
polaris-cli "Analyze the performance of my current project"
```

---

## 🧠 Model Routing Logic

POLARIS-CLI automatically selects the best model for the job:

- **Flagship:** `openai/gpt-oss-120b` for maximum reasoning and complex architecture.
- **Reasoning:** `qwen-qwq-32b` or `deepseek-r1-distill-llama-70b` for intense logic/math.
- **Heavy:** `llama-3.3-70b-versatile` for high-end generation.
- **Smart:** `groq/compound` for autonomous multi-step tool use.
- **Vision:** `meta-llama/llama-4-scout-17b-16e-instruct` for state-of-the-art visual context.
- **Versatile:** `openai/gpt-oss-20b` or `mixtral-8x7b-32768` for standard coding and writing.
- **Light:** `llama-3.1-8b-instant` for routing and simple tasks.

---

## ⚖️ License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

**Made with ❤️ by [akmalriyas](https://github.com/akmalriyas)**
