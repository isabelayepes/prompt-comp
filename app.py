import gradio as gr

def process_input(input_text):
    # Your processing logic here
    return f"Processed: {input_text}"

with gr.Blocks() as demo:
    gr.Markdown("# Electric Prompt UI")
    
    with gr.Row():
        input_text = gr.Textbox(label="Input Prompt")
        output_text = gr.Textbox(label="Output")
        
    submit_btn = gr.Button("Process")
    submit_btn.click(
        fn=process_input,
        inputs=[input_text],
        outputs=[output_text]
    )

if __name__ == "__main__":
    demo.launch()