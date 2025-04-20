import gradio as gr
from anthropic import Anthropic
from dotenv import load_dotenv
import os

# Load environment variables (ANTHROPIC_API_KEY should be set in your .env file)
load_dotenv()

# Initialize the Anthropic client; it will automatically use the API key from the environment
client = Anthropic()

# ------------------------------------------------------------------------------
# P0 Template and Compression Prompt (C)
# ------------------------------------------------------------------------------
P0_TEMPLATE = """You are an AI accountability buddy designed to help users achieve their health and wellbeing goals. Your role is to provide support, guidance, and personalized recommendations based on the user's input and progress. You will be working with the following information:

<context_variables>
wish/goal: {goal}
outcome/visualization/motivation: {outcome}
obstacles: {obstacles}
plan: <if empty, suggest plans>
</context_variables>

These context variables include:
•⁠ wish/goal: The user's primary goal or wish
•⁠ outcome/visualization/motivation: The user's desired outcome, visualization, or motivation
•⁠ obstacles: Potential challenges or obstacles in the way of achieving the goal
•⁠ plan: Approved actionable steps to achieve the goal

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

C = """<prompt> # Meta Prompt for Prompt Compression
You are a prompt compression specialist. Your task is to compress the input prompt using hierarchical structuring and dictionary reference techniques while preserving all functional requirements and essential instructions.
Compression Instructions
1. Apply Dictionary References:
    * Identify recurring concepts, formats, and instructions
    * Create abbreviations/codes with DEF: prefix (e.g., "DEF: XYZ = detailed explanation here")
    * Replace repetitive content with these references
2. Implement Hierarchical Structure:
    * Organize information into logical categories and subcategories
    * Use headers, subheaders, and indentation to show relationships
    * Group related concepts to reduce redundancy
3. Preserve Essential Elements:
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
* Reduce length by approximately 40-60% while maintaining full functionality
Remember: The compressed prompt will be used directly with an AI system with no additional context or information, so it must be complete and self-contained. </prompt>"""

# ------------------------------------------------------------------------------
# Revised API call using Anthropic SDK
# ------------------------------------------------------------------------------
def call_claude_api(prompt, model="claude-3-haiku-20240307", max_tokens=300, temperature=0):
    """
    Calls the Anthropic Claude API using the official SDK.
    The client automatically uses your API key from the environment.
    """
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system="You are an expert in facilitating conversations for an accountability buddy.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        return f"API call error: {e}"

# ------------------------------------------------------------------------------
# Conversation processing functions
# ------------------------------------------------------------------------------

def initial_turn_custom(goal, outcome, obstacles):
    """
    For the first interaction:
    - Uses user-provided goal, outcome, and obstacles to fill the P0 template.
    - Sends the customized prompt to Claude to obtain the initial bot output (O₀).
    - Returns the full conversation state (customized P0 + O₀) and O₀.
    """
    P0_custom = P0_TEMPLATE.format(goal=goal, outcome=outcome, obstacles=obstacles)
    bot_output = call_claude_api(P0_custom)
    conversation = P0_custom + "\n" + bot_output
    return conversation, bot_output

def next_turn(user_input, conversation):
    """
    For subsequent interactions:
    1. Concatenate the current conversation state with the user's input.
    2. Prepend the compression prompt (C) to produce a combined prompt.
    3. Call the Claude API with the combined prompt to compress/update the context.
    4. Use the new context to generate the bot's next response.
    5. Return the updated conversation state and bot response.
    """
    combined = conversation + "\n" + user_input
    compression_input = C + "\n" + combined
    new_context = call_claude_api(compression_input)
    bot_response = call_claude_api(new_context)
    updated_conversation = new_context + "\n" + bot_response
    return updated_conversation, bot_response

# ------------------------------------------------------------------------------
# Gradio UI Setup
# ------------------------------------------------------------------------------

with gr.Blocks() as demo:
    gr.Markdown("# Acbud: Your AI Accountability Buddy")
    gr.Markdown("This app uses Anthropic Claude as an accountability buddy. Your API key should be set in your environment (ANTHROPIC_API_KEY).")
    
    with gr.Column():
        gr.Markdown("## Tell us about yourself")
        user_goal = gr.Textbox(label="Your Goal/Wish", placeholder="Enter your primary goal")
        user_outcome = gr.Textbox(label="Desired Outcome/Motivation", placeholder="Enter your desired outcome or motivation")
        user_obstacles = gr.Textbox(label="Obstacles", placeholder="Enter potential obstacles")
        start_btn = gr.Button("Start my accountability journey")
    
    # Hidden variable to maintain the conversation state
    conversation_state = gr.State("")
    
    # Chat display: a list of (speaker, message) tuples
    chatbot = gr.Chatbot()
    
    # Input textbox and submit button for subsequent messages
    user_message = gr.Textbox(label="Your Message", placeholder="Type here...")
    submit_btn = gr.Button("Submit")
    
    def start_journey(goal, outcome, obstacles):
        """
        Initializes the conversation using the custom P0 template with user inputs.
        Returns the conversation state and displays the initial bot output.
        """
        conv_state, bot_msg = initial_turn_custom(goal, outcome, obstacles)
        chat_history = [("Acbud", bot_msg)]
        return conv_state, chat_history
    
    def interact(user_msg, conv_state):
        """
        Processes a subsequent turn.
        If the conversation has been started, it appends the new user input,
        updates the conversation state via next_turn(), and returns the bot response.
        If no conversation state is present, prompts the user to start the journey first.
        """
        if not conv_state:
            return conv_state, [("System", "Please start your journey by entering your details and clicking the 'Start my accountability journey' button.")]
        conv_state, bot_msg = next_turn(user_msg, conv_state)
        chat_history = [(f"User", user_msg), ("Acbud", bot_msg)]
        return conv_state, chat_history
    
    # Wire up the buttons with their callbacks.
    start_btn.click(
        start_journey,
        inputs=[user_goal, user_outcome, user_obstacles],
        outputs=[conversation_state, chatbot]
    )
    
    submit_btn.click(
        interact,
        inputs=[user_message, conversation_state],
        outputs=[conversation_state, chatbot]
    )

demo.launch()
