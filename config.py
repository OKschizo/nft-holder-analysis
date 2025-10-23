"""Configuration for NFT Holder Analysis"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
# Get your free API key from: https://dashboard.alchemy.com/
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY', 'YOUR_API_KEY_HERE')
ALCHEMY_BASE_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

# Web3 RPC endpoint for Multicall
WEB3_RPC_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

# NFT Contract Addresses
NFT_CONTRACTS = {
    'Milady': '0x5Af0D9827E0c53E4799BB226655A1de152A425a5',
    'CryptoPunks': '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBb'
}

# Stablecoin Contract Addresses
STABLECOINS = {
    'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    'BUSD': '0x4Fabb145d64652a948d72533023f6E7A623C7C53',
    'FRAX': '0x853d955aCEf822Db058eb8505911ED77F175b99e',
    'USDD': '0x0C10bF8FcB7Bf5412187A595ab97a3609160b5c6'
}

# Stablecoin Decimals
STABLECOIN_DECIMALS = {
    'USDC': 6,
    'USDT': 6,
    'DAI': 18,
    'BUSD': 18,
    'FRAX': 18,
    'USDD': 18
}

# Database
DB_PATH = 'nft_holders.db'

# Export Directory
EXPORT_DIR = 'exports'

