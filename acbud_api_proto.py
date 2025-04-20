import gradio as gr
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()
client = Anthropic()

# ------------------------------------------------------------------------------
# P0 Template and Compression Prompt (C)
# ------------------------------------------------------------------------------
P0_TEMPLATE = """You are an AI accountability buddy designed to help users achieve their health and wellbeing goals. 
Your role is to provide support, guidance, and personalized recommendations based on the user's input and progress.
If the plans tags are empty and the desired-action tags say: [Suggest an initial plan], 
then it is the first session and you must suggest self improvement plans based on the other information you have about the user.

<desired-action>[Suggest an initial plan]</desired-action>

<context_variables>
    <goal>{goal}</goal>
    <motivation>{outcome}</motivation>
    <obstacles>{obstacles}</obstacles>
    <plans></plans>
</context_variables>

These context variables include:
•⁠ wish/goal: The user's primary goal or wish
•⁠ outcome/visualization/motivation: The user's desired outcome, visualization, or motivation
•⁠ obstacles: Potential challenges or obstacles in the way of achieving the goal
•⁠ plans: Approved actionable steps to achieve the goal

<timeline></timeline>

The timeline variable contains:
•⁠ Time and date information for the most recent updates to context variables
•⁠ Current time and date

<cumulative_history></cumulative_history>

The cumulative history variable contains:
•⁠ Historical data on the effectiveness of previous plans
•⁠ Structured as: time/date, "if I see this (obstacle) I will do this (plan)", and corresponding effectiveness

When interacting with the user, follow these guidelines:

1. Initial interaction:
   - If any context variables are empty, ask the user to provide the missing information.
   - Use this format for requesting information:
     <request_info>
     [Specific question about missing context variable]
     </request_info>

2. Follow-up interaction:
   - Ask questions about the user's progress and any changes in their context.
   - Use this format for follow-up questions:
     <follow_up>
     [Specific question about progress or changes]
     </follow_up>

3. Updating context variables:
   - Based on the user's responses, update the context variables.
   - Use this format to confirm updates:
     <context_update>
     [Summary of updated context variables]
     </context_update>

4. Suggesting and approving plans:
   - Suggest small, actionable steps based on the user's goal and obstacles.
   - Use this format for suggestions:
     <suggested_plan>
     [List of actionable steps]
     </suggested_plan>
   - Allow the user to modify and approve the plan.
   - Once approved, update the plan context variable.

5. Handling disconnected timelines:
   - If the goal variable is updated but other variables are not, identify this issue in your next interaction.
   - Use this format to request updates:
     <timeline_update_request>
     I noticed that your goal has been updated, but other variables need to be aligned. Please provide updates for [list missing updates].
     </timeline_update_request>

6. Analyzing historical progression:
   - Use the cumulative history to recommend personalized, improved plans.
   - Consider what has and hasn't worked for the user in the past.
   - Use this format for personalized recommendations:
     <personalized_recommendation>
     Based on your history, I suggest: [Recommendation]
     This is because: [Explanation based on past effectiveness]
     </personalized_recommendation>

7. Maintaining a positive focus:
   - Always use encouraging language and focus on progress towards health and wellbeing goals.
   - Frame challenges as opportunities for growth.

8. Proactive messaging:
   - When the app is opened, assume the user wants to engage with their accountability buddy.
   - Use this format for proactive follow-up:
     <proactive_followup>
     Welcome back, <name></name>! [Personalized question or encouragement based on their goal and recent progress]
     </proactive_followup>"""

C = """<prompt> # Meta Prompt for Prompt Concatenation and Compression
You are the prompt context updater and prompt compression specialist for the accountability buddy's prompt. 
You must update the original prompt with the new information, particularly where tags are missing information. 
Based on the user's response, update context contained within the relevant tags. 
Remember the goal is for the next accountability buddy to be able to follow up.
You must also compress the input prompt using hierarchical structuring and dictionary reference techniques below while preserving all functional requirements and essential instructions. 

Compression Instructions
1. Apply Dictionary References:
    * Identify recurring concepts, formats, and instructions
    * Create abbreviations/codes with DEF: prefix (e.g., "DEF: XYZ = detailed explanation here")
    * Replace repetitive content with these references
2. Implement Hierarchical Structure:
    * Organize information into logical categories and subcategories
    * Use headers, subheaders, and indentation to show relationships
    * Group related concepts to reduce redundancy
3. Preserve Old and Add New Essential Elements:
    * Maintain all critical instructions that affect functionality
    * Keep all required data structures, tags, and formatting specifications
    * Ensure the compressed prompt produces identical outputs to the original
4. Optimize for Clarity:
    * Use concise language and remove unnecessary words
    * Convert paragraphs to bullet points where appropriate
    * Maintain readability for humans while compressing

Output Format
The compressed prompt should:
* Begin and end with <prompt> tags
* Include a brief heading identifying it as a compressed version
* Preserve all functional XML tags from the original prompt
* Organize information using # and ## markdown headers
* Present the compression with clear visual hierarchy
* Reduce length as possible while maintaining full functionality
Remember: The compressed prompt will be used directly with an AI system with no additional context or information, so it must be complete and self-contained. </prompt>"""

