pragma solidity ^0.5.0;

//  Import the following contracts from the OpenZeppelin library:
//    * `ERC20`
//    * `ERC20Detailed`
//    * `ERC20Mintable`
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC20/ERC20.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC20/ERC20Detailed.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/access/roles/MinterRole.sol";

// Create a constructor for the KaseiCoin contract and have the contract inherit the libraries that you imported from OpenZeppelin.

contract GamblerCoin is ERC20, ERC20Detailed, MinterRole {
    constructor(uint256 initial_supply)
        public
        ERC20Detailed("GamblerCoin", "GBC", 18)
    {
        address payable owner = msg.sender;
        _mint(owner, initial_supply);
    }

    /**
     * @dev Destroys `amount` tokens from the caller.
     *
     * See {ERC20-_burn}.
     */
    function burn(address owner, uint256 _tokensToBurn) public {
        _burn(owner, _tokensToBurn);
    }

    /**
     * @dev See {ERC20-_mint}.
    
     * Requirements:
     * - the caller must have the {MinterRole}.
     */
    function mint(address recipient, uint256 _newTokens)
        public
        onlyMinter
        returns (bool)
    {
        _mint(recipient, _newTokens);
        return true;
    }
}
/*
=====================================================================================================================================

=====================================================================================================================================
*/
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/math/SafeMath.sol";

/*
==========================================================================================================================================
==========================================================================================================================================
*/
contract DEX {
    using SafeMath for uint256;

    uint256 public exchange_rate = 2;
    address vault;
    GamblerCoin public token;

    event Bought(uint256 amount);
    event Sold(uint256 amount);

    constructor(uint256 initial_supply) public {
        token = new GamblerCoin(initial_supply);
        vault = msg.sender;
    }

    // Input is amount a Wei amount
    function buy() public payable {
        uint256 weiAmountTobuy = msg.value;

        uint256 tokenToBuy = _getTokenAmount(weiAmountTobuy);
        require(tokenToBuy >= 1, "You need to buy at least 1 Token.");
        require(weiAmountTobuy > 0, "You need to send some ether");
        token.mint(msg.sender, tokenToBuy);
        emit Bought(weiAmountTobuy);
    }

    // Input is amount of tokens
    function sell(uint256 amount) public {
        uint256 weiToTransfer = _getWeiAmount(amount);
        require(amount > 0, "You need to sell at least some tokens");
        require(
            token.balanceOf(msg.sender) >= amount,
            "Check the token balance"
        );
        token.burn(msg.sender, amount);
        //change to : transferFrom vault
        msg.sender.transfer(weiToTransfer);
        emit Sold(weiToTransfer);
    }

    // Function to convert the amount of wei for the purchased into amount of tokens. (1ETH = USDpriceEth * 100 Tokens)
    function _getTokenAmount(uint256 weiAmount)
        internal
        view
        returns (uint256)
    {
        //uint256 exchange_rate = getPrice();
        return weiAmount.mul(exchange_rate);
    }

    // Function to convert the amount of tokens to sell into amount of Wei.
    function _getWeiAmount(uint256 TokenAmount)
        internal
        view
        returns (uint256)
    {
        //uint256 exchange_rate = getPrice();
        return (TokenAmount).div(exchange_rate);
    }

    /*
    function getPrice() public view returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(0x9326BFA02ADD2366b30bacB125260Af641031331);
        (,int256 answer,,,) = priceFeed.latestRoundData();
        return uint256(answer*100);
    }
*/
    function() external payable {}

    // return the contract balance that gathers all the Eth from the purchase
    function VaultBalance() public view returns (uint256) {
        return address(this).balance;
    }

    // Allows deployer of the contract to withdraw funds from the Vault address.
    function withdraw(uint256 amount) public {
        require(msg.sender == vault, "You don't own this account!");
        require(address(this).balance >= amount, "Insufficient funds!");
        msg.sender.transfer(amount);
    }

    function mint(address recipient, uint256 _newTokens) public returns (bool) {
        token.mint(recipient, _newTokens);
        return true;
    }
}
