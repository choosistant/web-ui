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


def choosistant(review_text: str, model_type: str):
    # Let the prediction service do its magic.
    prediction: Prediction = predict(review_text=review_text, model_type=model_type)

    items = prediction.non_empty_benefits + prediction.non_empty_drawbacks
    highlighted_entities = []
    for item in items:
        if item.text in review_text:
            start_index = review_text.index(item.text)
            end_index = start_index + len(item.text)
            highlighted_entities.append(
                {"start": start_index, "end": end_index, "entity": item.label}
            )

    highlighted_input = {
        "text": review_text,
        "entities": highlighted_entities,
    }

    return highlighted_input, prediction.id


def main():
    flagging_handler = FlaggingHandler()

    example_url = "<a href='https://www.amazon.com/b?node=16225007011&pf_rd_r=SVC6K7QE0WNT3575Q2VJ&pf_rd_p=6b30eb15-a900-4294-9772-db8876444356&pd_rd_r=c2a147e6-37bf-41be-ba8b-826e1a45ad4c&pd_rd_w=3WOVP&pd_rd_wg=rWeT0&ref_=pd_gw_unk'>this page</a>"  # noqa: E501
    with gr.Blocks() as iface:
        gr.Markdown(f"Checkout some amazon reviews eg at {example_url}")
        text_input = gr.Textbox(
            lines=8, placeholder="Enter the review text here...", label="Review Text"
        )
        model_input = gr.Radio(
            choices=["qa", "seq2seq"],
            label="Model Choice",
            value="qa",
            show_label=True,
            interactive=True,
            type="value",
        )

        text_button = gr.Button("Submit")
        txt_pred_id = gr.Textbox(label="ID", visible=False)
        txt_predictions = gr.HighlightedText(label="Predictions", combine_adjacent=True)
        txt_predictions.style(color_map={"drawback": "red", "benefit": "green"})

        text_button.click(
            choosistant,
            inputs=[text_input, model_input],
            outputs=[txt_predictions, txt_pred_id],
        )
        with gr.Row():
            btn_incorrect = gr.Button("Flag as incorrect")
            btn_insufficient = gr.Button("Flag as insufficient")
            btn_other = gr.Button("Flag as other")
        flagging_handler.setup(
            components=[text_input, model_input, txt_predictions, txt_pred_id],
            flagging_dir="data/flagged",
        )

        btn_incorrect.click(
            lambda *args: flagging_handler.flag(
                flag_data=args, flag_option="Incorrect"
            ),
            [text_input, model_input, txt_predictions, txt_pred_id],
            None,
            preprocess=False,
        )
        btn_insufficient.click(
            lambda *args: flagging_handler.flag(
                flag_data=args, flag_option="Insufficient"
            ),
            [text_input, model_input, txt_predictions, txt_pred_id],
            None,
            preprocess=False,
        )
        btn_other.click(
            lambda *args: flagging_handler.flag(flag_data=args, flag_option="Other"),
            [text_input, model_input, txt_predictions, txt_pred_id],
            None,
            preprocess=False,
        )

        with gr.Tab("Examples A"):  # examples of good predictions
            gr.Examples(
                examples=[
                    [
                        "Great price on sale. Would be 5 star if it had a card reader slot. The operating system is using 13.5GB of space leaving 18.5GB of useable space. Web camera is pretty bad, only 640x480. Great battery life. Nice size and weight, the 1080p, anti-glare, IPS screen is the best feature. Trackpad is nice and responsive. both USB-A ports seem tight and a bit cheap, but they work and otherwise I'm very happy so far with this Chromebook.",  # noqa: E501
                        "qa",
                    ],
                    [
                        "This is a counterfeit product. Please do not buy!",
                        "seq2seq",
                    ],
                    [
                        "Expensive, but I think it's the only legit Polar Express train set available, and the kids love Polar Express; what can you do?The track you get with the train makes a small oval shape, and is pretty easy to fit together. Slightly easier than Lego, but harder than Trackmaster stuff.The bell that comes with the train is really bad, we've had cat toys which resembled a bell better than this one, which is a real shame. It just kind of rattles around.The train itself is pretty well made, stays on the track, and can go forwards and backwards; as well as playing sound clips from the film, a nice chug chug sound, and steaming sound when it's stationary.Overall, giving it four stars. It's really expensive and the bell is awful, but the kids really love it",  # noqa: E501
                        "qa",
                    ],
                    [
                        "Really want to love this bag but The water leaking from the pipe after 2 hikes",  # noqa: E501
                        "seq2seq",
                    ],
                ],
                inputs=[text_input, model_input],
                fn=choosistant,
                outputs=[txt_predictions, txt_pred_id],
                cache_examples=False,
            )

        with gr.Tab("Examples B"):  # examples of bad predictions
            gr.Examples(
                examples=[
                    [
                        "I purchased these scissors as I have dexterity problems and find using normal scissors quite hard & painful to grip, these are excellent, they are easy to grip, they cut easily without having to exert too much pressure so they do not hurt my hands, plus they are super sharp so cut very easily.",  # noqa: E501
                        "qa",
                    ],
                    [
                        "Not sure if it’s because I bought from Amazon, but the formula is somewhat runny when trying to apply to lips. I have this in a different flavor and bought it at Sephora and the consistency is different. Still love it though, smells great!",  # noqa: E501
                        "seq2seq",
                    ],
                    [
                        "The scents are amazing however 3 of the oils lids were not on tight and they spilled in the package. The 3 oils were not full due to this problem. Also the packaging was all oily due to this. If this was a gift for someone I would be embarrassed.",  # noqa: E501
                        "qa",
                    ],
                    [
                        "Very easy to handle. Great on felt material and anything else. Very precise. Also durable.",  # noqa: E501
                        "qa",
                    ],
                ],
                inputs=[text_input, model_input],
                fn=choosistant,
                outputs=[txt_predictions, txt_pred_id],
                cache_examples=False,
            )
        with gr.Tab("Examples C"):  # examples of edge cases
            gr.Examples(
                examples=[
                    [
                        "Me acabaron de llegar, inicialmente me gustaron, diseño, sonido etc. Pero salí con ellos a la calle y el sonido se entrecorta me sentí frustrada porque pagar un precio elevado por algo así no me parece justo",  # noqa: E501
                        "seq2seq",
                    ],
                    [
                        "I had this unit professionally installed and immediately noticed the flow was incredibly slow, almost a trickle. I called aqua sauna and they told me to put a quarter underneath the filter because sometimes the filters are not cut right by the manufacturer. I had the plumber back and he did this and the flow was better but when he put the unit back together it started leaking even when the water was turned off under the cabinet. The plumber disconnected the unit.. I'll have to return it.. ugh",  # noqa: E501
                        "qa",
                    ],
                ],
                inputs=[text_input, model_input],
                fn=choosistant,
                outputs=[txt_predictions, txt_pred_id],
                cache_examples=False,
            )

    iface.launch(debug=True, server_port=8090)


main()
