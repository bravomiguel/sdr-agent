from langchain.chat_models import init_chat_model

from agent.prompts import MEMORY_UPDATE_INSTRUCTIONS
from agent.schemas import UserPreferences


def extract_interrupt_payload(response):
    """Extract the actual payload from an interrupt response, handling both Studio UI format (with interrupt ID wrapper) and direct format."""
    if not isinstance(response, dict):
        return response

    # Check if this looks like an interrupt ID wrapper
    if len(response) == 1:
        key = next(iter(response.keys()))

        # Check if the key looks like an interrupt ID (UUID-like format with hyphens)
        # Format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (36 chars total)
        if (len(key) == 36 and
            key.count('-') == 4 and
                all(c in '0123456789abcdef-' for c in key.lower())):
            # Extract the wrapped payload
            return response[key]

    # If not wrapped, return as-is
    return response


def get_memory(store, namespace, default_content=None):
    """Get memory from the store or initialize with default if it doesn't exist.

    Args:
        store: LangGraph BaseStore instance to search for existing memory
        namespace: Tuple defining the memory namespace, e.g. ("email_assistant", "triage_preferences")
        default_content: Default content to use if memory doesn't exist

    Returns:
        str: The content of the memory profile, either from existing memory or the default
    """
    # Search for existing memory with namespace and key
    user_preferences = store.get(namespace, "user_preferences")
    # how to get instructions from store for specific user id
    # store.get(("instructions", user_id), "writing_style_instructions")

    # If memory exists, return its content (the value)
    if user_preferences:
        return user_preferences.value

    # If memory doesn't exist, add it to the store and return the default content
    else:
        # Namespace, key, value
        store.put(namespace, "user_preferences", default_content)
        user_preferences = default_content

    # Return the default content
    return user_preferences


def update_memory(store, namespace, messages, model):
    """Update memory profile in the store.

    Args:
        store: LangGraph BaseStore instance to update memory
        namespace: Tuple defining the memory namespace, e.g. ("email_assistant", "triage_preferences")
        messages: List of messages to update the memory with
    """
    # Get the existing memory
    user_preferences = store.get(namespace, "user_preferences")
    # how to get instructions from store for specific user id
    # store.put(("instructions", user_id), "writing_style_instructions", new_memory.content)

    # Update the memory
    llm = init_chat_model(
        model, temperature=0.0).with_structured_output(UserPreferences)
    result = llm.invoke(
        [
            {"role": "system", "content": MEMORY_UPDATE_INSTRUCTIONS.format(
                current_profile=user_preferences.value, namespace=namespace)}
        ] + messages
    )
    # Save the updated memory to the store
    store.put(namespace, "user_preferences", result.user_preferences)
