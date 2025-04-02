
from typing import Dict
from .router import Router

class GuardrailRouter(Router):
    def __init__(
        self,
        actions: Dict[str, str],
        classifier: str = "zero-shot-classification",
        model: str = "facebook/bart-large-mnli",
        n: int = 3,
        threshold: float = 0.08,
    ) -> None:
        super().__init__(actions, classifier, model, n, threshold)
