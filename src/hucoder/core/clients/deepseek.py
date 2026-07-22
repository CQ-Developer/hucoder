import json
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Literal, NotRequired, TypedDict

import httpx

from .commons import clean_dict


class SystemMessage(TypedDict):
    role: Literal["system"]
    content: str
    name: NotRequired[str]


class UserMessage(TypedDict):
    role: Literal["user"]
    content: str
    name: NotRequired[str]


class AssistantMessage(TypedDict):
    role: Literal["assistant"]
    content: str
    name: NotRequired[str]
    # Beta
    prefix: NotRequired[bool]
    reasoning_content: NotRequired[str]


class ToolMessage(TypedDict):
    role: Literal["tool"]
    content: str
    tool_call_id: str


class Thinking(TypedDict):
    type: Literal["enabled", "disabled"]


class ResponseFormat(TypedDict):
    type: Literal["texts", "json_object"]


class StreamOptions(TypedDict):
    include_usage: bool


class ToolFunction(TypedDict):
    name: str
    description: NotRequired[str]
    strict: NotRequired[bool]
    parameters: NotRequired[dict[str, Any]]


class Tool(TypedDict):
    type: Literal["function"]
    function: ToolFunction


class NamedFunctionToolChoice(TypedDict):
    name: str


class FunctionToolChoice(TypedDict):
    type: Literal["function"]
    function: NamedFunctionToolChoice


@dataclass(frozen=True, kw_only=True)
class ChatCompletionsUsageTokensDetails:
    reasoning_tokens: int | None = None


@dataclass(frozen=True, kw_only=True)
class ChatCompletionsUsage:
    completion_tokens: int
    prompt_tokens: int
    prompt_cache_hit_tokens: int
    prompt_cache_miss_tokens: int
    total_tokens: int
    completion_tokens_details: ChatCompletionsUsageTokensDetails | None = None


@dataclass(frozen=True, kw_only=True)
class ChatCompletionsChoiceMessageToolCallFunction:
    name: str
    arguments: str


@dataclass(frozen=True, kw_only=True)
class ChatCompletionsChoiceMessageToolCall:
    id: str
    type: Literal["function"]
    function: ChatCompletionsChoiceMessageToolCallFunction


@dataclass(frozen=True, kw_only=True)
class ChatCompletionsChoiceMessage:
    role: Literal["assistant"]
    content: str | None
    reasoning_content: str | None = None
    tool_calls: list[ChatCompletionsChoiceMessageToolCall] | None = None


@dataclass(frozen=True, kw_only=True)
class ChatCompletionsChoiceLogprobsContentTop:
    token: str
    logprob: float
    bytes: bytes | None


@dataclass(frozen=True, kw_only=True)
class ChatCompletionsChoiceLogprobsContent:
    token: str
    logprob: float
    bytes: bytes | None
    top_logprobs: list[ChatCompletionsChoiceLogprobsContentTop]


@dataclass(frozen=True, kw_only=True)
class ChatCompletionsChoiceLogprobs:
    content: list[ChatCompletionsChoiceLogprobsContent] | None
    reasoning_content: list[ChatCompletionsChoiceLogprobsContent] | None = None


@dataclass(frozen=True, kw_only=True)
class ChatCompletionsChoice:
    index: int
    finish_reason: Literal["stop", "length", "content_filter", "tool_calls", "insufficient_system_resource"]
    message: ChatCompletionsChoiceMessage
    logprobs: ChatCompletionsChoiceLogprobs | None


@dataclass(frozen=True, kw_only=True)
class ChatCompletions:
    id: str
    choices: list[ChatCompletionsChoice]
    created: int
    model: str
    system_fingerprint: str
    object: Literal["chat.completion"]
    usage: ChatCompletionsUsage | None = None


class DeepSeekChatClient:
    def __init__(self, *, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def chat(
        self,
        *,
        messages: list[SystemMessage | UserMessage | AssistantMessage | ToolMessage],
        model: Literal["deepseek-v4-flash", "deepseek-v4-pro"],
        thinking: Thinking | None = None,
        max_tokens: int | None = None,
        response_format: ResponseFormat | None = None,
        stop: str | list[str] | None = None,
        stream: bool | None = None,
        stream_options: StreamOptions | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        tools: list[Tool] | None = None,
        tool_choice: Literal["none", "auto", "required"] | FunctionToolChoice | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        user_id: str | None = None,
    ) -> ChatCompletions | Iterator[ChatCompletions]:
        raw = {
            "messages": messages,
            "model": model,
            "thinking": thinking,
            "max_tokens": max_tokens,
            "response_format": response_format,
            "stop": stop,
            "stream": stream,
            "stream_options": stream_options,
            "temperature": temperature,
            "top_p": top_p,
            "tools": tools,
            "tool_choice": tool_choice,
            "logprobs": logprobs,
            "top_logprobs": top_logprobs,
            "user_id": user_id,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        body = clean_dict(raw)
        if not stream:
            response = httpx.post(self.base_url, headers=headers, json=body)
            return ChatCompletions(**response.json())
        with httpx.stream("POST", self.base_url, headers=headers, json=body) as response_frames:
            for line in response_frames.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                if line == "data: [DONE]":
                    return
                yield ChatCompletions(**json.loads(line[5:].strip()))
