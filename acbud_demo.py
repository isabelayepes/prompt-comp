import gradio as gr
import time
import random  # For random delay

# ------------------------------------------------------------------------------
# Hardcoded prompts for Under the Hood Display (unchanged)
# ------------------------------------------------------------------------------
UNCOMPRESSED_PROMPT = """You are an AI accountability buddy designed to help users achieve their health and wellbeing goals. Your role is to provide support, guidance, and personalized recommendations based on the user's input and progress. You will be working with the following information:
<context_variables>
wish/goal: Lose 20 pounds in 6 months
outcome/visualization/motivation: Feeling confident and energetic in my favorite clothes
obstacles: Late-night snacking, sedentary job, lack of time for exercise
plan: 1. Replace evening snacks with herbal tea
2. Take a 15-minute walk during lunch break
3. Prepare healthy meals in advance for the week
4. Track daily calorie intake using a mobile app
</context_variables>
These context variables include:
•⁠ ⁠wish/goal: The user's primary goal or wish
•⁠ ⁠outcome/visualization/motivation: The user's desired outcome, visualization, or motivation
•⁠ ⁠obstacles: Potential challenges or obstacles in the way of achieving the goal
•⁠ ⁠plan: Approved actionable steps to achieve the goal
<timeline>
Last update to wish/goal: 2023-05-01 09:30:00
Last update to outcome/visualization/motivation: 2023-05-01 09:32:15
Last update to obstacles: 2023-05-01 09:35:45
Last update to plan: 2023-05-01 09:40:30
Current time and date: 2023-05-15 14:20:00
User's name: Sarah
</timeline>
The timeline variable contains:
•⁠ ⁠Time and date information for the most recent updates to context variables
•⁠ ⁠Current time and date
•⁠ ⁠User's name or nickname: Sarah
<cumulative_history>
2023-05-02, "If I see late-night cravings, I will drink herbal tea", effectiveness: moderate
2023-05-05, "If I feel too tired to cook, I will use pre-prepared healthy meals", effectiveness: high
2023-05-08, "If I can't take a walk during lunch, I will do desk exercises", effectiveness: low
2023-05-11, "If I'm tempted to skip tracking, I will log at least one meal", effectiveness: moderate
2023-05-14, "If I have a busy day, I will prioritize at least 10 minutes of exercise", effectiveness: high
</cumulative_history>
The cumulative history variable contains:
•⁠ ⁠Historical data on the effectiveness of previous plans
•⁠ ⁠Structured as: time/date, "if I see this (obstacle) I will do this (plan)", and corresponding effectiveness
When interacting with the user, follow these guidelines:
1.⁠ ⁠Initial interaction:
- If any context variables are empty, ask the user to provide the missing information.
- Use this format for requesting information:
<request_info>
[Specific question about missing context variable]
</request_info>
2.⁠ ⁠Follow-up interaction:
- Ask questions about the user's progress and any changes in their context.
- Use this format for follow-up questions:
<follow_up>
[Specific question about progress or changes]
</follow_up>
3.⁠ ⁠Updating context variables:
- Based on the user's responses, update the context variables.
- Use this format to confirm updates:
<context_update>
[Summary of updated context variables]
</context_update>
4.⁠ ⁠Suggesting and approving plans:
- Suggest small, actionable steps based on the user's goal and obstacles.
- Use this format for suggestions:
<suggested_plan>
[List of actionable steps]
</suggested_plan>
- Allow the user to modify and approve the plan.
- Once approved, update the plan context variable.
5.⁠ ⁠Handling disconnected timelines:
- If the goal variable is updated but other variables are not, identify this issue in your next interaction.
- Use this format to request updates:
<timeline_update_request>
I noticed that your goal has been updated, but other variables need to be aligned. Please provide updates for [list missing updates].
</timeline_update_request>
6.⁠ ⁠Analyzing historical progression:
- Use the cumulative history to recommend personalized, improved plans.
- Consider what has and hasn't worked for the user in the past.
- Use this format for personalized recommendations:
<personalized_recommendation>
Based on your history, I suggest: [Recommendation]
This is because: [Explanation based on past effectiveness]
</personalized_recommendation>
7.⁠ ⁠Maintaining a positive focus:
- Always use encouraging language and focus on progress towards health and wellbeing goals.
- Frame challenges as opportunities for growth.
8.⁠ ⁠Proactive messaging:
- When the app is opened, assume the user wants to engage with their accountability buddy.
- Use this format for proactive follow-up:
<proactive_followup>
Welcome back, <name>Sarah</name>! [Personalized question or encouragement based on their goal and recent progress]
</proactive_followup>
"""

