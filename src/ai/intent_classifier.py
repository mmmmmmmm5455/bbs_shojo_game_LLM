"""
本地语义意图分类（sentence-transformers）。
首次 classify 时加载模型并预计算意图向量；依赖未安装或加载失败时由调用方回退关键词逻辑。

安装（可选）: 在仓库根目录执行 ``pip install -r requirements-intent.txt``。
打包 exe 未内置本依赖时自动走关键词回退（见 BBSEngine._semantic_intent_enabled）。
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

# 键须与 GirlState.keyword_responses 基础键一致
INTENT_DESCRIPTIONS: Dict[str, str] = {
    "greeting": "打招呼、问好、hello hi 嗨 你好 在吗 hey good morning",
    "sad": "悲伤、难过、低落、想哭、心情不好、I feel sad depressed down blue unhappy",
    "tech": "程序、代码、bug、病毒、技术、编程、software code programming virus",
    "past": "过去、回忆、以前、小时候、曾经、remember the past childhood long ago",
    "future": "未来、以后、明天、打算、期望、hope future tomorrow plans what if",
    "love": "喜欢、爱、好感、suki love crush I love you like you romantically",
    "thanks": "感谢、谢谢、thanks thx 多谢 thank you appreciate",
    "bye": "再见、拜拜、晚安、离开、goodbye bye see you later good night",
    "question": "提问、询问、为什么、怎么办、疑问吗呢嘛 how why what when question",
    "confused": "困惑、不知道自己是谁、身份、真实、存在、混乱 confused who am I identity lost",
    "lonely": "孤独、一个人、寂寞、等待、没人理 I feel lonely alone isolated nobody listens empty",
    "phantom": "幽灵、数据、残留、灵魂、幻影、其他人 ghost phantom data soul spirit others",
}


class IntentClassifier:
    """延迟加载 MiniLM，对玩家句与意图描述做余弦相似度（归一化后点积）。"""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        threshold: float = 0.4,
    ) -> None:
        self.model_name = model_name
        self.threshold = threshold
        self._model = None
        self._intent_matrix: Optional[np.ndarray] = None
        self._intent_labels: Optional[List[str]] = None
        self._load_error: Optional[str] = None

    def _ensure_loaded(self) -> bool:
        if self._load_error is not None:
            return False
        if self._model is not None:
            return True
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            self._load_error = str(e)
            return False
        try:
            self._model = SentenceTransformer(self.model_name)
            labels = list(INTENT_DESCRIPTIONS.keys())
            texts = [INTENT_DESCRIPTIONS[k] for k in labels]
            mat = self._model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            self._intent_matrix = np.asarray(mat, dtype=np.float32)
            self._intent_labels = labels
        except Exception as e:
            self._model = None
            self._load_error = str(e)
            return False
        return True

    def classify(self, text: str) -> Tuple[Optional[str], float]:
        """
        返回 (意图键, 最佳相似度)。相似度低于 threshold 时意图为 None。
        模型未就绪时返回 (None, 0.0)。
        """
        if not text.strip():
            return None, 0.0
        if not self._ensure_loaded():
            return None, 0.0
        assert self._model is not None and self._intent_matrix is not None
        assert self._intent_labels is not None
        q = self._model.encode(
            [text.strip()[:512]],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]
        q = np.asarray(q, dtype=np.float32)
        sims = self._intent_matrix @ q
        idx = int(np.argmax(sims))
        best_score = float(sims[idx])
        best = self._intent_labels[idx]
        if best_score >= self.threshold:
            return best, best_score
        return None, best_score

    @property
    def available(self) -> bool:
        return self._ensure_loaded()

    @property
    def disabled_reason(self) -> Optional[str]:
        return self._load_error
