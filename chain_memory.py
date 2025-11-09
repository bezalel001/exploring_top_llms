from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from dotenv import load_dotenv
from rich.markdown import Markdown
from rich.console import Console
load_dotenv('.env')
console = Console()

# prepare model
llm = ChatOpenAI(model="gpt-5-nano", temperature=0.7)

# session history
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


# Begin the story
initial_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a creative stroryteller. Based on the following context and plyer's choice, continue and provide three different paths for the story to proceed. Keep the story extremely short and concise. Create an opening scene for an adventure story {place} and provide three different paths for the player to choose from."),
])

context_chain = initial_prompt | llm

# setup up a Runnable with message history, which allows you to add the history of messages in the conversation to the chain
config = {"configurable": {"session_id": "03"}}

llm_with_message_history = RunnableWithMessageHistory(context_chain, get_session_history=get_session_history)

context = llm_with_message_history.invoke({"place": "in a mystical forest"}, config=config)

console.print(Markdown(context.content))

# enable user choice mechanism
def process_player_choice(choice: str, config):
    response = llm_with_message_history.invoke([
        ("user", f"Continue the story based on the player's choice: {choice}"),
        ("system", "Provide three different paths for the story to proceed based on the player's choice."),
    ], config=config)
    return response


# Game loop e
while True:
    #  get player choice
    player_choice = input("Enter your choice (or 'exit' to quit): ")
    if player_choice.lower() == 'exit':
        break
    # continue the story based on player choice
    context = process_player_choice(player_choice, config=config)
    console.print(Markdown(context.content))