from dotenv import load_dotenv  
import os
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()  # Load environment variables from .env file

@tool
def check_transaction(transaction_id):
    """Check the status of a transaction."""
    mock_transactions = {
        "txn_123": {"status": "success", "reason": "completed" } ,
        "txn_456": {"status": "pending","reason": "Insufficient balance"},
        "txn_789": {"status":"failed", "reason": "Insufficient balance"}
    }
    txn = mock_transactions.get(transaction_id)
    if txn:
        return f"The transaction status is {txn['status']}. The reason is: {txn['reason']}."
    else:
        return "Transaction not found in the database."

tools = [check_transaction]

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

memory = MemorySaver()

system_prompt = (
    "You are Adura, the NMobile Support Agent. "
    "You help users troubleshoot failed transactions. "
    "Always ask for a Transaction ID first if the user reports an issue. "
    "Explain technical failure reasons in simple, empathetic terms."
)

# agent = create_agent(llm, tools, prompt)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are Adura, the NMobile Support Agent. Help users troubleshoot failed transactions. "
        "Always ask for a Transaction ID first. Explain technical reasons simply."
    ),
    checkpointer=memory
)
# store = {}

# def get_session_history(session_id):
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory()
#     return store[session_id]

# agent_with_history = RunnableWithMessageHistory(agent_executor, get_session_history, input_messages_key="input", history_messages_key="chat_history")
