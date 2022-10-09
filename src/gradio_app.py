from typing import List

import gradio as gr

from src.prediction_service import Prediction, PredictionItem, predict


def convert_prediction_items_to_text(
    items: List[PredictionItem], bullet: str, type_singular: str, type_plural: str
) -> str:
    """Converts a list of `PredictionItem`s to a text that can be displayed in the UI."""
    result_text = ""
    if len(items) == 0:
        result_text += f"No {type_singular} found.\n"
    else:
        result_text += "The model found following "
        if len(items) == 1:
            result_text += f"{type_singular}:\n"
        else:
            result_text += f"{type_plural}:\n"
        for item in items:
            result_text += f" {bullet} {item.text} [score: {item.score:0.2f}]\n"
    return result_text


def choosistant(review_text):
    # Let the prediction service do its magic.
    prediction: Prediction = predict(review_text)

    # Convert the prediction to a text that can be displayed in the UI.
    result_text = "Here is the result of prediction.\n\n"

    result_text += convert_prediction_items_to_text(
        items=prediction.non_empty_benefits,
        bullet="😁",
        type_singular="benefit",
        type_plural="benefits",
    )

    result_text += "\n"

    result_text += convert_prediction_items_to_text(
        items=prediction.non_empty_drawbacks,
        bullet="😐",
        type_singular="drawback",
        type_plural="drawback",
    )

    return result_text


text_input = gr.Textbox(
    lines=8, placeholder="Enter the review text here...", label="Review Text"
)
new_title = gr.Textbox(label="Detected pro/con")
example_url = "http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Musical_Instruments_5.json.gz"
iface = gr.Interface(
    choosistant,
    [text_input],
    new_title,
    description=f"Checkout some amazon reviews eg at [{example_url}]({example_url})",
    allow_flagging="manual",
    flagging_options=["Incorrect", "Offensive", "Other"],
    examples=[["The top side came ripped off"], ["The gear is child friendly"]],
)

iface.launch(debug=True, server_port=8090)
