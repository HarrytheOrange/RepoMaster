import json
import os
from datetime import datetime
from textwrap import dedent
from typing import Any, Optional, Tuple

import tiktoken
from autogen.oai import OpenAIWrapper


TOOL_RESPONSE_SUMMARY_PROMPT = dedent("""
You are a senior code-analysis assistant responsible for compressing verbose Autogen tool outputs.

[Tool Info]
- Name: {tool_name}
- Arguments: {tool_arguments}

[Original Output]
{tool_response}

Create a concise English summary that still preserves critical details. Focus on:
1. Conclusions, key findings, important paths, or command results.
2. Errors/exceptions and explicit causes.
3. Required follow-up actions or TODOs.

Use short paragraphs or bullet points and avoid omitting essential information.
""")


class ToolResponseSummarizer:
    def __init__(
        self,
        llm_config: Optional[dict[str, Any]] = None,
        token_limit: int = 1000,
        work_dir: Optional[str] = None,
        agent_name: str = "tool_response_summarizer",
    ):
        self.llm_config = llm_config or {}
        self.token_limit = token_limit
        self.work_dir = work_dir
        self.agent_name = agent_name or "tool_response_summarizer"
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def maybe_summarize(
        self,
        *,
        tool_name: Optional[str],
        tool_arguments: Any,
        tool_response: str,
    ) -> Optional[str]:
        if not tool_response:
            return None

        before_tokens = self._count_tokens(tool_response)
        if before_tokens <= self.token_limit:
            return None

        summary, usage, model = self._generate_summary(tool_name, tool_arguments, tool_response)
        if not summary:
            return None

        after_tokens = self._count_tokens(summary)
        self._log_compression(
            model=model,
            usage=usage,
            source_tool=tool_name,
            before_tokens=before_tokens,
            after_tokens=after_tokens,
        )
        return summary

    def _count_tokens(self, text: str) -> int:
        if not text:
            return 0
        try:
            return len(self.encoding.encode(text))
        except Exception:
            return len(text)

    def _generate_summary(
        self,
        tool_name: Optional[str],
        tool_arguments: Any,
        tool_response: str,
    ) -> Tuple[Optional[str], Optional[dict[str, Any]], Optional[str]]:
        prompt = TOOL_RESPONSE_SUMMARY_PROMPT.format(
            tool_name=tool_name or "unknown_tool",
            tool_arguments=self._format_arguments(tool_arguments),
            tool_response=tool_response,
        )
        messages = [{"role": "user", "content": prompt}]

        try:
            client = OpenAIWrapper(**self.llm_config)
            response = client.create(messages=messages)
        except Exception as exc:
            print(f"[ToolResponseSummarizer] summarize failed: {exc}", flush=True)
            return None, None, None

        summary = None
        try:
            summary = response.choices[0].message.content
        except Exception:
            pass

        usage = self._extract_usage(response)
        model = getattr(response, "model", None)
        if model is None and hasattr(response, "to_dict"):
            model = response.to_dict().get("model")

        return summary, usage, model

    def _format_arguments(self, arguments: Any) -> str:
        if arguments is None:
            return ""
        if isinstance(arguments, str):
            try:
                parsed = json.loads(arguments)
                if isinstance(parsed, (dict, list)):
                    arguments = parsed
            except Exception:
                return arguments
        if isinstance(arguments, (dict, list)):
            try:
                return json.dumps(arguments, ensure_ascii=False)
            except Exception:
                return str(arguments)
        return str(arguments)

    def _extract_usage(self, response) -> Optional[dict[str, Any]]:
        usage = getattr(response, "usage", None)
        if usage is None and hasattr(response, "to_dict"):
            usage = response.to_dict().get("usage")
        if usage is None:
            return None

        def _get(val, key):
            if isinstance(val, dict):
                return val.get(key)
            return getattr(val, key, None)

        return {
            "prompt_tokens": _get(usage, "prompt_tokens"),
            "completion_tokens": _get(usage, "completion_tokens"),
            "total_tokens": _get(usage, "total_tokens"),
        }

    def _log_compression(
        self,
        *,
        model: Optional[str],
        usage: Optional[dict[str, Any]],
        source_tool: Optional[str],
        before_tokens: int,
        after_tokens: int,
    ):
        log_dir = self.work_dir or os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "token_usage.log")

        entry = {
            "ts": datetime.now().isoformat(),
            "agent": self.agent_name,
            "model": model,
            "tool": "ToolResponseSummarizer",
            "source_tool": source_tool,
            "tool_response_tokens": after_tokens,
            "compression": {
                "before_tokens": before_tokens,
                "after_tokens": after_tokens,
            },
            "usage": usage,
        }

        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as exc:
            print(f"[ToolResponseSummarizer] log failed: {exc}", flush=True)

