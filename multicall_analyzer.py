"""
Ultra-Fast Wallet Analyzer using Multicall
Parker's Way: ONE multicall per token covering ALL wallets
~9,000 wallets × 41 tokens = 41 multicalls = ~20-40 seconds! 🚀
"""

from multicall import Call, Multicall
from typing import List, Dict
from datetime import datetime
from database import get_session, Holder, StablecoinBalance
from token_list import ALL_TOKENS
from tqdm import tqdm
from web3 import Web3
import config
import time

# Initialize Web3 provider for multicall
w3 = Web3(Web3.HTTPProvider(config.WEB3_RPC_URL))

class MulticallAnalyzer:
    def __init__(self, wallets_per_batch: int = 3000):
        """
        Initialize Multicall Analyzer
        
        Uses Parker's approach (with chunking for large holder lists):
        - 1 multicall per token per chunk
        - Each multicall queries up to 3,000 wallets for that token
        - ~9,000 wallets ÷ 3,000 = 3 chunks × 41 tokens = 123 multicalls
        - Parker's way: Fast and efficient! 🚀
        """
        self.tokens = ALL_TOKENS
        self.wallets_per_batch = wallets_per_batch
        
        print(f"\n🔍 Multicall Analyzer Initialized (Parker's Way + Chunking)")
        print(f"   • Tracking {len(self.tokens)} tokens")
        print(f"   • Wallets per batch: {wallets_per_batch}")
        print(f"   • Strategy: 1 multicall per token per chunk")
        print(f"   • Stablecoins: {len([t for t in self.tokens.values() if 'underlying' not in t])}")
        print(f"   • Receipt tokens: {len([t for t in self.tokens.values() if 'underlying' in t])}")
    
    def fetch_token_balances(self, token_symbol: str, token_info: dict, holders: List[Holder]) -> Dict[str, int]:
        """
        Fetch balances for ONE token across ALL holders in a SINGLE multicall
        
        Args:
            token_symbol: Token symbol (e.g., 'USDC')
            token_info: Token metadata (address, decimals)
            holders: List of ALL holders to query
            
        Returns:
            Dict mapping holder address to raw balance
        """
        # Create calls for this token across ALL holders
        calls = [
            Call(
                token_info['address'],
                ['balanceOf(address)(uint256)', holder.address],
                [(holder.address.lower(), None)]
            )
            for holder in holders
        ]
        
        # Execute single multicall for this token
        multi = Multicall(calls, _w3=w3)
        results = multi()
        
        return results
    
    def analyze_all_holders(self, limit: int = None):
        """
        Analyze all holders using Parker's multicall approach (with chunking)
        
        Performance:
        - OLD WAY: 9,000 wallets × 41 tokens ÷ 820 batch = 452 batches = ~4 minutes
        - PARKER'S WAY: 41 tokens × 3 chunks = 123 multicalls = ~60 seconds! 🚀
        """
        session = get_session()
        
        try:
            # Get all holders (or unanalyzed ones)
            if limit:
                holders = session.query(Holder).limit(limit).all()
            else:
                holders = session.query(Holder).all()
            
            if not holders:
                print("❌ No holders found in database!")
                return
            
            # Clear all existing stablecoin balances (we're re-analyzing everything)
            print(f"\n🗑️  Clearing old balance data...")
            session.query(StablecoinBalance).delete()
            session.commit()
            
            # Initialize all holders
            for holder in holders:
                holder.total_eth = 0  # ETH not queried via multicall
                holder.total_stablecoins = 0
                holder.last_analyzed = datetime.utcnow()
            
            # Calculate chunks
            num_chunks = (len(holders) + self.wallets_per_batch - 1) // self.wallets_per_batch
            total_tokens = len(self.tokens)
            total_multicalls = total_tokens * num_chunks
            est_time = total_multicalls * 0.5  # ~0.5s per multicall (larger batches take a bit longer)
            
            print(f"\n{'='*60}")
            print(f"🔥 MULTICALL ANALYSIS (PARKER'S WAY + CHUNKING)")
            print(f"{'='*60}")
            print(f"💰 Holders: {len(holders):,}")
            print(f"📦 Chunks: {num_chunks} ({self.wallets_per_batch} wallets each)")
            print(f"🪙  Tokens: {total_tokens}")
            print(f"📊 Strategy: 1 multicall per token per chunk")
            print(f"🔢 Total multicalls: {total_multicalls:,} (not {len(holders) * total_tokens:,}!)")
            print(f"⏰ Estimated time: ~{est_time/60:.1f} minutes")
            print(f"⚠️  Note: ETH balances set to $0 (use Alchemy for ETH)")
            print(f"{'='*60}\n")
            
            # Create a mapping of holder addresses to holder objects
            holder_map = {h.address.lower(): h for h in holders}
            
            # Split holders into chunks
            holder_chunks = [holders[i:i+self.wallets_per_batch] for i in range(0, len(holders), self.wallets_per_batch)]
            
            # Process each token (ONE multicall per token per chunk)
            pbar = tqdm(total=total_multicalls, desc="Fetching token balances", unit="multicall")
            
            for token_symbol, token_info in self.tokens.items():
                try:
                    decimals = token_info['decimals']
                    total_holders_with_balance = 0
                    
                    # Process each chunk for this token
                    for chunk_idx, holder_chunk in enumerate(holder_chunks):
                        try:
                            # Fetch balances for this token across this chunk
                            balances = self.fetch_token_balances(token_symbol, token_info, holder_chunk)
                            
                            # Process results
                            for address, raw_balance in balances.items():
                                if raw_balance and int(raw_balance) > 0:
                                    holder = holder_map.get(address.lower())
                                    if holder:
                                        balance_float = int(raw_balance) / (10 ** decimals)
                                        
                                        # Save balance record
                                        balance_record = StablecoinBalance(
                                            holder_id=holder.id,
                                            stablecoin_name=token_symbol,
                                            balance=balance_float,
                                            raw_balance=str(raw_balance),
                                            decimals=decimals,
                                            last_updated=datetime.utcnow()
                                        )
                                        session.add(balance_record)
                                        
                                        # Update holder's total
                                        holder.total_stablecoins += balance_float
                                        total_holders_with_balance += 1
                            
                            pbar.update(1)
                            pbar.set_postfix({"token": token_symbol, "chunk": f"{chunk_idx+1}/{len(holder_chunks)}", "found": total_holders_with_balance})
                            
                            # Minimal delay between chunks
                            time.sleep(0.05)
                            
                        except Exception as e:
                            pbar.write(f"\n❌ Error fetching {token_symbol} chunk {chunk_idx+1}: {e}")
                            pbar.update(1)
                            continue
                    
                    # Commit after each token
                    session.commit()
                    
                except Exception as e:
                    pbar.write(f"\n❌ Error processing {token_symbol}: {e}")
                    continue
            
            pbar.close()
            
            # Final commit
            print("\n💾 Saving results to database...")
            for holder in holders:
                holder.last_updated = datetime.utcnow()
            session.commit()
            
            # Calculate stats
            analyzed_count = sum(1 for h in holders if h.total_stablecoins > 0)
            total_value = sum(h.total_stablecoins for h in holders)
            
            print(f"\n{'='*60}")
            print(f"✅ ANALYSIS COMPLETE!")
            print(f"{'='*60}")
            print(f"  💰 Total holders: {len(holders):,}")
            print(f"  ✓ Holders with balances: {analyzed_count:,}")
            print(f"  💵 Total stablecoin value: ${total_value:,.0f}")
            print(f"  ⚡ Average: ${(total_value/analyzed_count if analyzed_count > 0 else 0):,.0f} per holder")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            session.rollback()
            raise
        finally:
            session.close()

if __name__ == "__main__":
    analyzer = MulticallAnalyzer()
    analyzer.analyze_all_holders()
