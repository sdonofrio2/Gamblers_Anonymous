import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
################################################################################
# Load-Contract function
################################################################################
@st.cache(allow_output_mutation=True)
def load_contract():
    # Load the contract ABI for DEX
    with open(Path("./contract/ABI_DEX.json")) as f:
        contract_abi_DEX = json.load(f)
    # Load the contract ABI for GamblerCoin
    with open(Path("./contract/ABI_COIN.json")) as f:
        contract_abi_Coin = json.load(f)
    # Set the contract address (this is the address of the deployed contract)
    contract_address_DEX = os.getenv("SMART_CONTRACT_ADDRESS_DEX")
    # Set the contract address (this is the address of the deployed contract)
    contract_address_Coin = os.getenv("SMART_CONTRACT_ADDRESS_COIN")
    # Get the contract
    contract_DEX = w3.eth.contract(address=contract_address_DEX, abi=contract_abi_DEX)
    # Get the contract
    contract_coin = w3.eth.contract(
        address=contract_address_Coin, abi=contract_abi_Coin
    )
    return contract_DEX, contract_coin


# Load the contract
contract_DEX, contract_coin = load_contract()
################################################################################
# Load- Ganache Contracts into Streamlit
################################################################################
st.title("GamblerCoin System")
st.write("Choose an account to get started")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)
st.markdown("---")
# Initiate a session state for the player variables
if "TokensAtTable" not in st.session_state:
    st.session_state["TokensAtTable"] = 0
if "TokensInWallet" not in st.session_state:
    st.session_state["TokensInWallet"] = contract_coin.functions.balanceOf(
        address
    ).call()
st.write(st.session_state)
##########################################################################################################
# Create buttons for the different functionalities
##########################################################################################################
# Create a Buy button to buy tokens
st.write("Do you want to purchase tokens?")
amount = st.number_input("Insert a number", step=1) * 1000000000000000000
if st.button("Buy Tokens"):
    tx_hash = contract_DEX.functions.buy().transact(
        {"from": address, "value": int(amount), "gas": 1000000}
    )
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    st.session_state["TokensInWallet"] += amount
    st.write("Transaction receipt minded:")
    st.write(dict(receipt))
# Create a Sell button to sell tokens
st.write("Do you want to Sell tokens?")
sellAmount = st.number_input("Insert a sell amount", step=1) * 1000000000000000000
if st.button("Sell Tokens"):
    tx_hash_sell = contract_DEX.functions.sell(int(sellAmount)).transact(
        {"from": address, "gas": 1000000}
    )
    receipt_sell = w3.eth.get_transaction_receipt(tx_hash_sell)
    st.session_state["TokensInWallet"] -= sellAmount
    st.write("Transaction receipt minded:")
    st.write(dict(receipt_sell))


# tokenBalance = contract_coin.functions.balanceOf(address).call()
# st.write(f"Current amount of tokens: {tokenBalance}.")
# st.write("Send Tokens to the game table")
# tableCount = st.session_state["TokensAtTable"]
# st.write(f"You have currently {tableCount} tokens at the table")


# Create a button to add tokens from the players wallet to the table.
st.write("Send Tokens to the game table")
tokensToTable = st.number_input(
    "How many tokens do you want to play with today?", step=1
)
if st.button("Add Tokens"):
    # Set variable to tableCount
    tableCount += tokensToTable
    # Burn tokensToTable from account of player
    tx_hash_burn = contract_coin.functions.burn(address, int(tokensToTable)).transact(
        {"from": address, "gas": 1000000}
    )
    st.session_state["TokensAtTable"] += tokensToTable
    st.session_state["TokensInWallet"] = contract_coin.functions.balanceOf(
        address
    ).call()
    tokenBalance = contract_coin.functions.balanceOf(address).call()
    st.write(f"You have currently {tableCount} tokens at the table")
    st.write(f"Current amount of tokens in your wallet: {tokenBalance}.")


# Button to close the table: all tokens at the table will be minted to the wallet
if st.button("Close Table"):
    # Mint tokensToTable from account of player
    tableCount = st.session_state["TokensAtTable"]
    tokenBalance = st.session_state["TokensInWallet"]
    if tableCount > 0:
        tx_hash_mint = contract_DEX.functions.mint(address, int(tableCount)).transact(
            {"from": address, "gas": 1000000}
        )
        st.session_state["TokensInWallet"] = contract_coin.functions.balanceOf(
            address
        ).call()
        st.session_state["TokensAtTable"] = 0
        tableCount = st.session_state["TokensAtTable"]
        tokenBalance = st.session_state["TokensInWallet"]
        st.write(
            f"You have succesfully removed all your coins from the table. You have {tableCount} tokens at the table"
        )
        st.write(f"Your Current amount of tokens in your wallet: {tokenBalance}.")
    else:
        st.write(
            f"You have succesfully closed your table.You had no tokens left at your table."
        )
        st.write(f"Your Current amount of tokens in your wallet:  {tokenBalance}.")


if st.button("Balance of Token"):
    tokenBalance = contract_coin.functions.balanceOf(address).call()
    st.write(tokenBalance)
if st.button("Reset Table"):
    for key in st.session_state.keys():
        del st.session_state[key]
