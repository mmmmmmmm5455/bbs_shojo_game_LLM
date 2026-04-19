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
        # 默认放宽：llama3 等较大模型冷启动首次 chat 常超过十几秒，过短会误判为不可用并退回模板。
        self.timeout = (
            timeout
            if timeout is not None
            else _env_float("BBS_SHOJO_OLLAMA_TIMEOUT", 12.0)
        )
        # 默认不做更长重试，保证图形端响应时限；需要时可手动上调。
        self.retry_timeout = _env_float(
            "BBS_SHOJO_OLLAMA_RETRY_TIMEOUT", self.timeout
        )
        self.keep_alive = os.environ.get("BBS_SHOJO_OLLAMA_KEEP_ALIVE", "20m").strip()
        self._host = host
        self._client: Optional[ollama.Client] = None
        self._available: Optional[bool] = None

    def _client_lazy(self, timeout_override: Optional[float] = None) -> ollama.Client:
        if timeout_override is not None:
            host = self._host or os.environ.get("OLLAMA_HOST")
            if host:
                return ollama.Client(host=host, timeout=timeout_override)
            return ollama.Client(timeout=timeout_override)
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
            # 更短默认输出，减少首轮等待；可用环境变量覆盖
            "num_predict": _env_int("BBS_SHOJO_OLLAMA_NUM_PREDICT", 40),
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

        def _chat_once(timeout_override: Optional[float] = None) -> Optional[str]:
            client = self._client_lazy(timeout_override=timeout_override)
            kwargs = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "options": self._chat_options(),
                "stream": True,
            }
            if self.keep_alive:
                kwargs["keep_alive"] = self.keep_alive
            stream = client.chat(**kwargs)
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

        try:
            text = _chat_once()
            if text:
                return text
        except Exception:
            text = None

        # 常见于大模型首次加载：第一次超时/空响应后，用更长超时再试一次。
        if self.retry_timeout > self.timeout + 1:
            try:
                text = _chat_once(timeout_override=self.retry_timeout)
                if text:
                    return text
            except Exception:
                pass
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
