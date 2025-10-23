"""
ULTRA-FAST RESCRAPER WITH MULTICALL (PARKER'S WAY)
- Uses 1 multicall per token covering ALL wallets
- 41 tokens = 41 multicalls = ~20-40 seconds!
- Queries 41 stablecoins + receipt tokens
- Can process 9,000+ wallets in under a minute! 🚀
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
    
    # Step 3: Analyze with Multicall (PARKER'S WAY!)
    print("\n💰 Step 3: Analyzing all wallets with MULTICALL...")
    print("🚀 Using PARKER'S APPROACH:")
    print("  • 1 multicall per token (not per wallet!)")
    print("  • Each multicall queries ALL ~9,000 wallets")
    print("  • 41 tokens = 41 multicalls = ~20-40 seconds!")
    print("  • Direct on-chain queries (no API limits!)")
    
    analyzer = MulticallAnalyzer()
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

