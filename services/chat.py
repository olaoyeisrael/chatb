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
import requests
from langchain_core.runnables import RunnableConfig


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


@tool
def check_balance():
    """Check balance"""
    pass

@tool
def get_transaction_history():
    """check transaction history"""
    pass


@tool
def buy_airtime(config: RunnableConfig, phone_number, network, amount):
    """Buy airtime"""
    api_url = "https://dashboard.nmobile.com.ng/api/purchase/airtime"
    token = config.get("configurable", {}).get("user_token")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-App-Id": "nmobile_app_id_12345",
        "X-App-Secret": "nmobile_app_secret_67890",
    }

    payload = {
        "network": network,
        "phone": phone_number,
        "amount": amount
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json
        if response.status_code == 200 and data.get("status") == "success":
            ref = data.get("reference_id", "Unknown")
            return f"Success! ₦{amount} airtime purchased for {phone_number} on {network}. Reference: {ref}."
            
        # 5. Handle API Business Logic Errors (e.g., Insufficient Funds)
        else:
            error_message = data.get("message", "Unknown API error")
            return f"Failed to buy airtime. The system said: {error_message}"



    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the transaction server. Details: {str(e)}"
    


@tool
def pay_bills():
    """Pay bills"""
    pass



tools = [check_transaction, check_balance, get_transaction_history, buy_airtime, pay_bills]

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

memory = MemorySaver()

# system_prompt = (
#     "You are Adura, the NMobile Support Agent. "
#     "You help users troubleshoot failed transactions. "
#     "Always ask for a Transaction ID first if the user reports an issue. "
#     "Explain technical failure reasons in simple, empathetic terms."
# )

# agent = create_agent(llm, tools, prompt)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        # "You are Adura, the NMobile Support Agent. Help users troubleshoot failed transactions. "
        # "Always ask for a Transaction ID first. Explain technical reasons simply."
        "You are Adura, the NMobile Support Agent. You are helpful, professional, and concise. "
        "You can check balances, view transaction history, buy airtime, and pay bills. "
        "IMPORTANT RULES:\n"
        # "1. You MUST ask the user for their 10-digit account number before performing ANY action. Do not guess it.\n"
        "1. For airtime, you must know the amount, network, and phone number to recharge.\n"
        "2. For bills, you must know the account number, biller, amount, and reference number.\n"
        "3. If a transaction fails due to insufficient funds, politely inform the user of their current balance."
    ),
    checkpointer=memory
)
# store = {}

# def get_session_history(session_id):
#     if session_id not in store:
#         store[session_id] = ChatMessageHistory()
#     return store[session_id]

# agent_with_history = RunnableWithMessageHistory(agent_executor, get_session_history, input_messages_key="input", history_messages_key="chat_history")
