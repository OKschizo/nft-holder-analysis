"""
ULTRA-FAST RESCRAPER
- Uses optimized Token Balances By Address endpoint (no metadata/prices)
- Batch 3 addresses per call
- 10 concurrent workers
- Should complete ~9,000 wallets in under 10 minutes!
"""

from database import wipe_all_data, get_session, Holder
from data_fetcher import fetch_all_collections
from portfolio_analyzer import PortfolioAnalyzer
import config

def main():
    print("\n" + "="*60)
    print("🔥 ULTRA-FAST NFT HOLDER RESCRAPE")
    print("="*60)
    
    # Step 1: Wipe database (already done, but keeping for safety)
    print("\n📦 Step 1: Database status...")
    session = get_session()
    count = session.query(Holder).count()
    session.close()
    print(f"Current holders in DB: {count}")
    
    if count > 0:
        print("⚠️  Clearing database...")
        wipe_all_data()
        print("✅ Database cleared!")
    else:
        print("✅ Database already clean!")
    
    # Step 2: Fetch NFT holders
    print("\n📥 Step 2: Fetching NFT holders...")
    fetch_all_collections()
    
    session = get_session()
    total_holders = session.query(Holder).count()
    session.close()
    
    print(f"\n✅ Fetched {total_holders} unique holders!")
    
    # Step 3: Analyze wallets with MAXIMUM SPEED
    print("\n💰 Step 3: Analyzing all wallets...")
    print("🚀 Using:")
    print("  • Token Balances By Address endpoint (fast!)")
    print("  • 3 addresses per API call")
    print("  • 10 concurrent workers")
    print("  • NO price fetching (stablecoins = $1)")
    
    analyzer = PortfolioAnalyzer(max_concurrent_requests=10)
    analyzer.analyze_all_holders()
    
    # Summary
    print("\n" + "="*60)
    print("🎉 RESCRAPE COMPLETE!")
    print("="*60)
    
    session = get_session()
    total = session.query(Holder).count()
    analyzed = session.query(Holder).filter(Holder.last_updated != None).count()
    session.close()
    
    print(f"Total holders: {total}")
    print(f"Analyzed: {analyzed}")
    print(f"\n✅ Run the dashboard to view results!")
    print("   > run_dashboard.bat")

if __name__ == "__main__":
    main()
