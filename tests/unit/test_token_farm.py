import pytest
from brownie import network, exceptions
from scripts.deploy import deploy_token_farm_and_dapp_token
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    INITIAL_PRICE_FEED_VALUE,
    DECIMALS,
)


def test_set_price_feed_contract():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Test only runs on local testnet")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    non_owner = get_account(index=1)
    # Act
    price_feed_address = get_contract("dai_usd_price_feed").address
    token_farm.setPriceFeedContract(
        dapp_token.address,
        price_feed_address,
        {"from": account},
    )
    # Assert
    assert token_farm.tokenPriceFeedMapping(dapp_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(
            dapp_token.address,
            price_feed_address,
            {"from": non_owner},
        )


def test_stake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Test only runs on local testnet")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    # Assert
    assert (
        token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked
    )
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account
    return token_farm, dapp_token


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Test only runs on local testnet")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)

    # Act
    token_farm.issueTokens({"from": account})
    # Assert
    assert (
        dapp_token.balanceOf(account.address)
        == starting_balance + INITIAL_PRICE_FEED_VALUE
    )


def test_unstake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Test only runs on local testnet")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)

    # Act
    token_farm.unstakeTokens(dapp_token.address, {"from": account})
    # Assert
    assert dapp_token.balanceOf(account.address) == starting_balance + amount_staked
    with pytest.raises(exceptions.VirtualMachineError):
        assert token_farm.stakers(0) == account


def test_token_value():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Test only runs on local testnet")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    (price, decimals) = token_farm.getTokenValue(dapp_token.address, {"from": account})
    assert (price, decimals) == (INITIAL_PRICE_FEED_VALUE, DECIMALS)


def test_user_single_token_value(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Test only runs on local testnet")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    assert (
        token_farm.getUserSingleTokenValue(
            account.address, dapp_token.address, {"from": account}
        )
        == (amount_staked * INITIAL_PRICE_FEED_VALUE) / 10 ** DECIMALS
    )


def test_user_total_value(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Test only runs on local testnet")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    assert (
        token_farm.getUserTotalValue(account.address, {"from": account})
        == (amount_staked * INITIAL_PRICE_FEED_VALUE) / 10 ** DECIMALS
    )


def test_token_is_allowed():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Test only runs on local testnet")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    assert token_farm.tokenIsAllowed(dapp_token.address, {"from": account}) == True
