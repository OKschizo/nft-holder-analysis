# 💎 NFT Holder Analysis Tool

Ultra-fast NFT holder tracking and wallet analysis for **Milady** and **CryptoPunks** collections.

Analyzes **9,000+ wallets in under 2 minutes** using concurrent processing and Alchemy's API.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Edit `config.py` and add your Alchemy API key:
```python
ALCHEMY_API_KEY = 'YOUR_API_KEY_HERE'
```

**Get a free API key:** https://dashboard.alchemy.com/
- Create account
- Create new app
- Enable **Ethereum Mainnet** network
- Copy API key

### 3. Run Full Analysis
```bash
python rescrape_all.py
```

This will:
1. ✅ Fetch all NFT holders (Milady + CryptoPunks)
2. ✅ Analyze wallet balances (ETH + stablecoins)
3. ✅ Store everything in local database

**Time:** ~2 minutes for 9,000+ wallets

### 4. View Dashboard
```bash
# Windows:
.\run_dashboard.bat

# Mac/Linux:
streamlit run dashboard.py
```

Opens at: **http://localhost:8501**

---

## 📊 Features

### Data Collection
- ✅ **NFT Holders**: Fetches all current holders for specified collections
- ✅ **Wallet Analysis**: Analyzes ETH + stablecoin balances (USDC, USDT, DAI, BUSD, FRAX, USDD)
- ✅ **Raw Data Storage**: Stores complete API responses for future reference
- ✅ **Fast Processing**: 10 concurrent workers, 3 addresses per API call

### Dashboard
- 📈 **Real-time Stats**: Total holders, liquid assets, collection breakdowns
- 🔍 **Crossover Analysis**: See holders who own both collections
- 💰 **Top Holders**: View wealthiest addresses by stablecoin balance
- 📊 **Interactive Charts**: Visual breakdowns of holdings
- 💾 **CSV Export**: Export all data or top holders

---

## 📁 Project Structure

```
automiladycamp/
├── rescrape_all.py         # 🔥 Main script - run this!
├── config.py               # API key & NFT contract addresses
├── database.py             # SQLite database models
├── data_fetcher.py         # NFT holder fetcher (Alchemy API)
├── portfolio_analyzer.py   # Wallet balance analyzer (concurrent)
├── dashboard.py            # Streamlit web interface
├── data_exporter.py        # CSV export functionality
├── requirements.txt        # Python dependencies
├── run_dashboard.bat       # Dashboard launcher (Windows)
├── summary.py              # Quick stats in terminal
└── exports/                # CSV exports (auto-generated)
```

---

## 🛠️ Usage

### Full Rescrape
Clears database and fetches everything fresh:
```bash
python rescrape_all.py
```

### Quick Stats
View summary without opening dashboard:
```bash
python summary.py
```

### Individual Steps
```python
# Just fetch NFT holders
from data_fetcher import fetch_all_collections
fetch_all_collections()

# Just analyze wallets (if holders already exist)
from portfolio_analyzer import PortfolioAnalyzer
analyzer = PortfolioAnalyzer(max_concurrent_requests=10)
analyzer.analyze_all_holders()

# Clear database
from database import wipe_all_data
wipe_all_data()
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

### NFT Collections
```python
NFT_CONTRACTS = {
    'Milady': '0x5Af0D9827E0c53E4799BB226655A1de152A425a5',
    'CryptoPunks': '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBb'
}
```

### Stablecoins Tracked
```python
STABLECOINS = {
    'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    # ...
}
```

### Performance Tuning
```python
# In rescrape_all.py, adjust concurrent workers:
analyzer = PortfolioAnalyzer(max_concurrent_requests=10)  # 5-20 recommended
```

---

## 📊 Data Storage

### Database
- **File**: `nft_holders.db` (SQLite)
- **Tables**:
  - `nft_collections` - Collection metadata
  - `holders` - Wallet addresses
  - `nft_holdings` - Who owns what NFTs
  - `stablecoin_balances` - Token balances per wallet

### Exports
Auto-generated CSV files in `exports/` folder:
- `all_holders_YYYYMMDD_HHMMSS.csv` - Complete dataset
- `top_100_stablecoin_holders_YYYYMMDD_HHMMSS.csv` - Top 100 by balance

---

## 🔧 Troubleshooting

### "403 Forbidden" Error
- ✅ Check API key is correct in `config.py`
- ✅ Ensure Ethereum Mainnet is enabled in Alchemy dashboard
- ✅ Verify NFT API is enabled (free tier includes this)

### "Database is locked"
- ✅ Stop all running processes: `taskkill /F /IM python.exe` (Windows)
- ✅ Delete `.db-wal` and `.db-shm` files
- ✅ Run again

### Slow Performance
- ✅ Increase concurrent workers (5-20 recommended)
- ✅ Check internet connection
- ✅ Alchemy free tier has rate limits but should still work

### Missing Data
- ✅ Run `python summary.py` to verify data exists
- ✅ Check `nft_holders.db` file exists
- ✅ Re-run `python rescrape_all.py` if needed

---

## 📈 Performance

### Speed
- **9,000+ wallets analyzed in ~2 minutes**
- **360x faster** than sequential processing
- **3 addresses per API call** (max batching)
- **10 concurrent workers** (parallel processing)

### API Efficiency
- ~3,000 API calls for 9,000 wallets
- Uses optimized `assets/tokens/balances/by-address` endpoint
- No unnecessary metadata or price fetching
- Respects Alchemy rate limits with automatic retry

---

## 🔐 Security

- ⚠️ **Never commit API keys** to version control
- ⚠️ **Don't share your API key** - each person needs their own
- ✅ API key is stored in `config.py` (add to `.gitignore`)
- ✅ Database contains public blockchain data only

---

## 📝 Requirements

- **Python**: 3.13+ (3.10+ should work)
- **Alchemy API Key**: Free tier sufficient
- **Dependencies**: See `requirements.txt`
- **OS**: Windows, Mac, Linux

---

## 💡 Tips

1. **First Run**: Takes ~2 minutes for full analysis
2. **Updates**: Run `rescrape_all.py` anytime for fresh data
3. **Exports**: Use dashboard's export button or find CSVs in `exports/`
4. **API Limits**: Free tier is 300M compute units/month (plenty for this)
5. **Database**: Can be deleted anytime, will regenerate on next run

---

## 🤝 Support

Need help?
1. Check troubleshooting section above
2. Verify API key is configured correctly
3. Ensure all dependencies are installed
4. Try running `python summary.py` for quick diagnostics

---

## ⚡ What Makes This Fast?

1. **Concurrent Processing**: 10 parallel workers analyzing wallets simultaneously
2. **Efficient API**: Uses balance-only endpoint (no metadata overhead)
3. **Batching**: 3 addresses per API call (max allowed)
4. **No Price Fetching**: Stablecoins = $1 (no need to query prices)
5. **Smart Caching**: Stores raw API responses for future use
6. **Database Optimization**: SQLite WAL mode for concurrent writes

---

Built with ❤️ using Python, Streamlit, and Alchemy API
