"""
stream_filter.py — State-machine stream filter for stripping <think>...</think> reasoning blocks.
"""
from typing import AsyncGenerator


def merge_consecutive_roles(messages: list[dict]) -> list[dict]:
    """Ensures roles alternate (user, assistant, user...). Merges consecutive identical roles."""
    if not messages:
        return []

    merged = []
    for msg in messages:
        if merged and merged[-1]["role"] == msg["role"]:
            merged[-1]["content"] += "\n" + msg["content"]
        else:
            merged.append({"role": msg["role"], "content": msg["content"]})
    return merged


async def filter_thinking_stream(token_generator: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    """
    Streams tokens while stripping <think>...</think> reasoning blocks in real-time.
    Handles split tags across chunk boundaries without buffering the whole response.
    """
    in_reasoning = False
    buffer = ""

    async for token in token_generator:
        buffer += token

        while True:
            if not in_reasoning:
                if "<think" in buffer.lower():
                    start_idx = buffer.lower().find("<think")
                    pre_content = buffer[:start_idx]
                    if pre_content:
                        yield pre_content

                    buffer = buffer[start_idx:]
                    in_reasoning = True
                    continue
                else:
                    if any(buffer.lower().startswith(s) for s in ["<", "<t", "<th", "<thi", "<thin", "<think"]):
                        break

                    if buffer:
                        yield buffer
                        buffer = ""
                    break
            else:
                if "</think>" in buffer.lower():
                    end_idx = buffer.lower().find("</think>") + len("</think>")
                    buffer = buffer[end_idx:]
                    in_reasoning = False
                    continue
                else:
                    if len(buffer) > 10:
                        buffer = buffer[-10:]
                    break

    if not in_reasoning and buffer:
        yield buffer