COMPRESSED_PROMPT = """Health Accountability Buddy Prompt (Compressed)
Definitions
DEF: CV = Context Variables (goal, motivation, obstacles, plan) DEF: TL = Timeline info (update dates, current date, user name) DEF: CH = Cumulative History (past strategies and effectiveness) DEF: UN = Current user's name from TL (Sarah)
Role & Input Structure
You are a health/wellbeing accountability buddy providing personalized support based on:
<CV> wish/goal: Lose 20 pounds in 6 months outcome/visualization/motivation: Feeling confident and energetic in my favorite clothes obstacles: Late-night snacking, sedentary job, lack of time for exercise plan: 1. Replace evening snacks with herbal tea 2. Take a 15-minute walk during lunch break 3. Prepare healthy meals in advance for the week 4. Track daily calorie intake using a mobile app </CV> <TL> Last update to wish/goal: 2023-05-01 09:30:00 Last update to outcome/visualization/motivation: 2023-05-01 09:32:15 Last update to obstacles: 2023-05-01 09:35:45 Last update to plan: 2023-05-01 09:40:30 Current time and date: 2023-05-15 14:20:00 User's name: Sarah </TL> <CH> 2023-05-02, "If I see late-night cravings, I will drink herbal tea", effectiveness: moderate 2023-05-05, "If I feel too tired to cook, I will use pre-prepared healthy meals", effectiveness: high 2023-05-08, "If I can't take a walk during lunch, I will do desk exercises", effectiveness: low 2023-05-11, "If I'm tempted to skip tracking, I will log at least one meal", effectiveness: moderate 2023-05-14, "If I have a busy day, I will prioritize at least 10 minutes of exercise", effectiveness: high </CH>
Interaction Protocols
Use these tags for different interaction types:
Missing Info → <request_info>[Question about missing CV]</request_info>


Progress Check → <follow_up>[Question about progress/changes]</follow_up>


Update Confirmation → <context_update>[Summary of updated CV]</context_update>


Plan Creation → <suggested_plan>[Actionable steps]</suggested_plan>


Timeline Alignment → <timeline_update_request>Goal updated but other variables need alignment. Please update [missing items].</timeline_update_request>


Historic Analysis → <personalized_recommendation>Based on history: [Recommendation] Because: [Explanation from CH effectiveness]</personalized_recommendation>


Welcome Message → <proactive_followup>Welcome back, UN! [Personalized encouragement based on goal/progress]</proactive_followup>


Core Guidelines
Maintain positive, encouraging tone
Frame challenges as growth opportunities
Analyze CH to prioritize strategies marked "high" effectiveness
Suggest small, actionable steps aligned with user's goal and obstacles
Allow user modification before plan approval
When app opens, assume user wants engagement
"""

# Compute word counts for Under the Hood tab
uncompressed_word_count = len(UNCOMPRESSED_PROMPT.split())
compressed_word_count = len(COMPRESSED_PROMPT.split())

# ------------------------------------------------------------------------------
# Conversation Simulation Functions (Sequential Turn-by-Turn, No Labels)
# ------------------------------------------------------------------------------

def start_journey(name, goal, outcome, obstacles, plan, conv_state):
    """
    Starts the conversation if not already active.
    The conversation state is a dictionary containing:
      - "sim_messages": a list of simulated assistant messages (hardcoded)
      - "sim_index": pointer for the next assistant message
      - "chat_history": list of messages as tuples:
           (user message or None, assistant message or None)
    The assistant's first message is displayed immediately on the left.
    """
    if conv_state and isinstance(conv_state, dict) and conv_state.get("chat_history"):
        # Conversation already active; return a system message.
        return conv_state, [("", "Your accountability session is already active. Please continue with your conversation.")]
    
    sim_messages = [
        "Welcome back, {name}! It's been two weeks since you set your goal to {goal}. I'm excited to see how you've been implementing your plan! I notice you've been testing different strategies, and it looks like pre-prepared healthy meals and prioritizing at least 10 minutes of exercise—even on busy days—have been working really well for you. How are you feeling about your progress so far?",
        "How has the herbal tea strategy been working for your late-night snacking? Are you finding it easier to resist those cravings now?",
        "I see your desk exercises weren't as effective. Would you like to explore other strategies to keep healthy that might better suit your sedentary job?",
        "Based on your history, I'd suggest continuing to prioritize meal prep on weekends since using pre-prepared healthy meals when tired has been highly effective for you. This strategy addresses both your lack-of-time obstacle and helps manage your calorie intake. Why don't we try out that strategy going forward?",
        "Ok! I'll check in after a bit! You're doing great!"
    ]
    # Replace placeholders with actual values
    sim_messages = [msg.format(name=name, goal=goal) for msg in sim_messages]
    # Initialize chat history with the first assistant message on the left.
    chat_history = [(None, sim_messages[0])]
    new_conv_state = {
        "info": f"Name: {name}; Goal: {goal}; Outcome: {outcome}; Obstacles: {obstacles}; Plan: {plan}",
        "sim_index": 1,            # next assistant message index
        "sim_messages": sim_messages,
        "chat_history": chat_history,
    }
    return new_conv_state, chat_history

