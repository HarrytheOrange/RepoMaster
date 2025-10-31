## RepoMaster Prompt Inventory and Agent Flows

This document summarizes all prompts defined in the repository and explains how they are used across the main agent flows.

### Contents
- Overview of main flows
- Prompt inventory by file
- How prompts are used in each flow
- Quick references to source locations

## Main Flows

### Code Explorer Flow
- Agents:
  - Code_Explorer (assistant): driven by `SYSTEM_EXPLORER_PROMPT`.
  - Coder_Excuter (user-proxy/executor): executes code/view ops, then returns results.
- Entry messages:
  - For repository analysis: `USER_EXPLORER_PROMPT` (task + work_dir + repo + important modules summary).
  - For general coding help in this flow: `CODE_ASSISTANT_PROMPT` (task + work_dir).
- Special instructions for Kaggle-like training tasks: `TRAIN_PROMPT` appended as additional instructions.
- Termination: content ends with `TERMINATE` or `<TERMINATE>`; token-limit guard can also stop.

- 中文说明：
  - 参与 Agent：
    - Code_Explorer（助理）：由 `SYSTEM_EXPLORER_PROMPT` 驱动。
    - Coder_Excuter（用户代理/执行器）：负责执行代码/查看操作，并将结果返回。
  - 入口消息：
    - 仓库分析：`USER_EXPLORER_PROMPT`（任务 + 工作目录 + 仓库路径 + 重要模块摘要）。
    - 通用编码：`CODE_ASSISTANT_PROMPT`（任务 + 工作目录）。
  - Kaggle 类训练任务：将 `TRAIN_PROMPT` 作为附加说明拼接在系统提示后。
  - 结束条件：内容以 `TERMINATE` 或 `<TERMINATE>` 结尾；也可能受令牌上限保护而停止。

### Deep Search Flow
- Agents:
  - researcher (assistant): `DEEP_SEARCH_SYSTEM_PROMPT` (planning, horizontal-first browsing, iterative reflection, misalignment checks, finish with <TERMINATE>).
  - executor (user-proxy): `EXECUTOR_SYSTEM_PROMPT` (executes search/browse; terminates only when researcher declares final answer).
- Auxiliary prompts:
  - `DEEP_SEARCH_CONTEXT_SUMMARY_PROMPT`: compress tool responses into essential facts.
  - `DEEP_SEARCH_RESULT_REPORT_PROMPT`: generate final comprehensive answer.

- 中文说明：
  - 参与 Agent：
    - researcher（研究员，助理）：`DEEP_SEARCH_SYSTEM_PROMPT`（规划、先横后纵浏览、迭代反思、错位校验，最终以 `<TERMINATE>` 结束）。
    - executor（执行者，用户代理）：`EXECUTOR_SYSTEM_PROMPT`（按研究员要求检索/浏览；仅当研究员宣布完成时终止）。
  - 辅助提示：
    - `DEEP_SEARCH_CONTEXT_SUMMARY_PROMPT`：将工具返回压缩为要点。
    - `DEEP_SEARCH_RESULT_REPORT_PROMPT`：生成最终综合回答。

### Agent Scheduler Flow (Enhanced RepoMaster)
- Agents:
  - scheduler_agent: `scheduler_system_message` (mode selection + tool orchestration).
  - user_proxy: `user_proxy_system_message` (returns tool outputs; does not answer user directly).
- Modes:
  - Web Search Mode → deep search agents.
  - Repository Mode → `run_repository_agent` (may invoke Code Explorer).
  - General Code Assistant Mode → `run_general_code_assistant` (General Coder).
- Repo searching strategy: first search repos, then run the best, evaluate, iterate.
- Termination: respond with `TERMINATE` when done.

- 中文说明：
  - 参与 Agent：
    - scheduler_agent（调度）：`scheduler_system_message`（模式选择与工具编排）。
    - user_proxy（执行代理）：`user_proxy_system_message`（仅返回工具输出，不直接面向用户）。
  - 模式：
    - Web 搜索模式 → 触发深度搜索代理。
    - 仓库模式 → 调用 `run_repository_agent`（可能进一步调用 Code Explorer）。
    - 通用编码模式 → 调用 `run_general_code_assistant`（General Coder）。
  - 仓库检索策略：先搜仓库，再运行最优候选，评估后迭代。
  - 结束条件：完成后输出 `TERMINATE`。

