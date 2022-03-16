import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from solcx import compile_standard, install_solc

load_dotenv()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

################################################################################
# Load-Contract function
################################################################################


@st.cache(allow_output_mutation=True)
def load_contract():

    # # Open Solidty file
    # with open("./contract/GamblerCoin.sol", "r") as file:
    #     gamblerCoin_file = file.read()

    # # Install the version of the compiler
    # install_solc("0.8.0")

    # # Solidity source code
    # compiled_sol = compile_standard(
    #     {
    #         "language": "Solidity",
    #         "sources": {"GamblerCoin.sol": {"content": gamblerCoin_file}},
    #         "settings": {
    #             "outputSelection": {
    #                 "*": {
    #                     "*": [
    #                         "abi",
    #                         "metadata",
    #                         "evm.bytecode",
    #                         "evm.bytecode.sourceMap",
    #                     ]
    #                 }
    #             }
    #         },
    #     },
    #     solc_version="0.8.0",
    # )

    # # Transform solidity souce file in Json
    # with open("compiled_code.json", "w") as file:
    #     json.dump(compiled_sol, file)

    #     contract_abi_DEX = json.loads(
    #         compiled_sol["contracts"]["GamblerCoin.sol"]["DEX"]["metadata"]
    #     )["output"]["abi"]

    #     contract_abi_Coin = json.loads(
    #         compiled_sol["contracts"]["GamblerCoin.sol"]["GamblerCoin"]["metadata"]
    #     )["output"]["abi"]

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


st.write("Do you want to purchase tokens?")
amount = st.number_input("Insert a number", step=1) * 1000000000000000000
if st.button("Buy Tokens"):
    tx_hash = contract_DEX.functions.buy().transact(
        {"from": address, "value": int(amount), "gas": 1000000}
    )
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    st.write("Transaction receipt minded:")
    st.write(dict(receipt))

st.write("Do you want to Sell tokens?")
sellAmount = st.number_input("Insert a sell amount", step=1) * 1000000000000000000
if st.button("Sell Tokens"):
    tx_hash_sell = contract_DEX.functions.sell(int(sellAmount)).transact(
        {"from": address, "gas": 1000000}
    )
    receipt_sell = w3.eth.get_transaction_receipt(tx_hash_sell)
    st.write("Transaction receipt minded:")
    st.write(dict(receipt_sell))


tokenBalance = contract_coin.functions.balanceOf(address).call()
st.write(f"Current amount of tokens: {tokenBalance}.")


st.write("Send Tokens to the game table")
tableCount = 0
st.write(f"You have currently {tableCount} tokens at the table")

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
    tokenBalance = contract_coin.functions.balanceOf(address).call()
    st.write(f"You have currently {tableCount} tokens at the table")
    st.write(f"Current amount of tokens in your wallet: {tokenBalance}.")


if st.button("Close Table"):
    # Mint tokensToTable from account of player
    if tableCount > 0:
        tx_hash_burn = contract_coin.functions.mint(address, int(tableCount)).transact(
            {"from": address, "gas": 1000000}
        )
        tableCount = 0
        tokenBalance = contract_coin.functions.balanceOf(address).call()
        st.write(
            f"You have succesfully removed all your coins from the table. You have {tableCount} tokens at the table"
        )
        st.write(f"Your Current amount of tokens in your wallet: {tokenBalance}.")
    else:
        st.write(
            f"You have succesfully closed your table.You had no tokens left at your table."
        )
        st.write(f"Your Current amount of tokens in your wallet: {tokenBalance}.")

################################################################################
# Get Appraisals
################################################################################
