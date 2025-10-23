"""
Comprehensive list of stablecoins and staked stablecoin receipt tokens
All addresses are lowercase for comparison
"""

# Major Stablecoins
STABLECOINS = {
    # Traditional Stablecoins
    'USDC': {
        'address': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
        'decimals': 6,
        'name': 'USD Coin'
    },
    'USDT': {
        'address': '0xdac17f958d2ee523a2206206994597c13d831ec7',
        'decimals': 6,
        'name': 'Tether USD'
    },
    'DAI': {
        'address': '0x6b175474e89094c44da98b954eedeac495271d0f',
        'decimals': 18,
        'name': 'Dai Stablecoin'
    },
    'BUSD': {
        'address': '0x4fabb145d64652a948d72533023f6e7a623c7c53',
        'decimals': 18,
        'name': 'Binance USD'
    },
    'FRAX': {
        'address': '0x853d955acef822db058eb8505911ed77f175b99e',
        'decimals': 18,
        'name': 'Frax'
    },
    'USDD': {
        'address': '0x0c10bf8fcb7bf5412187a595ab97a3609160b5c6',
        'decimals': 18,
        'name': 'Decentralized USD'
    },
    'TUSD': {
        'address': '0x0000000000085d4780b73119b644ae5ecd22b376',
        'decimals': 18,
        'name': 'TrueUSD'
    },
    'USDP': {
        'address': '0x8e870d67f660d95d5be530380d0ec0bd388289e1',
        'decimals': 18,
        'name': 'Pax Dollar'
    },
    'GUSD': {
        'address': '0x056fd409e1d7a124bd7017459dfea2f387b6d5cd',
        'decimals': 2,
        'name': 'Gemini Dollar'
    },
    'LUSD': {
        'address': '0x5f98805a4e8be255a32880fdec7f6728c6568ba0',
        'decimals': 18,
        'name': 'Liquity USD'
    },
    'sUSD': {
        'address': '0x57ab1ec28d129707052df4df418d58a2d46d5f51',
        'decimals': 18,
        'name': 'Synth sUSD'
    },
    'PYUSD': {
        'address': '0x6c3ea9036406852006290770bedfcaba0e23a0e8',
        'decimals': 6,
        'name': 'PayPal USD'
    },
}

