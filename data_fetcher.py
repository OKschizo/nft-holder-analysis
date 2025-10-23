"""Enhanced NFT data fetcher - stores complete raw API responses"""
import requests
import time
import json
from typing import Dict, List, Set
from datetime import datetime
from database import get_session, NFTCollection, Holder, NFTHolding
import config

class NFTDataFetcher:
    def __init__(self):
        self.base_url = config.ALCHEMY_BASE_URL
        self.nft_base_url = f"https://eth-mainnet.g.alchemy.com/nft/v3/{config.ALCHEMY_API_KEY}"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def fetch_all_holders(self, contract_address: str, collection_name: str) -> Dict:
        """
        Fetch ALL holders for a contract using getOwnersForContract
        Returns: {
            'owners': [list of addresses],
            'total_count': int,
            'raw_responses': [list of API responses],
            'metadata': {...}
        }
        """
        print(f"\n{'='*60}")
        print(f"🔍 Fetching holders for {collection_name}")
        print(f"📝 Contract: {contract_address}")
        print(f"{'='*60}\n")
        
        all_owners = set()
        raw_responses = []
        page_key = None
        page_num = 1
        
        while True:
            print(f"📄 Fetching page {page_num}...", end=" ", flush=True)
            
            url = f"{self.nft_base_url}/getOwnersForContract"
            params = {
                "contractAddress": contract_address,
                "withTokenBalances": True
            }
            
            if page_key:
                params["pageKey"] = page_key
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 429:
                    print(f"\n⏳ Rate limited! Waiting 5s...")
                    time.sleep(5)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                # Store raw response
                raw_responses.append(data)
                
                # Extract owners
                owners_in_page = data.get('owners', [])
                for owner_data in owners_in_page:
                    owner_address = owner_data.get('ownerAddress', '').lower()
                    if owner_address and owner_address != '0x0000000000000000000000000000000000000000':
                        all_owners.add(owner_address)
                
                print(f"✓ Got {len(owners_in_page)} owners (total: {len(all_owners)})")
                
                # Check for next page
                page_key = data.get('pageKey')
                if not page_key:
                    print(f"\n✅ Completed! Found {len(all_owners)} unique holders\n")
                    break
                
                page_num += 1
                time.sleep(0.3)  # Rate limit protection
                
            except requests.exceptions.RequestException as e:
                print(f"\n❌ Error on page {page_num}: {e}")
                if page_num == 1:
                    raise
                break
        
        return {
            'owners': list(all_owners),
            'total_count': len(all_owners),
            'raw_responses': raw_responses,
            'metadata': {
                'contract': contract_address,
                'collection_name': collection_name,
                'pages_fetched': page_num,
                'timestamp': time.time()
            }
        }
    
    def get_token_counts(self, contract_address: str) -> Dict[str, Dict]:
        """
        Get detailed token ownership including token IDs and counts
        Returns: {address: {'token_count': int, 'token_ids': [list], 'raw_data': {...}}}
        """
        print(f"\n🔢 Fetching detailed token ownership...")
        
        url = f"{self.nft_base_url}/getOwnersForContract"
        params = {
            "contractAddress": contract_address,
            "withTokenBalances": True
        }
        
        ownership_map = {}
        page_key = None
        page_num = 1
        
        while True:
            if page_key:
                params["pageKey"] = page_key
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 429:
                    time.sleep(5)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                for owner_data in data.get('owners', []):
                    address = owner_data.get('ownerAddress', '').lower()
                    if not address or address == '0x0000000000000000000000000000000000000000':
                        continue
                    
                    token_balances = owner_data.get('tokenBalances', [])
                    token_ids = [tb.get('tokenId') for tb in token_balances if tb.get('tokenId')]
                    
                    ownership_map[address] = {
                        'token_count': len(token_ids),
                        'token_ids': token_ids,
                        'raw_data': owner_data
                    }
                
                print(f"  Page {page_num}: {len(data.get('owners', []))} owners processed", end="\r")
                
                page_key = data.get('pageKey')
                if not page_key:
                    print(f"\n✅ Token counts completed: {len(ownership_map)} holders\n")
                    break
                
                page_num += 1
                time.sleep(0.3)
                
            except Exception as e:
                print(f"\n⚠️  Error fetching token counts: {e}")
                break
        
        return ownership_map
    
    def save_to_database(self, collection_name: str, contract_address: str, holders_data: Dict):
        """Save fetched data to database with all raw responses"""
        session = get_session()
        
        try:
            print(f"\n💾 Saving {collection_name} data to database...")
            
            # Get or create collection
            collection = session.query(NFTCollection).filter_by(name=collection_name).first()
            if not collection:
                collection = NFTCollection(
                    name=collection_name,
                    contract_address=contract_address
                )
                session.add(collection)
                session.flush()
            
            # Update collection data
            collection.total_holders = holders_data['total_count']
            collection.last_fetched = datetime.utcnow()
            collection.raw_api_response = json.dumps(holders_data['raw_responses'])
            
            # Get detailed token ownership
            token_ownership = self.get_token_counts(contract_address)
            
            # Save holders and holdings
            holders_created = 0
            holdings_created = 0
            
            for address in holders_data['owners']:
                # Get or create holder
                holder = session.query(Holder).filter_by(address=address.lower()).first()
                if not holder:
                    holder = Holder(address=address.lower())
                    session.add(holder)
                    session.flush()
                    holders_created += 1
                
                # Check if holding already exists
                existing_holding = session.query(NFTHolding).filter_by(
                    holder_id=holder.id,
                    collection_id=collection.id
                ).first()
                
                if not existing_holding:
                    # Get token data
                    token_data = token_ownership.get(address.lower(), {})
                    token_count = token_data.get('token_count', 1)
                    token_ids = token_data.get('token_ids', [])
                    
                    # Create holding
                    holding = NFTHolding(
                        holder_id=holder.id,
                        collection_id=collection.id,
                        token_count=token_count,
                        token_ids=json.dumps(token_ids),
                        raw_tokens_data=json.dumps(token_data.get('raw_data', {}))
                    )
                    session.add(holding)
                    holdings_created += 1
                
                # Update holder's total NFT count
                holder.total_nfts = sum(h.token_count for h in holder.holdings)
            
            session.commit()
            
            print(f"✅ Saved successfully!")
            print(f"   📊 Collection: {collection_name}")
            print(f"   👥 Total holders: {collection.total_holders}")
            print(f"   ➕ New holders created: {holders_created}")
            print(f"   ➕ New holdings created: {holdings_created}")
            print(f"{'='*60}\n")
            
            return {
                'success': True,
                'total_holders': collection.total_holders,
                'new_holders': holders_created,
                'new_holdings': holdings_created
            }
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving to database: {e}")
            raise
        finally:
            session.close()
    
    def fetch_and_save_collection(self, collection_name: str, contract_address: str):
        """Complete workflow: fetch and save a collection"""
        print(f"\n🚀 Starting full fetch for {collection_name}")
        print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Fetch all holders
        holders_data = self.fetch_all_holders(contract_address, collection_name)
        
        # Save to database
        result = self.save_to_database(collection_name, contract_address, holders_data)
        
        return result

def fetch_all_collections():
    """Fetch all configured NFT collections"""
    fetcher = NFTDataFetcher()
    results = {}
    
    print("\n" + "="*60)
    print("🎨 STARTING FULL NFT DATA FETCH")
    print("="*60 + "\n")
    
    for name, address in config.NFT_CONTRACTS.items():
        try:
            result = fetcher.fetch_and_save_collection(name, address)
            results[name] = result
        except Exception as e:
            print(f"❌ Failed to fetch {name}: {e}\n")
            results[name] = {'success': False, 'error': str(e)}
    
    print("\n" + "="*60)
    print("✅ FETCH COMPLETE")
    print("="*60)
    print("\nSummary:")
    for name, result in results.items():
        if result.get('success'):
            print(f"  ✓ {name}: {result['total_holders']} holders")
        else:
            print(f"  ✗ {name}: Failed - {result.get('error', 'Unknown error')}")
    print("\n")
    
    return results

if __name__ == "__main__":
    fetch_all_collections()
