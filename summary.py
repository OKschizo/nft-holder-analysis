"""Get complete data summary"""
from database import get_session, Holder, NFTCollection, NFTHolding, StablecoinBalance

s = get_session()

# Get all holders
all_holders = s.query(Holder).all()
total_stablecoins = sum([h.total_stablecoins for h in all_holders if h.total_stablecoins])
total_eth = sum([h.total_eth for h in all_holders if h.total_eth])

# Get by collection
milady_holder_ids = [h.holder_id for h in s.query(NFTHolding).filter_by(collection_id=1).all()]
punk_holder_ids = [h.holder_id for h in s.query(NFTHolding).filter_by(collection_id=2).all()]

milady_sc = sum([h.total_stablecoins for h in s.query(Holder).filter(Holder.id.in_(milady_holder_ids)).all() if h.total_stablecoins])
punk_sc = sum([h.total_stablecoins for h in s.query(Holder).filter(Holder.id.in_(punk_holder_ids)).all() if h.total_stablecoins])

with_assets = s.query(Holder).filter((Holder.total_stablecoins > 0) | (Holder.total_eth > 0)).count()

print("\n" + "="*60)
print("💎 NFT HOLDER ANALYSIS - FINAL SUMMARY")
print("="*60)
print(f"\n📊 Total Holders: {len(all_holders)}")
print(f"   • With liquid assets: {with_assets} ({with_assets/len(all_holders)*100:.1f}%)")
print(f"\n💰 TOTAL VALUE:")
print(f"   • Stablecoins: ${total_stablecoins:,.2f}")
print(f"   • ETH: {total_eth:,.2f} ETH")
print(f"\n📚 BY COLLECTION:")
print(f"   • Milady holders: ${milady_sc:,.2f}")
print(f"   • Punk holders: ${punk_sc:,.2f}")
print(f"\n📍 DATA LOCATION: nft_holders.db")
print(f"   • Balance records: {s.query(StablecoinBalance).count()}")
print(f"\n✅ Dashboard: http://localhost:8501")
print("="*60 + "\n")

s.close()

