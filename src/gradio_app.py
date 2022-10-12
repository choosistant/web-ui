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
        type_plural="drawbacks",
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
    flagging_handler = FlaggingHandler()
    text_input = gr.Textbox(
        lines=8, placeholder="Enter the review text here...", label="Review Text"
    )

    example_url = f"<a href='https://www.amazon.com/b?node=16225007011&pf_rd_r=SVC6K7QE0WNT3575Q2VJ&pf_rd_p=6b30eb15-a900-4294-9772-db8876444356&pd_rd_r=c2a147e6-37bf-41be-ba8b-826e1a45ad4c&pd_rd_w=3WOVP&pd_rd_wg=rWeT0&ref_=pd_gw_unk'>{'this page'}</a>"
    with gr.Blocks() as iface:
        gr.Markdown(f"Checkout some amazon reviews eg at {example_url}")
        text_input = gr.Textbox(
            lines=8, placeholder="Enter the review text here...", label="Review Text"
        )
        text_button = gr.Button("Submit")
        txt_pred_id = gr.Textbox(label="ID", visible=False)
        txt_predictions = gr.HighlightedText(label="Predictions", combine_adjacent=True)
        txt_predictions.style(color_map={"drawback": "red", "benefit": "green"})

        text_button.click(
            choosistant, inputs=[text_input], outputs=[txt_predictions, txt_pred_id]
        )
        with gr.Row():
            btn_incorrect = gr.Button("Flag as incorrect")
            btn_insufficient = gr.Button("Flag as insufficient")
            btn_other = gr.Button("Flag as other")
        flagging_handler.setup(
            components=[text_input, txt_predictions, txt_pred_id],
            flagging_dir="data/flagged",
        )

        btn_incorrect.click(
            lambda *args: flagging_handler.flag(
                flag_data=args, flag_option="Incorrect"
            ),
            [text_input, txt_predictions, txt_pred_id],
            None,
            preprocess=False,
        )
        btn_insufficient.click(
            lambda *args: flagging_handler.flag(
                flag_data=args, flag_option="Insufficient"
            ),
            [text_input, txt_predictions, txt_pred_id],
            None,
            preprocess=False,
        )
        btn_other.click(
            lambda *args: flagging_handler.flag(flag_data=args, flag_option="Other"),
            [text_input, txt_predictions, txt_pred_id],
            None,
            preprocess=False,
        )

        with gr.Tab("Examples A"):
            gr.Examples(
                examples=[
                    [
                        "I purchased this harddrive to backup my other harddrives. It just crashed on me & I am currently on the phone trying about to be charged thousands of dollars to get data recovery on something I haven't even had for 6 months. DO NOT PURCHASE. Its cheap & faulty. Horrible quality and very sensitive. I did not drop it anywhere or damage it in any way. It just sat on my desk"
                    ],
                    [
                        "Expensive, but I think it's the only legit Polar Express train set available, and the kids love Polar Express; what can you do?The track you get with the train makes a small oval shape, and is pretty easy to fit together. Slightly easier than Lego, but harder than Trackmaster stuff.The bell that comes with the train is really bad, we've had cat toys which resembled a bell better than this one, which is a real shame. It just kind of rattles around.The train itself is pretty well made, stays on the track, and can go forwards and backwards; as well as playing sound clips from the film, a nice chug chug sound, and steaming sound when it's stationary.Overall, giving it four stars. It's really expensive and the bell is awful, but the kids really love it"
                    ],
                ],
                inputs=[text_input],
                fn=choosistant,
                outputs=[txt_predictions, txt_pred_id],
                cache_examples=True,
            )

        with gr.Tab("Examples B"):
            gr.Examples(
                examples=[
                    [
                        "Not sure why I jumped on the bandwagon and got this. After seeing the price of the bottle of gel that you have to use with it, I knew I had been had. Now even that ~$25 bottle of gel is no longer available on Amazon -- its replacement is almost twice as expensive. Nuface says you cannot use Aloe Vera or anything else, you must use their product for the best results. Anyway, after using this ~1 month, I packed it away.Definitely do not recommend"
                    ],
                    [
                        "Okay so FIRST the mounting process is a… PROCESS. the included template is helpful but the line in the middle of the template is NOT center.Be glad I saved you that headache.The other thing you need to know is the additional OEM frames are a bit of a nightmare. I was able to score the tv + frame for $999 together on Black Friday and I’m so glad I did because paying $150~ ish dollars for the plastic frames is really annoying when you discover that the poor packaging design means they arrive broken!! Go look at the reviews for the optional Samsung frames. If you’re patient and deal with the returns and reorder until it’s right it will work out but you’ve been warned okay?Alright all that aside the TV is gorgeous.\nI’m so happy with it. Picture quality is good my only complaint is that the screen should be more anti-reflective. It’s not as reflective as straight glass but with any lamps or windows you might be annoyed by the glare If you’re a design snob/observant enough in the first place to be looking at this tv. Regardless of the glare and the stupid overpriced bezels (which IMO are completely necessary if you want this tv since the whole point is to look like a frame) I would still repurchase because it’s just stunning to look at.Also the art subscription- just don’t.There’s not enough art to warrant $5 a month and you can upload your own pictures (of artwork that you can find on google for FREE) to the TV via the smart things app.They’ve shorted the free subscription to ONE month with a new tv purchase and it’s still not worth it. Just google your favorite art, save it in a high quality resolution and voilà."
                    ],
                ],
                inputs=[text_input],
                fn=choosistant,
                outputs=[txt_predictions, txt_pred_id],
                cache_examples=True,
            )

    iface.launch(debug=True, server_port=8090)


main()
