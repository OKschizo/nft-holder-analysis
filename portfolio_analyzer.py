"""
Enhanced Portfolio Analyzer using Alchemy Portfolio API
Stores complete raw API responses with metadata and prices
"""

import requests
import time
import json
from typing import Dict, List
from datetime import datetime
from database import get_session, Holder, StablecoinBalance
import config
from tqdm import tqdm
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class PortfolioAnalyzer:
    def __init__(self, max_concurrent_requests: int = 10):
        self.base_url = f"https://api.g.alchemy.com/data/v1/{config.ALCHEMY_API_KEY}"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.max_concurrent = max_concurrent_requests
        self.lock = threading.Lock()  # For thread-safe database operations
        
        # Known stablecoin addresses (lowercase)
        self.stablecoins = {
            'USDC': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
            'USDT': '0xdac17f958d2ee523a2206206994597c13d831ec7',
            'DAI': '0x6b175474e89094c44da98b954eedeac495271d0f',
            'BUSD': '0x4fabb145d64652a948d72533023f6e7a623c7c53',
            'FRAX': '0x853d955acef822db058eb8505911ed77f175b99e',
            'USDD': '0x0c10bf8fcb7bf5412187a595ab97a3609160b5c6'
        }
    
    def get_wallet_portfolio_batch(self, addresses: List[str], retries: int = 3) -> Dict:
        """
        Get balances for up to 3 wallets at once using simpler balances endpoint
        No metadata/prices needed - we already know stablecoin decimals and $1 value
        """
        url = f"{self.base_url}/assets/tokens/balances/by-address"
        
        payload = {
            "addresses": [
                {
                    "address": addr,
                    "networks": ["eth-mainnet"]
                }
                for addr in addresses[:3]  # Max 3 addresses per call (balances endpoint)
            ],
            "includeNativeTokens": True,
            "includeErc20Tokens": True
        }
        
        for attempt in range(retries):
            try:
                response = self.session.post(url, json=payload, timeout=15)
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', 5)) + random.uniform(0, 2)
                    print(f"\n⏳ Rate limited! Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                
                # Handle other errors
                if response.status_code >= 400:
                    if attempt < retries - 1:
                        time.sleep(1 * (attempt + 1))
                        continue
                    return {'error': f'HTTP {response.status_code}', 'raw_response': None}
                
                data = response.json()
                return {
                    'success': True,
                    'data': data,
                    'raw_response': json.dumps(data),
                    'timestamp': datetime.utcnow().isoformat(),
                    'addresses_in_batch': addresses
                }
                
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    print(f"\n⏱️  Timeout! Retrying...")
                    time.sleep(2)
                    continue
                return {'error': 'Timeout', 'raw_response': None}
            
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                return {'error': str(e), 'raw_response': None}
        
        return {'error': 'Max retries exceeded', 'raw_response': None}
    
    def parse_portfolio_response(self, portfolio_data: Dict) -> Dict:
        """
        Parse Alchemy portfolio response and extract balances
        
        Returns: {
            'eth_balance': float,
            'stablecoins': {name: {'balance': float, 'usd_value': float, 'raw_balance': str, 'decimals': int}},
            'total_stablecoin_value': float,
            'all_tokens': [list of all token data],
            'metadata': {...}
        }
        """
        if not portfolio_data.get('success'):
            return {
                'eth_balance': 0,
                'stablecoins': {},
                'total_stablecoin_value': 0,
                'all_tokens': [],
                'error': portfolio_data.get('error')
            }
        
        data = portfolio_data.get('data', {}).get('data', {})
        tokens = data.get('tokens', [])
        
        eth_balance = 0
        stablecoins = {}
        all_tokens = []
        
        for token in tokens:
            token_address = token.get('tokenAddress')
            token_balance = token.get('tokenBalance', '0')
            metadata = token.get('tokenMetadata', {})
            decimals = metadata.get('decimals', 18)
            symbol = metadata.get('symbol', '')
            
            # Parse token balance
            try:
                balance_float = int(token_balance) / (10 ** decimals) if token_balance != '0' else 0
            except:
                balance_float = 0
            
            # Skip zero balances
            if balance_float == 0:
                continue
            
            # Store token data
            token_data = {
                'address': token_address,
                'symbol': symbol,
                'balance': balance_float,
                'raw_balance': token_balance,
                'decimals': decimals,
                'metadata': metadata
            }
            
            # Stablecoins are $1, ETH we can ignore for stablecoin analysis
            # No need to fetch prices since we only care about stablecoin USD value
            token_data['usd_value'] = balance_float  # Assume $1 for stablecoins
            
            all_tokens.append(token_data)
            
            # Check if it's ETH (null address)
            if token_address is None or token_address.lower() == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
                eth_balance = balance_float
            
            # Check if it's a stablecoin
            token_addr_lower = (token_address or '').lower()
            for stable_name, stable_addr in self.stablecoins.items():
                if token_addr_lower == stable_addr:
                    stablecoins[stable_name] = {
                        'balance': balance_float,
                        'raw_balance': token_balance,
                        'decimals': decimals,
                        'usd_value': token_data.get('usd_value', balance_float)  # Assume 1:1 if no price
                    }
                    break
        
        # Calculate total stablecoin value
        total_stable = sum(s['usd_value'] for s in stablecoins.values())
        
        return {
            'eth_balance': eth_balance,
            'stablecoins': stablecoins,
            'total_stablecoin_value': total_stable,
            'all_tokens': all_tokens,
            'metadata': {
                'total_tokens': len(all_tokens),
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    def analyze_holders_batch(self, holders: List[Holder], session) -> Dict[str, bool]:
        """Analyze up to 3 holders at once in a single API call"""
        addresses = [h.address for h in holders]
        results = {addr: False for addr in addresses}
        
        try:
            # Get portfolio for all addresses in one call
            portfolio = self.get_wallet_portfolio_batch(addresses)
            
            if not portfolio.get('success'):
                return results
            
            # Parse response for each address
            data = portfolio.get('data', {}).get('data', {})
            tokens_list = data.get('tokens', [])
            
            # Group tokens by address
            tokens_by_address = {}
            for token in tokens_list:
                addr = token.get('address', '').lower()
                if addr not in tokens_by_address:
                    tokens_by_address[addr] = []
                tokens_by_address[addr].append(token)
            
            # Process each holder (thread-safe database updates)
            with self.lock:
                for holder in holders:
                    try:
                        holder_tokens = tokens_by_address.get(holder.address.lower(), [])
                        
                        # Parse tokens for this holder
                        parsed = self._parse_tokens(holder_tokens)
                
                        # Store raw response
                        holder.raw_balance_response = portfolio.get('raw_response')
                        holder.last_analyzed = datetime.utcnow()
                        
                        # Update ETH balance
                        holder.total_eth = parsed['eth_balance']
                        
                        # Clear old stablecoin balances
                        session.query(StablecoinBalance).filter_by(holder_id=holder.id).delete()
                        
                        # Save ETH as a balance record
                        if parsed['eth_balance'] > 0:
                            eth_balance = StablecoinBalance(
                                holder_id=holder.id,
                                stablecoin_name='ETH',
                                balance=parsed['eth_balance'],
                                raw_balance=str(int(parsed['eth_balance'] * 10**18)),
                                decimals=18,
                                last_updated=datetime.utcnow()
                            )
                            session.add(eth_balance)
                        
                        # Save stablecoin balances (value = balance since stablecoins = $1)
                        for stable_name, stable_data in parsed['stablecoins'].items():
                            if stable_data['balance'] > 0:
                                balance = StablecoinBalance(
                                    holder_id=holder.id,
                                    stablecoin_name=stable_name,
                                    balance=stable_data['balance'],  # Stablecoins = $1, so balance = USD value
                                    raw_balance=stable_data['raw_balance'],
                                    decimals=stable_data['decimals'],
                                    last_updated=datetime.utcnow()
                                )
                                session.add(balance)
                        
                        # Update total stablecoins
                        holder.total_stablecoins = parsed['total_stablecoin_value']
                        holder.last_updated = datetime.utcnow()
                        
                        results[holder.address] = True
                        
                    except Exception as e:
                        print(f"\n❌ Error processing {holder.address[:10]}...: {e}")
                        results[holder.address] = False
                        continue
            
            return results
            
        except Exception as e:
            print(f"\n❌ Error in batch: {e}")
            return results
    
    def process_batch_worker(self, holder_ids: List[int], pbar, stats: Dict) -> None:
        """Worker function for concurrent batch processing - each thread gets own session"""
        # Create a new session for this thread
        session = get_session()
        
        try:
            # Load holders fresh in this thread's session
            holders = [session.query(Holder).get(h_id) for h_id in holder_ids]
            
            results = self.analyze_holders_batch(holders, session)
            
            # Commit in thread
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                # Mark all as failed
                for _ in holder_ids:
                    with self.lock:
                        stats['errors'] += 1
                pbar.write(f"\n⚠️ Commit error: {e}")
                return
            
            # Update stats
            with self.lock:
                for success in results.values():
                    if success:
                        stats['analyzed'] += 1
                    else:
                        stats['errors'] += 1
                
                pbar.update(len(holders))
                
                # Progress updates every 100
                if stats['analyzed'] % 100 == 0 and stats['analyzed'] > 0:
                    pbar.write(f"✓ Progress: {stats['analyzed']}/{stats['total']} ({stats['errors']} errors)")
        
        except Exception as e:
            with self.lock:
                stats['errors'] += len(holder_ids)
                pbar.write(f"\n❌ Batch worker error: {e}")
        
        finally:
            session.close()
    
    def _parse_tokens(self, tokens: List[Dict]) -> Dict:
        """Parse token list for a single address - optimized for balances-only endpoint"""
        eth_balance = 0
        stablecoins = {}
        
        for token in tokens:
            token_address = token.get('tokenAddress')
            token_balance = token.get('tokenBalance', '0')
            
            # Check if ETH (null address)
            if token_address is None or token_address.lower() == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
                try:
                    # token_balance is hex string, need to convert with base 16
                    eth_balance = int(token_balance, 16) / (10 ** 18) if token_balance != '0' else 0
                except:
                    eth_balance = 0
                continue
            
            # Check if it's a stablecoin we care about
            token_addr_lower = token_address.lower()
            for stable_name, stable_addr in self.stablecoins.items():
                if token_addr_lower == stable_addr:
                    # Use known decimals from config
                    decimals = config.STABLECOIN_DECIMALS[stable_name]
                    try:
                        # token_balance is hex string, need to convert with base 16
                        balance_float = int(token_balance, 16) / (10 ** decimals) if token_balance != '0' else 0
                    except:
                        balance_float = 0
                    
                    if balance_float > 0:
                        stablecoins[stable_name] = {
                            'balance': balance_float,
                            'raw_balance': token_balance,
                            'decimals': decimals,
                            'usd_value': balance_float  # $1 per stablecoin
                        }
                    break
        
        total_stable = sum(s['usd_value'] for s in stablecoins.values())
        
        return {
            'eth_balance': eth_balance,
            'stablecoins': stablecoins,
            'total_stablecoin_value': total_stable
        }
    
    def analyze_all_holders(self, limit: int = None, batch_size: int = 1):
        """
        Analyze all holders who haven't been analyzed yet
        
        Args:
            limit: Maximum number of holders to analyze (None = all)
            batch_size: Number of addresses per API call (Portfolio API allows up to 2)
        """
        session = get_session()
        
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
        
        print(f"\n{'='*60}")
        print(f"💰 Analyzing {len(holders)} wallets with {self.max_concurrent} concurrent workers...")
        print(f"⏰ Estimated time: ~{len(holders) * 0.05 / 60:.1f} minutes (BLAZING FAST! 🔥)")
        print(f"{'='*60}\n")
        
        # Stats tracking
        stats = {
            'analyzed': 0,
            'errors': 0,
            'total': len(holders)
        }
        
        # Split into batches of 3 (by holder ID, not objects)
        holder_ids = [h.id for h in holders]
        batches = [holder_ids[i:i+3] for i in range(0, len(holder_ids), 3)]
        
        session.close()  # Close main session - workers will create their own
        
        # Process batches concurrently
        pbar = tqdm(total=len(holders), desc=f"Analyzing (x{self.max_concurrent} concurrent)")
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit all batch jobs (pass IDs, not objects)
            futures = [
                executor.submit(self.process_batch_worker, batch, pbar, stats)
                for batch in batches
            ]
            
            # Wait for completion
            for future in as_completed(futures):
                try:
                    future.result()  # This will raise any exceptions from the worker
                except Exception as e:
                    pbar.write(f"\n❌ Future error: {e}")
        
        pbar.close()
        
        print(f"\n{'='*60}")
        print(f"✅ Analysis Complete!")
        print(f"{'='*60}")
        print(f"  ✓ Successfully analyzed: {stats['analyzed']}")
        print(f"  ✗ Errors: {stats['errors']}")
        print(f"  📊 Success rate: {(stats['analyzed']/stats['total']*100):.1f}%")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    analyzer = PortfolioAnalyzer()
    analyzer.analyze_all_holders()
