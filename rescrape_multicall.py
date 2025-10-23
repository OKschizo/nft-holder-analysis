"""
ULTRA-FAST RESCRAPER WITH MULTICALL
- Uses Multicall to batch 100 calls per request
- Queries 50+ stablecoins + receipt tokens
- Can process thousands of wallets in minutes
"""

from database import wipe_all_data, get_session, Holder
from data_fetcher import fetch_all_collections
from multicall_analyzer import MulticallAnalyzer
import config

def main():
    print("\n" + "="*60)
    print("🔥 ULTRA-FAST NFT HOLDER RESCRAPE (MULTICALL)")
    print("="*60)
    
    # Step 1: Check database
    print("\n📦 Step 1: Database status...")
    session = get_session()
    count = session.query(Holder).count()
    session.close()
    print(f"Current holders in DB: {count}")
    
    if count > 0:
        response = input("\n⚠️  Clear existing data? (y/n): ")
        if response.lower() == 'y':
            print("Clearing database...")
            wipe_all_data()
            print("✅ Database cleared!")
        else:
            print("⏭️  Skipping database clear")
    else:
        print("✅ Database already clean!")
    
    # Step 2: Fetch NFT holders
    print("\n📥 Step 2: Fetching NFT holders...")
    fetch_all_collections()
    
    session = get_session()
    total_holders = session.query(Holder).count()
    session.close()
    
    print(f"\n✅ Fetched {total_holders} unique holders!")
    
    # Step 3: Analyze with Multicall
    print("\n💰 Step 3: Analyzing all wallets with MULTICALL...")
    print("🚀 Using:")
    print("  • Multicall contract batching")
    print("  • 100 calls per multicall request")
    print("  • 50+ stablecoins + receipt tokens")
    print("  • Direct on-chain queries")
    
    analyzer = MulticallAnalyzer(batch_size=100)
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
    print("   > .\\run_dashboard.bat")

if __name__ == "__main__":
    main()

