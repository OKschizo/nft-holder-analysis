"""
Ultra-Fast Wallet Analyzer using Multicall
Queries 50+ tokens across thousands of wallets in seconds
"""

from multicall import Call, Multicall
from typing import List, Dict
from datetime import datetime
from database import get_session, Holder, StablecoinBalance
from token_list import ALL_TOKENS, get_token_info
from tqdm import tqdm
import config
import time

class MulticallAnalyzer:
    def __init__(self, batch_size: int = 100):
        """
        Initialize Multicall Analyzer
        
        Args:
            batch_size: Number of calls per multicall request (default 100)
                       Each wallet × token = 1 call, so 100 calls = ~2 wallets with 50 tokens
        """
        self.batch_size = batch_size
        self.tokens = ALL_TOKENS
        self.token_addresses = list(ALL_TOKENS.keys())
        
        print(f"\n🔍 Multicall Analyzer Initialized")
        print(f"   • Tracking {len(self.tokens)} tokens")
        print(f"   • Batch size: {batch_size} calls per request")
        print(f"   • Tokens: {len([t for t in self.tokens.values() if 'underlying' not in t])} stablecoins")
        print(f"   • Receipt tokens: {len([t for t in self.tokens.values() if 'underlying' in t])}")
    
    def create_balance_calls(self, holders: List[Holder]) -> List[Call]:
        """Create multicall balance check calls for holders"""
        calls = []
        
        for holder in holders:
            # Add ETH balance (special case - not a token)
            calls.append(
                Call(
                    holder.address,
                    'balance()(uint256)',
                    [(f'eth_{holder.address}', None)]
                )
            )
            
            # Add token balance calls
            for symbol, token_info in self.tokens.items():
                calls.append(
                    Call(
                        token_info['address'],
                        ['balanceOf(address)(uint256)', holder.address],
                        [(f'{symbol}_{holder.address}', None)]
                    )
                )
        
        return calls
    
    def process_multicall_results(self, results: Dict, holders: List[Holder], session) -> Dict:
        """Process multicall results and save to database"""
        stats = {'analyzed': 0, 'errors': 0, 'total': len(holders)}
        
        for holder in holders:
            try:
                # Get ETH balance
                eth_key = f'eth_{holder.address}'
                eth_balance = results.get(eth_key, 0)
                eth_balance_float = int(eth_balance) / (10 ** 18) if eth_balance else 0
                
                # Update holder
                holder.total_eth = eth_balance_float
                holder.last_analyzed = datetime.utcnow()
                
                # Clear old balances
                session.query(StablecoinBalance).filter_by(holder_id=holder.id).delete()
                
                # Save ETH balance
                if eth_balance_float > 0:
                    eth_record = StablecoinBalance(
                        holder_id=holder.id,
                        stablecoin_name='ETH',
                        balance=eth_balance_float,
                        raw_balance=str(eth_balance),
                        decimals=18,
                        last_updated=datetime.utcnow()
                    )
                    session.add(eth_record)
                
                # Process token balances
                total_stablecoins = 0
                
                for symbol, token_info in self.tokens.items():
                    token_key = f'{symbol}_{holder.address}'
                    raw_balance = results.get(token_key, 0)
                    
                    if raw_balance and int(raw_balance) > 0:
                        decimals = token_info['decimals']
                        balance_float = int(raw_balance) / (10 ** decimals)
                        
                        # For receipt tokens, we still count them as stablecoin value
                        # (they represent staked/wrapped stablecoins)
                        total_stablecoins += balance_float
                        
                        # Save balance
                        balance_record = StablecoinBalance(
                            holder_id=holder.id,
                            stablecoin_name=symbol,
                            balance=balance_float,
                            raw_balance=str(raw_balance),
                            decimals=decimals,
                            last_updated=datetime.utcnow()
                        )
                        session.add(balance_record)
                
                # Update total
                holder.total_stablecoins = total_stablecoins
                holder.last_updated = datetime.utcnow()
                
                stats['analyzed'] += 1
                
            except Exception as e:
                print(f"\n❌ Error processing {holder.address[:10]}...: {e}")
                stats['errors'] += 1
        
        # Commit batch
        try:
            session.commit()
        except Exception as e:
            print(f"\n⚠️  Commit error: {e}")
            session.rollback()
            
        return stats
    
    def analyze_all_holders(self, limit: int = None):
        """
        Analyze all holders using multicall
        
        Much faster than individual calls:
        - 9,000 wallets × 50 tokens = 450,000 calls
        - Batched at 100 calls/request = 4,500 requests
        - At ~0.5s per request = ~37 minutes
        
        Compare to: Alchemy Portfolio API at 2 minutes for 9,000 wallets
        """
        session = get_session()
        
        try:
            # Get unanalyzed holders
            query = session.query(Holder).filter(Holder.last_updated == None)
            
            if limit:
                holders = query.limit(limit).all()
            else:
                holders = query.all()
            
            if not holders:
                print("✅ All holders already analyzed!")
                session.close()
                return
            
            # Calculate estimates
            total_calls = len(holders) * (len(self.tokens) + 1)  # +1 for ETH
            total_batches = (total_calls + self.batch_size - 1) // self.batch_size
            est_time = total_batches * 0.5  # ~0.5s per batch
            
            print(f"\n{'='*60}")
            print(f"🔥 MULTICALL ANALYSIS")
            print(f"{'='*60}")
            print(f"💰 Holders: {len(holders)}")
            print(f"🪙  Tokens per holder: {len(self.tokens) + 1} (including ETH)")
            print(f"📊 Total calls: {total_calls:,}")
            print(f"📦 Batches: {total_batches:,} ({self.batch_size} calls each)")
            print(f"⏰ Estimated time: ~{est_time/60:.1f} minutes")
            print(f"{'='*60}\n")
            
            # Create all calls
            print("🔨 Building multicall requests...")
            all_calls = self.create_balance_calls(holders)
            
            # Split into batches
            batches = [all_calls[i:i+self.batch_size] for i in range(0, len(all_calls), self.batch_size)]
            
            print(f"✅ Created {len(batches):,} batches\n")
            
            # Process batches
            total_stats = {'analyzed': 0, 'errors': 0, 'total': len(holders)}
            
            pbar = tqdm(total=len(batches), desc="Processing batches")
            
            for i, batch in enumerate(batches):
                try:
                    # Execute multicall
                    multi = Multicall(batch)
                    results = multi()
                    
                    # Determine which holders are in this batch
                    # Each holder has (tokens + 1) calls
                    calls_per_holder = len(self.tokens) + 1
                    holder_start = (i * self.batch_size) // calls_per_holder
                    holder_end = min(holder_start + (self.batch_size // calls_per_holder) + 2, len(holders))
                    batch_holders = holders[holder_start:holder_end]
                    
                    # Process results
                    batch_stats = self.process_multicall_results(results, batch_holders, session)
                    
                    total_stats['analyzed'] += batch_stats['analyzed']
                    total_stats['errors'] += batch_stats['errors']
                    
                    pbar.update(1)
                    
                    # Progress updates every 50 batches
                    if (i + 1) % 50 == 0:
                        pbar.write(f"✓ Progress: {total_stats['analyzed']}/{len(holders)} holders")
                    
                    # Small delay to avoid overwhelming RPC
                    time.sleep(0.1)
                    
                except Exception as e:
                    pbar.write(f"\n❌ Batch error: {e}")
                    total_stats['errors'] += len(batch_holders)
            
            pbar.close()
            
            print(f"\n{'='*60}")
            print(f"✅ Analysis Complete!")
            print(f"{'='*60}")
            print(f"  ✓ Successfully analyzed: {total_stats['analyzed']}")
            print(f"  ✗ Errors: {total_stats['errors']}")
            print(f"  📊 Success rate: {(total_stats['analyzed']/total_stats['total']*100):.1f}%")
            print(f"{'='*60}\n")
            
        finally:
            session.close()

if __name__ == "__main__":
    analyzer = MulticallAnalyzer(batch_size=100)
    analyzer.analyze_all_holders()