# Yield-Bearing Stablecoin Receipt Tokens
STABLECOIN_RECEIPTS = {
    # Aave Interest-Bearing Tokens
    'aUSDC': {
        'address': '0xbcca60bb61934080951369a648fb03df4f96263c',
        'decimals': 6,
        'name': 'Aave USDC',
        'underlying': 'USDC'
    },
    'aUSDT': {
        'address': '0x3ed3b47dd13ec9a98b44e6204a523e766b225811',
        'decimals': 6,
        'name': 'Aave USDT',
        'underlying': 'USDT'
    },
    'aDAI': {
        'address': '0x028171bca77440897b824ca71d1c56cac55b68a3',
        'decimals': 18,
        'name': 'Aave DAI',
        'underlying': 'DAI'
    },
    'aBUSD': {
        'address': '0xa361718326c15715591c299427c62086f69923d9',
        'decimals': 18,
        'name': 'Aave BUSD',
        'underlying': 'BUSD'
    },
    'aFRAX': {
        'address': '0xd4937682df3c8aef4fe912a96a74121c0829e664',
        'decimals': 18,
        'name': 'Aave FRAX',
        'underlying': 'FRAX'
    },
    'aLUSD': {
        'address': '0xce1871f791548600cb59efbeffc9c38719142079',
        'decimals': 18,
        'name': 'Aave LUSD',
        'underlying': 'LUSD'
    },
    
    # Compound cTokens
    'cUSDC': {
        'address': '0x39aa39c021dfbae8fac545936693ac917d5e7563',
        'decimals': 8,
        'name': 'Compound USDC',
        'underlying': 'USDC'
    },
    'cUSDT': {
        'address': '0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9',
        'decimals': 8,
        'name': 'Compound USDT',
        'underlying': 'USDT'
    },
    'cDAI': {
        'address': '0x5d3a536e4d6dbd6114cc1ead35777bab948e3643',
        'decimals': 8,
        'name': 'Compound DAI',
        'underlying': 'DAI'
    },
    
    # Yearn Vaults
    'yvUSDC': {
        'address': '0xa354f35829ae975e850e23e9615b11da1b3dc4de',
        'decimals': 6,
        'name': 'Yearn USDC Vault',
        'underlying': 'USDC'
    },
    'yvUSDT': {
        'address': '0x3b27f92c0e212c671ea351827edf93db27cc0c65',
        'decimals': 6,
        'name': 'Yearn USDT Vault',
        'underlying': 'USDT'
    },
    'yvDAI': {
        'address': '0xdA816459F1AB5631232FE5e97a05BBBb94970c95',
        'decimals': 18,
        'name': 'Yearn DAI Vault',
        'underlying': 'DAI'
    },
    
    # Curve LP Tokens (stablecoin pools)
    '3Crv': {
        'address': '0x6c3f90f043a72fa612cbac8115ee7e52bde6e490',
        'decimals': 18,
        'name': 'Curve 3Pool',
        'underlying': 'USDC/USDT/DAI'
    },
    'FRAXBP': {
        'address': '0x3175df0976dfa876431c2e9ee6bc45b65d3473cc',
        'decimals': 18,
        'name': 'Curve FRAX/USDC',
        'underlying': 'FRAX/USDC'
    },
    'LUSD3CRV': {
        'address': '0xed279fdd11ca84beef15af5d39bb4d4bee23f0ca',
        'decimals': 18,
        'name': 'Curve LUSD/3CRV',
        'underlying': 'LUSD/3CRV'
    },
    
    # Convex Staked Curve Tokens
    'cvx3Crv': {
        'address': '0x30d9410ed1d5da1f6c8391af5338c93ab8d4035c',
        'decimals': 18,
        'name': 'Convex 3Pool',
        'underlying': '3Crv'
    },
    
    # StakeDAO
    'sd3Crv': {
        'address': '0xb17640796e4c27a39af51887aff3f8dc0daf9567',
        'decimals': 18,
        'name': 'StakeDAO 3Pool',
        'underlying': '3Crv'
    },
    
    # Maker DSR (DAI Savings Rate)
    'sDAI': {
        'address': '0x83f20f44975d03b1b09e64809b757c47f942beea',
        'decimals': 18,
        'name': 'Savings DAI',
        'underlying': 'DAI'
    },
    
    # Liquity Stability Pool
    'LQTY': {
        'address': '0x6dea81c8171d0ba574754ef6f8b412f2ed88c54d',
        'decimals': 18,
        'name': 'Liquity Token',
        'underlying': 'LUSD'
    },
    
    # Frax Finance
    'sFRAX': {
        'address': '0xa663b02cf0a4b149d2ad41910cb81e23e1c41c32',
        'decimals': 18,
        'name': 'Staked FRAX',
        'underlying': 'FRAX'
    },
    'cvxFXS': {
        'address': '0xfeef77d3f69374f66429c91d732a244f074bdf74',
        'decimals': 18,
        'name': 'Convex FXS',
        'underlying': 'FXS'
    },
    
    # Origin Dollar
    'OUSD': {
        'address': '0x2a8e1e676ec238d8a992307b495b45b3feaa5e86',
        'decimals': 18,
        'name': 'Origin Dollar',
        'underlying': 'USDC/USDT/DAI'
    },
    
    # Alchemix
    'alUSD': {
        'address': '0xbc6da0fe9ad5f3b0d58160288917aa56653660e9',
        'decimals': 18,
        'name': 'Alchemix USD',
        'underlying': 'DAI'
    },
    
    # Angle Protocol
    'agEUR': {
        'address': '0x1a7e4e63778b4f12a199c062f3efdd288afcbce8',
        'decimals': 18,
        'name': 'Angle EUR',
        'underlying': 'EUR Stablecoin'
    },
    
    # Ethena
    'USDe': {
        'address': '0x4c9edd5852cd905f086c759e8383e09bff1e68b3',
        'decimals': 18,
        'name': 'Ethena USD',
        'underlying': 'Synthetic USD'
    },
    'sUSDe': {
        'address': '0x9d39a5de30e57443bff2a8307a4256c8797a3497',
        'decimals': 18,
        'name': 'Staked Ethena USD',
        'underlying': 'USDe'
    },
    
    # Reflexer (RAI)
    'RAI': {
        'address': '0x03ab458634910aad20ef5f1c8ee96f1d6ac54919',
        'decimals': 18,
        'name': 'Reflexer RAI',
        'underlying': 'Uncollateralized'
    },
    
    # Fei Protocol
    'FEI': {
        'address': '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        'decimals': 18,
        'name': 'Fei USD',
        'underlying': 'Algorithmic'
    },
}

# Combine all tokens
ALL_TOKENS = {**STABLECOINS, **STABLECOIN_RECEIPTS}

# Create lookup by address
TOKEN_BY_ADDRESS = {
    token['address']: {
        'symbol': symbol,
        'decimals': token['decimals'],
        'name': token['name']
    }
    for symbol, token in ALL_TOKENS.items()
}

def get_all_token_addresses():
    """Return list of all token addresses"""
    return list(TOKEN_BY_ADDRESS.keys())

def get_token_info(address):
    """Get token info by address"""
    return TOKEN_BY_ADDRESS.get(address.lower())

def get_token_count():
    """Return total number of tokens tracked"""
    return len(ALL_TOKENS)

# Summary
if __name__ == "__main__":
    print(f"Token List Summary:")
    print(f"  - Stablecoins: {len(STABLECOINS)}")
    print(f"  - Receipt Tokens: {len(STABLECOIN_RECEIPTS)}")
    print(f"  - Total: {len(ALL_TOKENS)}")

