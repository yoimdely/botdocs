from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

_CONTEXT_TTL = 15 * 60  # 15 minutes
_document_contexts: Dict[str, Dict[str, Any]] = {}


def _cleanup() -> None:
    now = time.time()
    expired = [doc_id for doc_id, payload in _document_contexts.items() if now - payload.get("created_at", 0) > _CONTEXT_TTL]
    for doc_id in expired:
        _document_contexts.pop(doc_id, None)


def store_document_context(payload: Dict[str, Any]) -> str:
    _cleanup()
    doc_id = uuid.uuid4().hex
    payload = dict(payload)
    payload["created_at"] = time.time()
    _document_contexts[doc_id] = payload
    return doc_id


def get_document_context(doc_id: str) -> Optional[Dict[str, Any]]:
    _cleanup()
    context = _document_contexts.get(doc_id)
    if not context:
        return None
    if time.time() - context.get("created_at", 0) > _CONTEXT_TTL:
        _document_contexts.pop(doc_id, None)
        return None
    return context
