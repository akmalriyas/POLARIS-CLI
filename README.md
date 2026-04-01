# POLARIS-CLI

POLARIS-CLI is a high-performance, autonomous command-line interface agent designed for developers. Engineered for speed and precision, it leverages the Groq LPU™ Inference Engine to execute complex multi-step reasoning, filesystem operations, and terminal tasks with near-instant responsiveness.

---

<details>
<summary><b>Key Features</b></summary>

*   **Autonomous Reasoning:** Employs a ReAct (Reasoning and Action) loop to solve complex tasks using integrated tools.
*   **Intelligent Model Routing:** Automatically classifies tasks to utilize the most efficient model, ranging from lightweight 8B models to flagship 120B+ architectures.
*   **Native Vision Support:** Seamlessly processes local image files (PNG, JPG, WebP) using state-of-the-art multimodal vision models.
*   **Resilient API Client:** Features automatic key rotation and sophisticated error handling for high-availability performance.
*   **Secure Configuration:** Implements OS-native secure storage for API credentials with restricted file permissions.
*   **Premium Terminal UI:** Minimalist, branded interface featuring real-time status indicators and syntax-highlighted output.

</details>

---

## Installation

Install the package directly from source or via pip:

```bash
pip install polaris-cli
```

---

## Getting Started

### Initial Configuration
Upon first execution, POLARIS-CLI will launch an interactive wizard to configure your Groq API keys.

```bash
polaris-cli setup
```

### Basic Interaction
Enter an interactive multi-turn session to chat with the agent:

```bash
polaris-cli chat
```

Or execute a single one-off task:

```bash
polaris-cli "Write a python script that analyzes the current directory"
```

---

<details>
<summary><b>Available Commands</b></summary>

| Command | Description |
|:--- |:--- |
| `chat` | Enter the interactive, stateful multi-turn session. |
| `keys` | Manage and rotate your Groq API keys. |
| `setup` | Launch the first-run configuration wizard. |
| `reset` | Securely clear all local configuration and cached keys. |
| `help` | Display the branded help interface and usage guide. |

</details>

---

<details>
<summary><b>Autonomous Toolset</b></summary>

POLARIS-CLI provides the agent with a suite of low-level system capabilities:

*   **Filesystem:** `read_file`, `write_file`, and `ls_dir` for direct file manipulation.
*   **System:** `run_cmd` for terminal execution and `sys_get_info` for environment awareness.
*   **Search:** `search_code` for fast, recursive grep-style regex searching across the codebase.

</details>

---

<details>
<summary><b>Intelligent Model Routing</b></summary>

The agent dynamically routes tasks to specialized models based on complexity and intent:

*   **Flagship Logic:** `openai/gpt-oss-120b` (System Architecture)
*   **Deep Reasoning:** `qwen/qwen3-32b` (Complex Coding & Math)
*   **Heavy Generation:** `llama-3.3-70b-versatile` (Long-form content)
*   **Native Vision:** `meta-llama/llama-4-scout-17b-16e-instruct` (Multimodal analysis)
*   **Light Execution:** `llama-3.1-8b-instant` (Greetings & Terminal commands)

</details>

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

Created with ❤️ by [akmalriyas](https://github.com/akmalriyas)
