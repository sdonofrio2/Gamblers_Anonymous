import json

from web3 import Web3

# In the video, we forget to `install_solc`
# from solcx import compile_standard
from solcx import compile_standard, install_solc
import os
from dotenv import load_dotenv

load_dotenv()


with open("./contract/GamblerCoin.sol", "r") as file:
    GamblerCoin_file = file.read()

# We add these two lines that we forgot from the video!
print("Installing...")
install_solc("0.6.0")

# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"./contract/GamblerCoin.sol": {"content": GamblerCoin_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["GamblerCoin.sol"]["DEX"]["evm"]["bytecode"][
    "object"
]

# get abi
abi = json.loads(compiled_sol["contracts"]["GamblerCoin.sol"]["DEX"]["metadata"])[
    "output"
]["abi"]

print(abi)
