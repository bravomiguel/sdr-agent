
from langgraph.graph import START, END, StateGraph
from agent.configuration import Configuration
from agent.state import InputState, State


from datetime import datetime
from langchain_core.runnables import RunnableConfig
from agent.prompts import SYSTEM_PROMPT
from agent.tools import SEND_EMAIL
from langchain.chat_models import init_chat_model
from agent.schemas import EmailContentSchema
from langgraph.types import interrupt
from typing import Literal


from agent.utils import extract_interrupt_payload

# Initialize LLM
# llm = init_chat_model("openai:gpt-4o-mini", temperature=0.0)
llm = init_chat_model("groq:llama-3.3-70b-versatile", temperature=0.0)
llm_router = llm.with_structured_output(EmailContentSchema)

# Define nodes


def generate_email(state: State, config: RunnableConfig):
    """Use llm to generate email content."""
    prospect_info = state.prospect_info
    sdr_name = 'Walt Boxwell'
    email_preferences = 'Keep tone professional yet friendly'
    feedback = state.feedback

    messages = state.messages

    system_message = {"role": "system", "content": SYSTEM_PROMPT.format(
        prospect_info=prospect_info,
        sdr_name=sdr_name,
        email_preferences=email_preferences,
        system_time=datetime.now().isoformat()
    )}

    user_messages = []
    if feedback:
        user_messages.append({
            "role": "user", "content": f"FEEDBACK: {feedback}"})

    user_messages.append(
        {"role": "user", "content": "Generate email subject and body."})

    result = llm_router.invoke([system_message] + messages + user_messages)

    ai_message = {
        "role": "ai", "content": f"Subject: {result.subject}\n\n Email body: {result.body}"}

    return {
        "messages": user_messages + [ai_message],
        "email_content": result,
        "feedback": None
    }


def send_email(state: State, config: RunnableConfig):
    """Send or reject email, or provide feedback based on user response."""
    prospect_info = state.prospect_info
    email_content = state.email_content

    raw_response = interrupt(
        {
            "question": "Ready to send?",
            "to": prospect_info.email,
            "subject": email_content.subject,
            "body": email_content.body
        }
    )

    response = extract_interrupt_payload(raw_response)

    # Debug: Print both formats for comparison
    # print(f"Raw response: {raw_response}")
    # print(f"Extracted response: {response}")

    new_state = state

    if response['type'] == 'accept':
        observation = SEND_EMAIL.invoke(
            {
                "to": prospect_info.email,
                "subject": email_content.subject,
                "body": email_content.body
            }
        )

        new_state = {
            "messages": [{"role": "ai", "content": observation}]
        }
    elif response['type'] == 'reject':
        new_state = {
            "messages": [{"role": "ai", "content": "Email rejected by the user."}],
        }
    elif response['type'] == 'feedback':
        feedback = response.get("feedback")

        new_state = {
            "email_content": None,
            "feedback": feedback
        }

    # Catch all other responses
    else:
        raise ValueError(f"Invalid response: {response}")

    return new_state

# Define routing after send email


def route_after_send_email(state: State) -> Literal["generate_email", "__end__"]:
    """Route to end or back to llm if feedback provided."""
    if state.feedback:
        return "generate_email"
    else:
        return END


# Define a new graph
builder = StateGraph(State, input=InputState, config_schema=Configuration)

# Define the nodes
builder.add_node("generate_email", generate_email)
builder.add_node("send_email", send_email)

# Set the edges
builder.add_edge(START, "generate_email")
builder.add_edge("generate_email", "send_email")
builder.add_conditional_edges("send_email", route_after_send_email)

# Compile the builder into an executable graph
graph = builder.compile(name="SDR Agent")