### General Coder Flow
- Agents:
  - General_Coder (assistant): `Coder_Prompt` (or Update variants) as system prompt.
  - Coder_Excute (user-proxy): executes generated code; summarizes created files if needed.
- Behavior: step-by-step, install dependencies, full executable scripts, error handling, retry with fixes, finish with `TERMINATE`.

- 中文说明：
  - 参与 Agent：
    - General_Coder（助理）：以 `Coder_Prompt`（或 Update 变体）作为系统提示。
    - Coder_Excute（用户代理）：执行生成的代码；必要时汇总创建的文件。
  - 行为规范：分步执行、安装依赖、输出完整可运行脚本、错误处理与重试修复、完成后以 `TERMINATE` 结束。

### Code Block Judge Pipeline
- Purpose: when assistant outputs multiple code blocks, use LLM to decide executability, intent, target file, deduplicate, and order.
- Prompts:
  - `_build_system_prompt` and `_build_user_prompt` in codeblock judge.
- Used by: extended user proxy code execution path to filter/sort blocks before execution.

- 中文说明：
  - 目的：当回复包含多个代码块时，使用 LLM 判定可执行性、意图、目标文件，去重并排序。
  - 提示：
    - `_build_system_prompt` 与 `_build_user_prompt` 位于代码块判定模块。
  - 使用位置：扩展的用户代理执行路径在执行前对代码块进行筛选与排序。

### Web Search Micro‑Prompts
- `SYSTEM_MESSAGE_HAS_SUFFICIENT_INFO`: decide if search results suffice (Yes/No only).
- `SYSTEM_MESSAGE_GENERATE_ANSWER`: produce final answer based on provided results.
- `SYSTEM_MESSAGE_IMPROVE_QUERY`: Think-on-Graph method to improve a query; output only the improved query.

- 中文说明：
  - `SYSTEM_MESSAGE_HAS_SUFFICIENT_INFO`：判断检索结果是否足够（仅回答 Yes/No）。
  - `SYSTEM_MESSAGE_GENERATE_ANSWER`：基于结果直接生成最终回答。
  - `SYSTEM_MESSAGE_IMPROVE_QUERY`：使用 ToG 方法改写并输出仅包含改进后的查询。

## Prompt Inventory by File

### src/core/prompt.py
- `USER_EXPLORER_PROMPT`
  - Purpose: First user message for repository analysis; injects task, work_dir, repo path, important modules.
  - Used by: Code Explorer as initial message (repo mode).
- `CODE_ASSISTANT_PROMPT`
  - Purpose: First user message for general coding assistance in explorer flow; injects task and work_dir.
  - Used by: Code Explorer when `task_type == "general"`.
- `SYSTEM_EXPLORER_PROMPT`
  - Purpose: System prompt for Code_Explorer. Enforces absolute paths, tool-first, step-by-step plan, full scripts, error handling, PyTorch-first, `<TERMINATE>` usage.
  - Used by: Code Explorer (assistant system_message).
- `TRAIN_PROMPT`
  - Purpose: Strict rules for model training/inference (GPU, early stopping, checkpoints, single-file guidance, result file checks) with example snippets.
  - Used by: Code Explorer when `task_type == 'kaggle'` (as additional instructions).

### src/services/prompts/deepsearch_prompt.py
- `DEEP_SEARCH_SYSTEM_PROMPT`
  - Purpose: Researcher’s system prompt; emphasizes stepwise planning, horizontal-first browsing, misalignment checks, iterative reflection; finish with `<TERMINATE>`.
  - Used by: DeepSearchAgent researcher.
- `EXECUTOR_SYSTEM_PROMPT`
  - Purpose: Executor’s system prompt; runs searches/browses per researcher’s request; terminates only when researcher signals finalization.
  - Used by: DeepSearchAgent executor.
- `DEEP_SEARCH_CONTEXT_SUMMARY_PROMPT`
  - Purpose: Summarize tool responses into concise facts.
  - Used by: DeepSearchAgent to compress long tool outputs.
- `DEEP_SEARCH_RESULT_REPORT_PROMPT`
  - Purpose: Create final comprehensive answer from entire trajectory.
  - Used by: DeepSearchAgent summary step.

