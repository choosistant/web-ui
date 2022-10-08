import gradio as gr

def choosistant(review_text,procon='Benefits'):
  if procon == 'Benefits':
    return review_text[0:4]
  elif procon == 'Drawbacks':
    return review_text[-4:]
  else:
    return "Select whether to see either benefits or drawbacks of this product."

text_input = gr.Textbox(lines=8,placeholder="Enter the review text here...",label="Review Text")
new_title = gr.Textbox(label="Detected pro/con")
iface = gr.Interface(
    choosistant, [text_input, gr.Radio(['Benefits','Drawbacks'],label='Pros/Cons')],
    new_title,
    description ="Checkout some amazon reviews eg at [http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Musical_Instruments_5.json.gz](http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Musical_Instruments_5.json.gz)",
    allow_flagging="manual",
    flagging_options = ['Incorrect','Insufficient', 'Offensive', 'Other'],
    examples = [['The top side came ripped off','Drawbacks'],
                ['The gear is child friendly','Benefits']],
    )

iface.launch(server_port=8090)
