from brownie import (
    network,
    accounts,
    config,
    Contract,
    MockDAI,
    MockWETH,
    MockV3Aggregator,
)

INITIAL_PRICE_FEED_VALUE = 2000 * 10 ** 18
DECIMALS = 18
LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "hardhat",
    "development",
    "ganache",
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "fau_token": MockDAI,
    "weth_token": MockWETH,
}


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_PRICE_FEED_VALUE):
    account = get_account()
    print(f"Deploying mocks for {network.show_active()}")
    print("Deploying Mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
    print("Deployed Mock Price Feed at: ", mock_price_feed.address)
    # link_token = LinkToken.deploy({"from": account})
    print("Deploying Mock DAI")
    dai_token = MockDAI.deploy({"from": account})
    print("deployed to ", dai_token.address)
    print("Deploying Mock WETH")
    weth_token = MockWETH.deploy({"from": account})
    print("deployed to ", weth_token.address)


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config if defined, otherwise it will deploy the mock version of that contract and return the mock contract.
    Args:
        contract_name (string)
    Returns:
        brownie.network.contract.ProjectContract: The most recently deployed version of the contract.
    """
    contract_type = contract_to_mock.get(contract_name)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def fund_with_link(
    contract_address, account=None, link_token=None, amount=10 ** 17
):  # 0.1 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    # link_token = interface.LinkTokenInterface(link_token.address)
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print(f"Funded {contract_address}")
    return tx
