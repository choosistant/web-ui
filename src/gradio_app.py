from typing import Any, List, Optional

import gradio as gr

from src.prediction_service import Prediction, PredictionItem, predict


class FlaggingHandler(gr.FlaggingCallback):
    def __init__(self):
        self._csv_logger = gr.CSVLogger()

    def setup(self, components: List[gr.components.Component], flagging_dir: str):
        """Called by Gradio at the beginning of the `Interface.launch()` method.
        Parameters:
        components: Set of components that will provide flagged data.
        flagging_dir: A string, typically containing the path to the directory where
        the flagging file should be storied (provided as an argument to Interface.__init__()).
        """
        self.components = components
        self._csv_logger.setup(components=components, flagging_dir=flagging_dir)

    def flag(
        self,
        flag_data: List[Any],
        flag_option: Optional[str] = None,
        flag_index: Optional[int] = None,
        username: Optional[str] = None,
    ) -> int:
        """Called by Gradio whenver one of the <flag> buttons is clicked.
        Parameters:
        interface: The Interface object that is being used to launch the flagging interface.
        flag_data: The data to be flagged.
        flag_option (optional): In the case that flagging_options are provided, the flag option that is being used.
        flag_index (optional): The index of the sample that is being flagged.
        username (optional): The username of the user that is flagging the data, if logged in.
        Returns:
        (int) The total number of samples that have been flagged.
        """
        for item in flag_data:
            print(f"Flagging: {item}")
        if flag_option:
            print(f"Flag option: {flag_option}")

        if flag_index:
            print(f"Flag index: {flag_index}")

        flagged_count = self._csv_logger.flag(
            flag_data=flag_data,
            flag_option=flag_option,
            flag_index=flag_index,
            username=username,
        )
        return flagged_count


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

    items = prediction.non_empty_benefits + prediction.non_empty_drawbacks
    highlighted_entities = []
    for item in items:
        start_index = review_text.index(item.text)
        end_index = start_index + len(item.text)
        highlighted_entities.append(
            {"start": start_index, "end": end_index, "entity": item.label}
        )

    highlighted_input = {
        "text": review_text,
        "entities": highlighted_entities,
    }

    return highlighted_input, 34123123


def main():
    text_input = gr.Textbox(
        lines=8, placeholder="Enter the review text here...", label="Review Text"
    )
    # new_title = gr.Textbox(label="Detected pro/con")
    txt_pred_id = gr.Textbox(label="ID", visible=False)
    txt_predictions = gr.HighlightedText(label="Predictions", combine_adjacent=True)
    txt_predictions.style(color_map={"drawback": "red", "benefit": "green"})
    example_url = "http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Musical_Instruments_5.json.gz"
    iface = gr.Interface(
        fn=choosistant,
        inputs=[text_input],
        outputs=[txt_predictions, txt_pred_id],
        cache_examples=True,
        description=f"Checkout some amazon reviews eg at [{example_url}]({example_url})",
        allow_flagging="manual",
        flagging_options=["Incorrect", "Offensive", "Other"],
        flagging_dir="data/flagged",
        flagging_callback=FlaggingHandler(),
        examples=[["The top side came ripped off"], ["The gear is child friendly"]],
    )

    iface.launch(debug=True, server_port=8090)


main()
