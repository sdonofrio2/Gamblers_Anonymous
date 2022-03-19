import streamlit as st
from PIL import Image
from components import GamePlay, Player, Dealer, Deck

# bank_account = Bank_Account()

# Imports for smart contract
import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

################################################################################
# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
# Load-Contract function
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
accounts = w3.eth.accounts
################################################################################
# Create two tabs for the application. The first to interact with your wallet and the second to play
option_list = ["Deposit/Withdrawal Tokens", "Play Game"]
with st.sidebar:
    ga_sidebar = st.selectbox("What would you like to do?", option_list)
    # Initiate a session state for the player variables
    address = st.selectbox("Select Account", options=accounts)
    # Create a session state to save the wallets values
    if "TokensAtTable" not in st.session_state:
        st.session_state["TokensAtTable"] = 0
    if "TokensInWallet" not in st.session_state:
        st.session_state["TokensInWallet"] = contract_coin.functions.balanceOf(
            address
        ).call()

    st.sidebar.subheader("Overview")
    st.sidebar.write(f"Table Balance: {st.session_state.TokensAtTable}")
    st.sidebar.write(f"Balance in wallet: {st.session_state.TokensInWallet}")

if ga_sidebar == "Deposit/Withdrawal Tokens":
    st.title("GamblerCoin System")
    st.write("Choose an account to get started")
    st.markdown("---")

    ################################################################################
    # Initiate buttons for different functionalities
    # Create a Buy button to buy tokens
    st.write("Do you want to purchase tokens?")
    amount_tokens = st.number_input("Insert a number", step=1,)
    if st.button("Buy Tokens"):
        st.session_state.TokensInWallet += amount_tokens
        amount_wei = amount_tokens / 2500 * 1000000000000000000
        # Buy function use the amount of wei as argument
        tx_hash = contract_DEX.functions.buy().transact(
            {"from": address, "value": int(amount_wei), "gas": 1000000}
        )
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        st.write("Transaction receipt minded:")
        st.write(dict(receipt))
    st.markdown("---")
    # Create a Sell button to sell tokens
    st.write("Do you want to Sell tokens?")
    sellAmount = st.number_input("Insert a sell amount", step=1)
    if st.button("Sell Tokens"):
        # Sell function use the amount of tokens as argument
        tx_hash_sell = contract_DEX.functions.sell(int(sellAmount)).transact(
            {"from": address, "gas": 1000000}
        )
        receipt_sell = w3.eth.get_transaction_receipt(tx_hash_sell)
        st.session_state.TokensInWallet -= sellAmount
        st.write("Transaction receipt minded:")
        st.write(dict(receipt_sell))
    st.markdown("---")
    # Create a button to add tokens from the players wallet to the table.
    st.write("Send Tokens to the game table")
    tokensToTable = st.number_input(
        "How many tokens do you want to play with today?", step=1
    )
    if st.button("Add Tokens"):

        # Burn tokensToTable from account of player
        tx_hash_burn = contract_coin.functions.burn(
            address, int(tokensToTable)
        ).transact({"from": address, "gas": 1000000})
        st.session_state.TokensAtTable += tokensToTable
        st.session_state.TokensInWallet = contract_coin.functions.balanceOf(
            address
        ).call()
        tokenBalance = contract_coin.functions.balanceOf(address).call()
        st.write(
            f"You have currently {st.session_state.TokensAtTable} tokens at the table"
        )
        st.write(f"Current amount of tokens in your wallet: {tokenBalance}.")
    st.markdown("---")

    # For testing purposes only
    if st.button("Balance of Token"):
        tokenBalance = contract_coin.functions.balanceOf(address).call()
        st.write(tokenBalance)

    if st.button("Reset Table"):
        for key in st.session_state.keys():
            del st.session_state[key]

    # Button to close the table: all tokens at the table will be minted to the wallet
    if st.sidebar.button("Close Table"):
        # Mint tokensToTable from account of player
        tableCount = st.session_state["TokensAtTable"]
        tokenBalance = st.session_state["TokensInWallet"]
        if tableCount > 0:
            tx_hash_mint = contract_DEX.functions.mint(
                address, int(tableCount)
            ).transact({"from": address, "gas": 1000000})
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


