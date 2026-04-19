"""
本地 Ollama 对话兜底（Phase 2）。需本机安装 Ollama 并 ``ollama pull <model>``。
未运行 / 超时 / 异常时由调用方回退台词池。
"""
from __future__ import annotations

import os
import threading
from typing import Callable, List, Optional

import ollama


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class LLMFallback:
    def __init__(
        self,
        model: str = "phi3:mini",
        timeout: Optional[float] = None,
        host: Optional[str] = None,
    ) -> None:
        self.model = model
        self.timeout = (
            timeout
            if timeout is not None
            else _env_float("BBS_SHOJO_OLLAMA_TIMEOUT", 12.0)
        )
        self._host = host
        self._client: Optional[ollama.Client] = None
        self._available: Optional[bool] = None

    def _client_lazy(self) -> ollama.Client:
        if self._client is None:
            host = self._host or os.environ.get("OLLAMA_HOST")
            if host:
                self._client = ollama.Client(host=host, timeout=self.timeout)
            else:
                self._client = ollama.Client(timeout=self.timeout)
        return self._client

    def check_available(self) -> bool:
        """Ollama 可达且已安装目标模型（名称精确匹配或同族 tag）。"""
        try:
            r = self._client_lazy().list()
            names: List[str] = []
            for m in getattr(r, "models", []) or []:
                names.append(getattr(m, "model", "") or "")
            if self.model in names:
                return True
            base = self.model.split(":")[0] if ":" in self.model else self.model
            return any(n.split(":")[0] == base for n in names if n)
        except Exception:
            return False

    def is_available_cached(self) -> bool:
        if self._available is None:
            self._available = self.check_available()
        return bool(self._available)

    def invalidate_cache(self) -> None:
        self._available = None

    def _chat_options(self) -> dict:
        return {
            "temperature": _env_float("BBS_SHOJO_OLLAMA_TEMPERATURE", 0.6),
            "num_predict": _env_int("BBS_SHOJO_OLLAMA_NUM_PREDICT", 80),
        }

    def generate_reply_sync(
        self,
        prompt: str,
        on_first_chunk: Optional[Callable[[], None]] = None,
    ) -> Optional[str]:
        """同步生成；阻塞当前线程。流式聚合，首 token 时可选回调。"""
        if not prompt.strip():
            return None
        first_sent = False

        def _maybe_first() -> None:
            nonlocal first_sent
            if on_first_chunk and not first_sent:
                first_sent = True
                try:
                    on_first_chunk()
                except Exception:
                    pass

        try:
            client = self._client_lazy()
            stream = client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options=self._chat_options(),
                stream=True,
            )
            parts: List[str] = []
            for chunk in stream:
                piece = ""
                if chunk is not None:
                    msg = getattr(chunk, "message", None)
                    if msg is not None:
                        piece = getattr(msg, "content", None) or ""
                    elif isinstance(chunk, dict):
                        piece = (chunk.get("message") or {}).get("content") or ""
                if piece:
                    _maybe_first()
                    parts.append(piece)
            text = "".join(parts).strip()
            return text or None
        except Exception:
            return None

    def generate_reply_async(
        self,
        prompt: str,
        on_start: Optional[Callable[[], None]] = None,
        on_done: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        """后台线程调用 Ollama；结果经回调返回（不阻塞主线程）。"""

        def _worker() -> None:
            if on_start:
                on_start()
            try:
                text = self.generate_reply_sync(prompt)
                if text and on_done:
                    on_done(text)
                elif not text and on_error:
                    on_error("empty_or_failed")
            except Exception as e:
                if on_error:
                    on_error(str(e))

        threading.Thread(target=_worker, daemon=True).start()
