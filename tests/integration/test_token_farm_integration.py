from brownie import network
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
)
from scripts.deploy import deploy_token_farm_and_dapp_token
import pytest


def test_stake_and_issue_correct_amounts(amount_staked):
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for integration test")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    starting_balance = dapp_token.balanceOf(account.address)
    price_feed_contract = get_contract("dai_usd_price_feed")
    (_, price, _, _, _) = price_feed_contract.latestRoundData()
    amount_token_to_issue = (
        price * amount_staked
    ) / 10 ** price_feed_contract.decimals()
    # Act
    issue_tx = token_farm.issueTokens({"from": account})
    issue_tx.wait(1)
    # Assert
    assert (
        dapp_token.balanceOf(account.address)
        == starting_balance + amount_token_to_issue
    )