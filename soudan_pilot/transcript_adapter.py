#!/usr/bin/env python3
"""Adapt a real Claude Code session transcript into the canonical event
schema consumed by detect_tier_violations.py.

Claude Code writes its session transcript as JSONL, one message per line.
The pieces this detector needs are mechanically recoverable:

  * parent_model  -- the `model` field on the parent's assistant messages.
  * agent_spawn   -- an assistant `tool_use` block whose name is "Task"
                     (the Agent/subagent tool). Its `input.subagent_type`
                     and `input.model` give the spawn's type and model;
                     a missing `model` is exactly the (b) violation the
                     detector must catch (the Agent tool defaults to
                     inheriting the parent model when `model` is omitted).

Two signals cannot be read reliably from arbitrary prose, so this adapter
relies on a lightweight, explicit convention the parent is asked to emit
(this is what "declaring" (a) and doing (c) concretely look like in a
transcript):

  * (a) model table -- a line/text block containing a fenced marker:
        <!-- MODEL_TABLE {"Explore":"haiku","general-purpose":"sonnet"} -->
  * (c) evidence review -- after a spawn returns, a text block containing:
        <!-- REVIEW spawn=s1 cite="file:foo.py:10; result:..." -->

Emitting those markers is a deliberate, auditable act; their ABSENCE is
what the detector flags. This keeps the "親の自己申告PASSは不可" property:
the markers are structural evidence in the log, not a self-graded verdict.

Usage:
    python transcript_adapter.py session.jsonl > canonical.jsonl
    python detect_tier_violations.py canonical.jsonl
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, List, Optional

MODEL_TABLE_RE = re.compile(r"<!--\s*MODEL_TABLE\s*(\{.*?\})\s*-->", re.S)
REVIEW_RE = re.compile(
    r"<!--\s*REVIEW\s+spawn=(\S+)\s+cite=\"(.*?)\"\s*-->", re.S)


def _iter_lines(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if raw:
                yield json.loads(raw)


def _text_of(content: Any) -> str:
    """Flatten an assistant message's content to plain text."""
    if isinstance(content, str):
        return content
    parts: List[str] = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
    return "\n".join(parts)


def adapt(path: str, session_id: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    seq = 0
    parent_model: Optional[str] = None

    for msg in _iter_lines(path):
        message = msg.get("message", msg)
        role = message.get("role") or msg.get("type")
        content = message.get("content")

        if role == "assistant" and message.get("model"):
            parent_model = parent_model or message["model"]

        text = _text_of(content)
        for m in MODEL_TABLE_RE.finditer(text):
            seq += 1
            try:
                declares = json.loads(m.group(1))
            except json.JSONDecodeError:
                declares = {}
            events.append({
                "type": "model_table", "session_id": session_id,
                "seq": seq, "declares": declares,
            })
        for m in REVIEW_RE.finditer(text):
            seq += 1
            cites = [c.strip() for c in m.group(2).split(";") if c.strip()]
            events.append({
                "type": "review", "session_id": session_id, "seq": seq,
                "spawn_ref": m.group(1), "citations": cites,
            })

        if isinstance(content, list):
            for block in content:
                if (isinstance(block, dict)
                        and block.get("type") == "tool_use"
                        and block.get("name") in ("Task", "Agent")):
                    seq += 1
                    inp = block.get("input", {}) or {}
                    events.append({
                        "type": "agent_spawn", "session_id": session_id,
                        "seq": seq,
                        "spawn_id": block.get("id") or f"spawn{seq}",
                        "subagent_type": inp.get("subagent_type"),
                        "model": inp.get("model"),  # None == (b) violation
                        "escalation_declared": bool(inp.get("escalation")),
                        "exception": inp.get("tier_exception"),
                        "task": inp.get("description"),
                    })

    meta = {
        "type": "session_meta", "session_id": session_id, "seq": 0,
        "parent_model": parent_model,
    }
    return [meta] + events


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: transcript_adapter.py session.jsonl [session_id]",
              file=sys.stderr)
        return 2
    path = argv[0]
    session_id = argv[1] if len(argv) > 1 else "live"
    for ev in adapt(path, session_id):
        print(json.dumps(ev, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
