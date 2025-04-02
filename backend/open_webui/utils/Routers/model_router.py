
from typing import Dict
from .router import Router

class ModelRouter(Router):
    def __init__(
        self,
        models: Dict[str, str],
        classifier: str = "zero-shot-classification",
        model: str = "facebook/bart-large-mnli",
        n: int = 1,
        threshold: float = 0.1,
    ) -> None:
        super().__init__(models, classifier, model, n, threshold)