def interact(user_msg, conv_state):
    """
    Handles a subsequent turn:
      1. Appends the user's message (displayed on the right) and then,
      2. Waits a random time (between 0.8 and 1.2 seconds) before appending the next assistant message (if available, on the left).
      3. Clears the user input box.
    """
    if not conv_state or not isinstance(conv_state, dict):
        return conv_state, [("", "Please click 'Accountability Now!' under the About You section to start your journey.")], ""
    
    # Append user's message as (user message, None) so it renders on the right.
    conv_state["chat_history"].append((user_msg, None))
    # Wait a random delay
    time.sleep(random.uniform(0.8, 1.2))
    if conv_state["sim_index"] < len(conv_state["sim_messages"]):
        next_msg = conv_state["sim_messages"][conv_state["sim_index"]]
        conv_state["chat_history"].append((None, next_msg))
        conv_state["sim_index"] += 1
    # Return the updated conversation state, chat history and an empty string to clear the user message textbox.
    return conv_state, conv_state["chat_history"], ""

# ------------------------------------------------------------------------------
# Gradio UI Setup
# ------------------------------------------------------------------------------
with gr.Blocks() as demo:
    gr.Markdown("# Acbud: Your AI Accountability Buddy")
    
    with gr.Tabs():
        # ======== Chat Tab ========
        with gr.TabItem("Chat"):
            gr.Markdown("### About you")
            with gr.Column():
                user_name = gr.Textbox(
                    label="Your Name", 
                    value="Sarah",
                    placeholder="Enter your name (e.g. Sarah)"
                )
                user_goal = gr.Textbox(
                    label="Your Goal/Wish", 
                    value="Lose 20 pounds in 6 months",
                    placeholder="Enter your primary goal"
                )
                user_outcome = gr.Textbox(
                    label="Desired Outcome/Motivation", 
                    value="Feeling confident and energetic in my favorite clothes",
                    placeholder="Enter your desired outcome or motivation"
                )
                user_obstacles = gr.Textbox(
                    label="Obstacles",
                    value="Late-night snacking, sedentary job, lack of time for exercise",
                    placeholder="Enter potential obstacles"
                )
                plan_text = gr.Textbox(
                    label="Current Plan",
                    value=("1. Replace evening snacks with herbal tea\n"
                           "2. Take a 15-minute walk during lunch break\n"
                           "3. Prepare healthy meals in advance\n"
                           "4. Track daily calorie intake in a mobile app"),
                    lines=4,
                    placeholder="Your current actionable plan"
                )
                start_btn = gr.Button("Accountability Now!")
            
            # Hidden state to maintain conversation (dictionary)
            conversation_state = gr.State({})
            
            # Chatbot component (no labels on the bubbles)
            chatbot = gr.Chatbot()
            
            with gr.Column():
                user_message = gr.Textbox(label="Your Message", placeholder="Type your message here...")
                submit_btn = gr.Button("Submit")
            
            # Start the journey: show first assistant message; store conversation state
            start_btn.click(
                start_journey,
                inputs=[user_name, user_goal, user_outcome, user_obstacles, plan_text, conversation_state],
                outputs=[conversation_state, chatbot]
            )
            
            # Handle subsequent interaction: add user's message, wait, then add assistant message, and clear user input
            submit_btn.click(
                interact,
                inputs=[user_message, conversation_state],
                outputs=[conversation_state, chatbot, user_message]
            )
        
        # ======== Under the Hood Tab ========
        with gr.TabItem("Under the Hood"):
            gr.Markdown("## Prompt Compression Details")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Original Uncompressed Prompt")
                    gr.Markdown(f"**Word Count:** {uncompressed_word_count}")
                    uncompressed_display = gr.HTML(value=f"<pre>{UNCOMPRESSED_PROMPT}</pre>")
                with gr.Column():
                    gr.Markdown(
                        "<div style='text-align: center; font-size: 36px; margin-top: 40px;'>"
                        "➡<br/><i>Compression</i>"
                        "</div>"
                    )
                with gr.Column():
                    gr.Markdown("### Compressed Prompt")
                    gr.Markdown(f"**Word Count:** {compressed_word_count}")
                    compressed_display = gr.HTML(value=f"<pre>{COMPRESSED_PROMPT}</pre>")

demo.launch()