### src/services/prompts/general_coder_prompt.py
- `Coder_Prompt`
  - Purpose: General coding assistant system prompt; when to generate code/shell, absolute execution, error correction loops, `TERMINATE`.
  - Used by: General Coder assistant.
- `Coder_Prompt_Update` / `Coder_Prompt_Update_en` / `Coder_Prompt_Update_zh`
  - Purpose: Stronger structure/robustness requirements; `_zh` emphasizes separate shell install then Python code.
  - Potentially used as alternative system prompts for stricter workflows.
- `Code_Planning_Prompt`
  - Purpose: Produce structured execution plans (goals, steps, dependencies, risks, resources, metrics).
  - Used where plan-only generation is required.

### src/services/prompts/optimized_task_execution.py
- `Optimized_Task_Execution_Prompt`
  - Purpose: Rewrite dialogue and execution trajectory into an optimal path; keep only final corrected code; provide task summary.
  - Used by: Optimization utilities for summarizing trajectories.
- `Optimiz_Dialogue_History_Prompt`
  - Purpose: Compress dialogue history while preserving roles and tool calls; output simplified array format.
  - Used by: Dialogue optimization utilities.

### src/utils/web_search_agent/prompt_web_search.py
- `SYSTEM_MESSAGE_HAS_SUFFICIENT_INFO`
- `SYSTEM_MESSAGE_GENERATE_ANSWER`
- `SYSTEM_MESSAGE_IMPROVE_QUERY`
  - Purpose: Micro-prompts for web search sufficiency checks, answer generation, and query improvement.
  - Used by: Web search agents/tools.

### src/services/autogen_upgrade/codeblock_judge.py
- `_build_system_prompt` / `_build_user_prompt`
  - Purpose: Ask LLM to determine code block executability, intent, deduplication, and ordering; output JSON plan.
  - Used by: Extended user proxy’s code execution path to pre-process code blocks.

### src/core/agent_scheduler.py
- `scheduler_system_message`
  - Purpose: Mode selection logic (Web Search / Repository / General Coder), repo-first search→run strategy, de-dup/termination policies.
  - Used by: RepoMaster scheduler agent.
- `user_proxy_system_message`
  - Purpose: Execution proxy rules—no user-facing answers, summarize tool outputs to scheduler, termination policy.
  - Used by: RepoMaster user proxy agent.

### src/core/git_task.py
- `TaskManager.get_task_prompt`
  - Purpose: Task card template (task description, absolute repo path, input data list, output directory, core objective).
  - Used by: Repo task orchestration when running repository-based tasks.

## How Prompts Drive Flows (Source Pointers)

- Code Explorer wiring and usage:
  - `src/core/agent_code_explore.py` constructs the agents, injects `SYSTEM_EXPLORER_PROMPT` for Code_Explorer, chooses initial message between `USER_EXPLORER_PROMPT` and `CODE_ASSISTANT_PROMPT`, and appends `TRAIN_PROMPT` for Kaggle tasks. It also defines the `Coder_Excuter` system message for execution rules.

- Deep Search wiring and usage:
  - `src/services/agents/deep_search_agent.py` builds researcher/executor agents with `DEEP_SEARCH_SYSTEM_PROMPT` and `EXECUTOR_SYSTEM_PROMPT`, summarizes long tool responses using `DEEP_SEARCH_CONTEXT_SUMMARY_PROMPT`, and produces final report with `DEEP_SEARCH_RESULT_REPORT_PROMPT`.

- Scheduler wiring and usage:
  - `src/core/agent_scheduler.py` builds `scheduler_agent` and `user_proxy`, registers tools for web search, repo-run, general coder, and repo searching; selects modes per the scheduler prompt.

- General Coder wiring and usage:
  - `src/services/agents/agent_general_coder.py` sets the assistant system message to `Coder_Prompt`, runs code execution through an extended user proxy, and summarizes generated files.

- Code Block Judge path:
  - `src/services/autogen_upgrade/base_agent.py` integrates code block extraction; `src/services/autogen_upgrade/codeblock_judge.py` prompts the LLM to keep/sort blocks; results feed into executor.

- Web Search prompts:
  - `src/utils/web_search_agent/prompt_web_search.py` supports sufficiency decision, answer synthesis, and query improvement.

