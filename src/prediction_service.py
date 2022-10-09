from typing import List

import requests

API_SERVER_URL = "http://localhost:8000/predict"


class PredictionItem:
    def __init__(self, label: str, text: str, score: float):
        self.label = label
        self.text = text
        self.score = score

    def __repr__(self):
        return f"{self.label}: '{self.text}' (score: {self.score:0.2f})"

    def __str__(self):
        return self.__repr__()


class Prediction:
    def __init__(
        self, segments: List[str], labels: List[str], scores: List[float]
    ) -> None:
        self._benefits = []
        self._drawbacks = []

        for segment, label, score in zip(segments, labels, scores):
            item = PredictionItem(label=label, text=segment, score=score)
            print(f"Processing item: {item}")
            if label == "benefit":
                self._benefits.append(item)
            elif label == "drawback":
                self._drawbacks.append(item)
            else:
                raise ValueError(f"Unknown label: {label}")

    @property
    def all_benefits(self) -> List[PredictionItem]:
        return self._benefits

    @property
    def all_drawbacks(self) -> List[PredictionItem]:
        return self._drawbacks

    @property
    def non_empty_benefits(self) -> List[PredictionItem]:
        return self._filter_items(self._benefits)

    @property
    def non_empty_drawbacks(self) -> List[PredictionItem]:
        return self._filter_items(self._drawbacks)

    def _filter_items(self, items: List[PredictionItem]) -> List[PredictionItem]:
        non_empty_items = [item for item in items if item.text.strip() != ""]
        sorted_items = sorted(
            non_empty_items, key=lambda item: item.score, reverse=True
        )
        deduped_items = []
        observed_texts = []
        for item in sorted_items:
            if item.text not in observed_texts:
                deduped_items.append(item)
                observed_texts.append(item.text)
        return deduped_items


def predict(review_text) -> Prediction:
    payload = {
        "url": "https://localhost/",
        "review_text": review_text,
    }
    resp = requests.post(url=API_SERVER_URL, json=payload)
    if resp.status_code != 200:
        return "Error"
    result = resp.json()
    return Prediction(
        segments=result["segments"],
        labels=result["labels"],
        scores=result["scores"],
    )