# ------------------------------------------------------------------------------
# Revised API call using Anthropic SDK
# ------------------------------------------------------------------------------

def call_claude_api(prompt, model="claude-3-7-sonnet-20250219", max_tokens=2000, temperature=0.1):
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system="This is part of an accountability buddy chat service.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"API call error: {e}"

# ------------------------------------------------------------------------------
# Conversation processing functions
# ------------------------------------------------------------------------------

def initial_turn_custom(goal, outcome, obstacles):
    P0_custom = P0_TEMPLATE.format(goal=goal, outcome=outcome, obstacles=obstacles)
    bot_output = call_claude_api(P0_custom)
    internal_context = P0_custom
    combined = f"{P0_custom}\nAssistant's output: {bot_output}"
    return internal_context, bot_output, combined

def extract_cleaned_compressed_prompt(model_output):
    """
    Extracts the cleaned prompt by removing everything before the first <prompt> tag.
    Returns the full <prompt> block, or a fallback message if not found.
    """
    tag = "<prompt>"
    idx = model_output.find(tag)
    if idx != -1:
        return model_output[idx:].strip()
    else:
        # Fall back if the model didn't format correctly
        return "(<compressed prompt>" + model_output.strip()

def next_turn(user_input, internal_context):
    combined_uncompressed = internal_context + "\nUser's input: " + user_input
    compression_input = C + "\n" + combined_uncompressed
    compressed_context_response = call_claude_api(compression_input)

    cleaned_compressed_context = extract_cleaned_compressed_prompt(compressed_context_response)

    bot_response = call_claude_api(cleaned_compressed_context)

    combined_uncompressed += f"\nAssistant's output: {bot_response}"

    return cleaned_compressed_context, bot_response, combined_uncompressed, compressed_context_response


# -------------------------
# Gradio UI Definition here
# -------------------------

with gr.Blocks() as demo:
    gr.Markdown("# Acbud: Your AI Accountability Buddy")
    gr.Markdown("Set your ANTHROPIC_API_KEY in your environment.")

    with gr.Column():
        gr.Markdown("## Tell us about yourself")
        user_goal = gr.Textbox(label="Your Goal/Wish", placeholder="Enter your primary goal")
        user_outcome = gr.Textbox(label="Desired Outcome/Motivation", placeholder="Enter your desired outcome")
        user_obstacles = gr.Textbox(label="Obstacles", placeholder="Enter potential obstacles")
        start_btn = gr.Button("Accountability now!")

    internal_context_state = gr.State("")
    chatbot = gr.Chatbot(type="messages")

    user_message = gr.Textbox(label="Your Message", placeholder="Type here...")
    submit_btn = gr.Button("Submit Message")

    with gr.Tab("Under the Hood"):
        gr.Markdown("## Prompt Compression Details")

        with gr.Row():
            with gr.Column():
                word_count_uncompressed = gr.Markdown("**Word Count:** 0")
                P_i_display = gr.Textbox(label="Uncompressed Prompt (Pᵢ + Oᵢ + Iᵢ)", lines=15, interactive=False)

            with gr.Column():
                gr.Markdown(
                    "<div style='text-align: center; font-size: 36px; margin-top: 40px;'>"
                    "➡<br/><i>Compression</i></div>"
                )

            with gr.Column():
                word_count_compressed = gr.Markdown("**Word Count:** 0")
                P_prime_i_display = gr.Textbox(label="Compressed Prompt C(Pᵢ+Oᵢ+Iᵢ)", lines=15, interactive=False)

    def update_word_counts(uncompressed, compressed):
        uncompressed_count = len(uncompressed.split())
        compressed_count = len(compressed.split())
        return (f"**Word Count:** {uncompressed_count}",
                f"**Word Count:** {compressed_count}")

    # Define interactions
    def start_journey(goal, outcome, obstacles):
        internal_context, bot_msg, combined_uncompressed = initial_turn_custom(goal, outcome, obstacles)
        chat_history = [{"role": "assistant", "content": bot_msg}]
        compressed_initial = "(Not compressed yet)"
        counts = update_word_counts(combined_uncompressed, compressed_initial)
        return internal_context, chat_history, combined_uncompressed, compressed_initial, *counts
    
    def interact(user_msg, internal_context):
        cleaned_compressed_context, bot_msg, combined_uncompressed, compressed_context = next_turn(user_msg, internal_context)
        chat_history = [
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": bot_msg}
        ]
        counts = update_word_counts(combined_uncompressed, compressed_context)
        
        return (cleaned_compressed_context, chat_history, combined_uncompressed, compressed_context, *counts, "")

    # Wire up buttons
    start_btn.click(
        start_journey,
        inputs=[user_goal, user_outcome, user_obstacles],
        outputs=[internal_context_state, chatbot, P_i_display, P_prime_i_display, word_count_uncompressed, word_count_compressed]
    )

    submit_btn.click(
        interact,
        inputs=[user_message, internal_context_state],
        outputs=[
            internal_context_state,
            chatbot,
            P_i_display,
            P_prime_i_display,
            word_count_uncompressed,
            word_count_compressed,
            user_message  # <-- clears this textbox after submission
        ]
    )


demo.launch()