## Notes
- Many prompts embed placeholders like `{current_time}`, `{task}`, `{work_dir}`, `{remote_repo_path}` and are formatted at runtime.
- Flows consistently enforce: full executable scripts, no partial code, robust error handling, and explicit termination tokens.

## 全量 Prompt 原文与中文翻译（含详细说明）

说明：以下每一条均包含三部分——名称与位置、原文、中文翻译与详细说明（用途、触发时机、适用 Agent/流程、关键约束与注意事项）。

### 1) USER_EXPLORER_PROMPT（src/core/prompt.py）

原文：
```
I need you to analyze the provided code repository and use your powerful capabilities to complete the user's task.:

**Task Description**:
<task>
{task}
</task>

**Working Directory (code execution directory)**:
<work_dir>
{work_dir}
</work_dir>

**Repository Address**:
<repo>
{remote_repo_path}
</repo>

**Important Repository Components**:
<code_importance>
{code_importance}
</code_importance>
```

中文翻译与说明：
- 作用：代码仓库分析流程的首条用户消息模板，携带任务描述、工作目录、仓库地址与关键模块提示，帮助 Agent 定位重点。
- 触发：`CodeExplorer.analyze_code` 在仓库模式（非 general）时注入。
- 变量：`{task}` `{work_dir}` `{remote_repo_path}` `{code_importance}`。

### 2) CODE_ASSISTANT_PROMPT（src/core/prompt.py）

原文：
```
I need you to analyze the provided code repository and use your powerful capabilities to complete the user's task.:

**Task Description**:
<task>
{task}
</task>

**Working Directory (code execution directory)**:
<work_dir>
{work_dir}
</work_dir>
```

中文翻译与说明：
- 作用：代码探索流中的“通用编码”入口提示，提供任务与工作目录，不包含仓库路径与重要组件摘要。
- 触发：`CodeExplorer.analyze_code` 在 `task_type == "general"` 时注入。

### 3) SYSTEM_EXPLORER_PROMPT（src/core/prompt.py）

原文（节选，完整见源码）：
```
You are a top-tier code expert, focused on quickly understanding and analyzing code repositories, and generating and executing corresponding code to efficiently complete specific tasks.
...
**Absolute Path Requirements**: When processing files and directories, you must use absolute paths...
...
## Workflow and Standards
1. **Understand Task** ...
2. **Plan Formulation** ...
3. **Codebase Analysis** ...
4. Code Implementation and Execution ...
5. **Error Handling and Iteration** ...
6. **Tool Priority** ...
7. **Task Validation** ...
8. **Task Completion** ...
## !! Key Constraints and Mandatory Requirements !!
- Error Reflection and Iteration ...
- Absolute paths required ...
- Do not repeat code generation ...
- PyTorch Priority ...
- PYTHONPATH ...
- Tools + Code ...
...
```

中文翻译与说明：
- 作用：为“代码分析”Agent 提供系统级行为规范：分步计划、优先工具、绝对路径、完整可执行脚本、错误修复循环、结果校验与 `<TERMINATE>` 结束。
- 触发：`Code_Explorer` 初始化时作为系统提示注入。
- 关键要求：
  - 绝对路径；禁止只给片段代码；安装依赖要在代码块内；无需手动 cat 文件；不可新建虚拟环境/不可用 Docker；深度学习优先 PyTorch；任务完成提供总结并 `<TERMINATE>`。

### 4) TRAIN_PROMPT（src/core/prompt.py）

原文（包含示例代码引用）：
```
# =============== Model Training and Inference Guide ===============
...（环境/框架、数据、训练、早停、Checkpoint、单文件组织、日志、避免大 try/except、结果与输出规范）...
Here is sample code for checkpoint saving, loading, and early stopping...
{train_pipline_example2}
...（GPU、保存路径、结果文件校验等特别说明）...
```

中文翻译与说明：
- 作用：对训练/推理任务给出硬性流程规范与代码示例（EarlyStopping、Checkpoint 保存/恢复、单脚本组织）。
- 触发：`CodeExplorer` 在 `task_type == 'kaggle'` 时作为 `additional_instructions` 附加到系统提示。
- 关键要求：
  - 仅 PyTorch；GPU 优先；每轮保存 checkpoint 与模型；实时推理输出；最终产物命名与存在性校验。

### 5) DEEP_SEARCH_SYSTEM_PROMPT（src/services/prompts/deepsearch_prompt.py）

