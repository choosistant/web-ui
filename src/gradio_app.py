import gradio as gr


def choosistant(review_text, procon="Benefits"):
    # waiting for model
    return "none yet" + " " + review_text


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

iface.launch(server_port=8090)
