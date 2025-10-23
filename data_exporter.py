"""Export data to CSV and other formats"""
import pandas as pd
import os
from datetime import datetime
import config
from database import get_session, Holder, NFTHolding, StablecoinBalance, NFTCollection

class DataExporter:
    def __init__(self):
        self.export_dir = config.EXPORT_DIR
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_all_holders(self) -> str:
        """Export all holders with their NFT and stablecoin data"""
        session = get_session()
        
        try:
            holders = session.query(Holder).all()
            
            data = []
            for holder in holders:
                row = {
                    'address': holder.address,
                    'total_nfts': holder.total_nfts,
                    'total_stablecoins_usd': holder.total_stablecoins,
                }
                
                # Add individual NFT holdings
                for holding in holder.holdings:
                    row[f'{holding.collection.name}_count'] = holding.token_count
                
                # Add individual stablecoin balances and ETH
                for sb in holder.stablecoin_balances:
                    if sb.stablecoin_name == 'ETH':
                        row['ETH_balance'] = sb.balance
                    else:
                        row[f'{sb.stablecoin_name}_balance'] = sb.balance
                
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Fill NaN with 0
            df = df.fillna(0)
            
            # Sort by total stablecoins descending
            df = df.sort_values('total_stablecoins_usd', ascending=False)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'all_holders_{timestamp}.csv'
            filepath = os.path.join(self.export_dir, filename)
            
            df.to_csv(filepath, index=False)
            print(f"Exported {len(df)} holders to {filepath}")
            
            return filepath
            
        finally:
            session.close()
    
    def export_collection_holders(self, collection_name: str) -> str:
        """Export holders for a specific collection"""
        session = get_session()
        
        try:
            collection = session.query(NFTCollection).filter_by(name=collection_name).first()
            if not collection:
                print(f"Collection {collection_name} not found")
                return None
            
            data = []
            for holding in collection.holdings:
                holder = holding.holder
                row = {
                    'address': holder.address,
                    'token_count': holding.token_count,
                    'token_ids': holding.token_ids,
                    'total_stablecoins_usd': holder.total_stablecoins,
                }
                
                # Add stablecoin balances
                for sb in holder.stablecoin_balances:
                    row[f'{sb.stablecoin_name}_balance'] = sb.balance
                
                data.append(row)
            
            df = pd.DataFrame(data)
            df = df.fillna(0)
            df = df.sort_values('total_stablecoins_usd', ascending=False)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{collection_name}_holders_{timestamp}.csv'
            filepath = os.path.join(self.export_dir, filename)
            
            df.to_csv(filepath, index=False)
            print(f"Exported {len(df)} holders for {collection_name} to {filepath}")
            
            return filepath
            
        finally:
            session.close()
    
    def export_top_stablecoin_holders(self, top_n: int = 100) -> str:
        """Export top N holders by stablecoin balance"""
        session = get_session()
        
        try:
            holders = session.query(Holder).order_by(
                Holder.total_stablecoins.desc()
            ).limit(top_n).all()
            
            data = []
            for holder in holders:
                row = {
                    'address': holder.address,
                    'total_nfts': holder.total_nfts,
                    'total_stablecoins_usd': holder.total_stablecoins,
                }
                
                # Add NFT holdings
                for holding in holder.holdings:
                    row[f'{holding.collection.name}_count'] = holding.token_count
                
                # Add stablecoin balances
                for sb in holder.stablecoin_balances:
                    row[f'{sb.stablecoin_name}_balance'] = sb.balance
                
                data.append(row)
            
            df = pd.DataFrame(data)
            df = df.fillna(0)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'top_{top_n}_stablecoin_holders_{timestamp}.csv'
            filepath = os.path.join(self.export_dir, filename)
            
            df.to_csv(filepath, index=False)
            print(f"Exported top {top_n} holders to {filepath}")
            
            return filepath
            
        finally:
            session.close()
    
    def export_summary_stats(self) -> str:
        """Export summary statistics"""
        session = get_session()
        
        try:
            collections = session.query(NFTCollection).all()
            total_holders = session.query(Holder).count()
            
            data = []
            
            # Overall stats
            data.append({
                'metric': 'Total Unique Holders',
                'value': total_holders
            })
            
            total_stablecoins = session.query(Holder).with_entities(
                Holder.total_stablecoins
            ).all()
            total_stable_sum = sum([h[0] for h in total_stablecoins if h[0]])
            
            data.append({
                'metric': 'Total Stablecoins (USD)',
                'value': f'${total_stable_sum:,.2f}'
            })
            
            # Per collection stats
            for collection in collections:
                data.append({
                    'metric': f'{collection.name} - Total Holders',
                    'value': collection.total_holders
                })
            
            df = pd.DataFrame(data)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'summary_stats_{timestamp}.csv'
            filepath = os.path.join(self.export_dir, filename)
            
            df.to_csv(filepath, index=False)
            print(f"Exported summary stats to {filepath}")
            
            return filepath
            
        finally:
            session.close()

def export_all_data():
    """Export all data in various formats"""
    exporter = DataExporter()
    
    print("Exporting all data...")
    exporter.export_all_holders()
    exporter.export_top_stablecoin_holders(100)
    exporter.export_summary_stats()
    
    for collection_name in config.NFT_CONTRACTS.keys():
        exporter.export_collection_holders(collection_name)
    
    print("\n✓ All data exported!")