原文：
```
You are a professional researcher skilled in analyzing problems and formulating search strategies.
... (step-by-step reasoning, entity extraction, next task, search vs browse, horizontal-first strategy, misalignment checks, multiple rounds) ...
When you believe you have collected enough information and prepared a final answer, clearly mark it as <TERMINATE>, ending with <TERMINATE>.
```

中文翻译与说明：
- 作用：深度搜索“研究员”系统提示，强调“先横后纵”的浏览策略、迭代反思与错位校正，信息充分后 `<TERMINATE>`。
- 触发：`AutogenDeepSearchAgent` 研究员 Agent 初始化。

### 6) DEEP_SEARCH_SYSTEM_PROMPT_BACK2 / BACK3（src/services/prompts/deepsearch_prompt.py）

原文：
```
... BACK2：面向金融研究场景的更严格四步法（分解计划→执行扩展→反思迭代→综合结论）...
... BACK3：强调横向优先的 SERP 充分挖掘策略与并行浏览 ...
```

中文翻译与说明：
- 作用：深搜系统提示的备用版本（更长、更严格），可根据需要替换以获得更强的研究范式。
- 默认未启用；保留作备选模板。

### 7) EXECUTOR_SYSTEM_PROMPT（src/services/prompts/deepsearch_prompt.py）

原文：
```
You are the researcher's assistant, responsible for executing search and browsing operations.
... (only reply TERMINATE when researcher indicates completion; do not alter user question) ...
```

中文翻译与说明：
- 作用：深搜“执行者”系统提示，只执行研究员指令的检索/浏览；终止条件严格受研究员驱动。
- 触发：`AutogenDeepSearchAgent` 执行 Agent 初始化。

### 8) DEEP_SEARCH_CONTEXT_SUMMARY_PROMPT（src/services/prompts/deepsearch_prompt.py）

原文：
```
Based on the conversation context, provide a refined summary of the tool return results...
```

中文翻译与说明：
- 作用：将工具长输出压缩为要点（事实、数据、时间、链接等），便于继续推理或控长。
- 触发：深搜流程中对超长工具返回进行摘要时使用。

### 9) DEEP_SEARCH_RESULT_REPORT_PROMPT（src/services/prompts/deepsearch_prompt.py）

原文：
```
Based on the entire conversation context and all collected information, directly, clearly, and completely answer the user's original query.
...（包含必须项：关键事实/数据/时间/上下文/引用；风格：直给结论、条理清晰、可操作）...
```

中文翻译与说明：
- 作用：生成最终报告式答案，覆盖关键信息并给出明确结论与引用。
- 触发：深搜会话的总结阶段。

### 10) Coder_Prompt（src/services/prompts/general_coder_prompt.py）

原文（节选）：
```
You are a helpful AI assistant.
... when to suggest python/sh code, how to install deps, # filename: header, error-fix loop, only reply TERMINATE when done ...
```

中文翻译与说明：
- 作用：通用编码助理的系统提示，规定何时产出代码/脚本、输出规范、自动执行方式与错误修复流程，完成时回复 “TERMINATE”。
- 触发：`GeneralCoder` 助手机制。

### 11) Coder_Prompt_Update / _en / _zh（src/services/prompts/general_coder_prompt.py）

原文：
```
... Update：更严格的脚本结构、错误处理、日志与可执行性要求 ...
... _zh：先给 shell 依赖安装脚本，再给 Python 代码，强调主函数与异常捕获 ...
```

中文翻译与说明：
- 作用：加强型系统提示，提升鲁棒性与工程化程度；`_zh` 版本适配中文任务描述与输出习惯。
- 触发：可按需替换默认 `Coder_Prompt`。

### 12) Code_Planning_Prompt（src/services/prompts/general_coder_prompt.py）

原文：
```
You are an advanced AI planning agent designed to create comprehensive and effective plans...
```

中文翻译与说明：
- 作用：仅生成高质量计划（目标/步骤/依赖/挑战/资源/度量），不执行代码。
- 触发：需要“先规划、后执行”的场景。

### 13) Optimized_Task_Execution_Prompt（src/services/prompts/optimized_task_execution.py）

原文：
```
# Task Execution Path Optimization Prompt (Including Code Correction and Task Summary)
...（提炼目标、关键步骤、纠错、仅保留最终正确代码、生成最优执行路径与总结）...
```