elif ga_sidebar == "Play Game":
    # Game settings
    number_of_decks = 6
    blackjack_multiplier = 1.5

    # Initialize player, dealer, deck and game play. Cache these variables
    @st.cache(allow_output_mutation=True, suppress_st_warning=True)
    def start_game():
        game_deck = Deck(number_of_decks)
        dealer = Dealer()
        player = Player()
        game_play = GamePlay(player, dealer, game_deck, blackjack_multiplier)
        return game_deck, dealer, player, game_play

    game_deck, dealer, player, game_play = start_game()

    game_play.update()

    # creating an object of class
    # B = Bank_Account()

    # Calling functions with that class object
    # B.deposit()
    # B.withdraw()
    # B.display()
    # B.balance
    # update_chips_amt = int(st.session_state.TokensAtTable)

    # @st.cache(allow_output_mutation=True, suppress_st_warning=True)
    class Chips:
        def __init__(self):
            self.total = int(st.session_state.TokensAtTable)
            self.bet = 0

        def win_bet(self):
            self.total += self.bet
            return self.total

        def lose_bet(self):
            self.total -= self.bet
            return self.total

        def win_bet_bj(self):
            self.total += self.bet * 1.5
            return self.total

        def take_bet(Chips):
            while True:
                try:
                    Chips.bet = int(
                        st.text_input("How many chips would you like to bet? ", key="a")
                    )
                except ValueError:
                    st.write("Sorry! Please can you type in a number: ")
                else:
                    if Chips.bet > Chips.total:
                        st.write(
                            f"Insufficient funds! We put the maximum avaible funds instead: {int(st.session_state.TokensAtTable)}"
                        )
                        Chips.bet = int(st.session_state.TokensAtTable)
                        return False
                    else:
                        break

    st.title("BlackJack Simulator")
    # set up the player's chips
    player_chips = Chips()

    Chips.take_bet(player_chips)

    if st.button("New hand?"):
        game_play.deal_in()

    player_stats = st.empty()
    player_images = st.empty()
    player_hit_option = st.empty()
    player_double_down_option = st.empty()
    player_stand_option = st.empty()
    dealer_stats = st.empty()
    dealer_images = st.empty()
    result = st.empty()

    if "Hit" in player.possible_actions:
        if player_hit_option.button("Hit"):
            player.player_hit(game_deck, game_play)
            if "Hit" not in player.possible_actions:
                player_hit_option.empty()
    if "Double Down" in player.possible_actions:
        if player_double_down_option.button("Double Down"):
            player.double_down(game_deck, game_play)
            player_double_down_option.empty()
            player_hit_option.empty()
            player_stand_option.empty()
    if "Stand" in player.possible_actions:
        if player_stand_option.button("Stand"):
            player.stand(game_play)
            player_hit_option.empty()
            player_double_down_option.empty()
            player_stand_option.empty()

    game_play.update()

    # @st.cache(allow_output_mutation=True, suppress_st_warning=True)
    # game_play.update_chips()
    # if len(self.player.possible_actions) == 0:

    @st.cache(allow_output_mutation=True, suppress_st_warning=True)
    def update_chips():
        if player.best_outcome == "Bust":
            player_chips.lose_bet()
        elif player.best_outcome == "Blackjack" and dealer.cards[0].rank not in [1, 10]:
            player_chips.win_bet_bj()  # * blackjack_multiplier
        elif dealer.best_outcome == "Bust":
            player_chips.win_bet()
        elif dealer.best_outcome == "Blackjack" and player.best_outcome != "Blackjack":
            player_chips.lose_bet()
        elif dealer.best_outcome != "Blackjack" and player.best_outcome == "Blackjack":
            player_chips.win_bet_bj()  # * blackjack_multiplier
        elif dealer.best_outcome == "Awaiting Deal":
            0
        elif player.best_outcome == "Awaiting Deal":
            0
        elif int(dealer.best_outcome) > int(player.best_outcome):
            player_chips.lose_bet()
        elif int(dealer.best_outcome) < int(player.best_outcome):
            player_chips.win_bet()
        return player_chips.total

    update_chips_amt = update_chips()
    st.subheader(update_chips_amt)
    st.session_state["TokensAtTable"] = update_chips_amt

    player_stats.write(player)
    player_images.image(
        [Image.open(card.image_location) for card in player.cards], width=100
    )
    dealer_stats.write(dealer)
    dealer_images.image(
        [Image.open(card.image_location) for card in dealer.cards], width=100
    )
    result.write(game_play)