中文翻译与说明：
- 作用：将对话与执行轨迹重排为“最优路径”，只保留最终正确代码与关键步骤，并输出任务总结。

### 14) Optimiz_Dialogue_History_Prompt（src/services/prompts/optimized_task_execution.py）

原文：
```
# Enhanced Dialogue History Optimization Prompt (Including Tool Calls)
...（压缩对话，保留角色、工具调用与关键信息，输出数组格式）...
```

中文翻译与说明：
- 作用：在不丢失关键信息的前提下大幅精简历史对话，便于后续继续工作。

### 15) SYSTEM_MESSAGE_HAS_SUFFICIENT_INFO / GENERATE_ANSWER / IMPROVE_QUERY（src/utils/web_search_agent/prompt_web_search.py）

原文：
```
SYSTEM_MESSAGE_HAS_SUFFICIENT_INFO: Analyze the search results... only 'Yes' or 'No'.
SYSTEM_MESSAGE_GENERATE_ANSWER: Generate a comprehensive answer... Provide only the answer.
SYSTEM_MESSAGE_IMPROVE_QUERY: ... Think on Graph (ToG) ... provide only the improved query.
```

中文翻译与说明：
- 作用：Web 搜索微提示：判断是否足够、直接生成答案、改写优化查询（ToG）。
- 触发：Web 搜索代理的子步骤。

### 16) Code Block Execution Planner Prompts（src/services/autogen_upgrade/codeblock_judge.py）

原文（系统提示，节选）：
```
You are a code block execution planner.
Input is a set of code blocks extracted from conversation...
Task description:
1) Judge whether each code block is runnable and whether the language label matches (language_ok)
2) Identify intent (env_setup/direct_exec/script_run/other)
3) Extract target_file
4) Deduplication rules
5) Sorting rules
Output JSON format: { "blocks": [...], "order": [...] }
... examples ...
Only output JSON, no other text.
```

中文翻译与说明：
- 作用：当回复中包含多个代码块时，调用 LLM 对其进行“可执行性/语言匹配/意图/目标文件”判定、去重与排序，输出 JSON 计划。
- 触发：扩展的执行代理在代码执行前预处理代码块。

### 17) scheduler_system_message（src/core/agent_scheduler.py）

原文（节选）：
```
Role: Enhanced Task Scheduler
...（四种模式选择；先 Web 搜索评估；仓库优先“搜库→跑库”策略；去重/终止策略）...
```

中文翻译与说明：
- 作用：全局调度系统提示，负责在 Web 搜索 / 仓库模式 / 通用编码 三种模式之间做决策与编排工具。
- 触发：`RepoMasterAgent` 的调度 Agent。

### 18) user_proxy_system_message（src/core/agent_scheduler.py）

原文：
```
Role: Execution Proxy (User Proxy)
...（不直接面向用户、只向调度返回工具结果、避免复述、终止策略）...
```

中文翻译与说明：
- 作用：调度流中的执行代理提示，约束其行为仅为执行和汇报，不对用户输出结论。

### 19) Code_Excuter 系统提示（src/core/agent_code_explore.py）

原文：
```
You are the assistant to the code analyzer, responsible for executing code analysis and viewing operations.
After completing operations, return the results to the code analyzer for analysis.
When the task is completed or cannot be completed, you should reply "TERMINATE" ...
```

中文翻译与说明：
- 作用：代码探索执行代理的系统提示，只做执行与返回结果，结束条件明确。

### 20) TaskManager.get_task_prompt（src/core/git_task.py）

原文（模板）：
```
### Task Description
{task_description}

#### Repository Path (Absolute Path): 
```
{repo_path}
```
Understanding Guide: ['Read README.md to understand basic project functionality and usage']

#### File Paths
- Input file paths and descriptions:
{input_data}

- Output file directory: 
Results must be saved in the {output_dir_path} directory. If results are saved in the repository directory, they need to be moved to the {output_dir_path} directory.

#### Additional Notes
**Core Objective**: Quickly understand and analyze the code repository, generate and execute necessary code or call tools to efficiently and accurately complete user-specified tasks.
```

中文翻译与说明：
- 作用：仓库任务卡片模板，统一任务描述、仓库绝对路径、输入/输出与核心目标的格式。
- 触发：仓库任务初始化与编排。


