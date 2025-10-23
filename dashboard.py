"""
Milady & CryptoPunks NFT Holder Analysis Dashboard
Clean, modern interface for analyzing holder wallets and stablecoin balances
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database import get_session, NFTCollection, Holder, StablecoinBalance, NFTHolding, init_collections
from data_fetcher import NFTDataFetcher
from portfolio_analyzer import PortfolioAnalyzer
from data_exporter import DataExporter

# Page config
st.set_page_config(
    page_title="Milady & Punks Analysis",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF6B9D 0%, #C239B3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
    .stMetric {
        background-color: #1e1e1e !important;
        padding: 1rem;
        border-radius: 8px;
    }
    .stMetric label {
        color: #e0e0e0 !important;
        font-weight: 600 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: bold !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #a0a0a0 !important;
    }
    /* Fix dataframe text */
    .stDataFrame {
        color: #000000 !important;
    }
    /* Fix markdown text */
    .stMarkdown {
        color: #e0e0e0 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    p {
        color: #e0e0e0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_collections()

# Header
st.markdown('<p class="main-header">💎 Milady & CryptoPunks Holder Analysis</p>', unsafe_allow_html=True)
st.markdown("### On-chain wallet analysis and stablecoin tracking")
st.markdown("---")

# Sidebar
st.sidebar.title("🎛️ Controls")

# Collection toggle
st.sidebar.markdown("### 👁️ View Collections")
show_milady = st.sidebar.checkbox("💗 Milady", value=True, key="show_milady")
show_punks = st.sidebar.checkbox("🔷 CryptoPunks", value=True, key="show_punks")

active_collections = []
if show_milady:
    active_collections.append("Milady")
if show_punks:
    active_collections.append("CryptoPunks")

if active_collections:
    st.sidebar.success(f"📊 Viewing: {', '.join(active_collections)}")
else:
    st.sidebar.warning("⚠️ Select at least one collection")

st.sidebar.markdown("---")

# Data Management
st.sidebar.markdown("### 📡 Data Management")

if st.sidebar.button("🔄 Fetch NFT Holders", use_container_width=True):
    with st.spinner("Fetching NFT holder data from Alchemy..."):
        try:
            fetcher = NFTDataFetcher()
            for name, address in [("Milady", "0x5Af0D9827E0c53E4799BB226655A1de152A425a5"),
                                   ("CryptoPunks", "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBb")]:
                holders = fetcher.get_nft_holders(address)
                st.sidebar.info(f"✓ {name}: {len(holders['owners'])} holders")
            st.sidebar.success("✅ NFT data fetched!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# Wallet Analysis
st.sidebar.markdown("### 💰 Analyze Wallets")
analyze_limit = st.sidebar.number_input(
    "Limit (0 = all)", 
    min_value=0, 
    max_value=10000, 
    value=0,
    help="Number of wallets to analyze. 0 = analyze all unanalyzed wallets"
)

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("⚡ Fast", use_container_width=True):
        with st.spinner("Analyzing wallets..."):
            try:
                analyzer = PortfolioAnalyzer()
                analyzer.analyze_all_holders(limit=analyze_limit if analyze_limit > 0 else None)
                st.sidebar.success("✅ Analysis complete!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

with col2:
    if st.button("🚀 Ultra", use_container_width=True):
        with st.spinner("Ultra-fast analysis..."):
            try:
                analyzer = PortfolioAnalyzer()
                analyzer.analyze_all_holders(limit=analyze_limit if analyze_limit > 0 else None)
                st.sidebar.success("✅ Analysis complete!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

st.sidebar.markdown("---")

# Export section
st.sidebar.markdown("### 📥 Export Data")
exporter = DataExporter()

if st.sidebar.button("📊 Export All Data", use_container_width=True):
    try:
        filename = exporter.export_all_holders()
        st.sidebar.success(f"✓ Exported: {filename}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

if st.sidebar.button("🏆 Export Top 100", use_container_width=True):
    try:
        filename = exporter.export_top_stablecoin_holders(100)
        st.sidebar.success(f"✓ Exported: {filename}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# Main Dashboard
session = get_session()

# Get filtered collections
if active_collections:
    collections = session.query(NFTCollection).filter(NFTCollection.name.in_(active_collections)).all()
else:
    collections = []

# Calculate metrics
total_holders = 0
total_nfts = 0
holders_with_balance = set()
total_stablecoins = 0

for collection in collections:
    total_holders += collection.total_holders
    # Calculate total NFTs from holdings
    total_nfts += sum(holding.token_count for holding in collection.holdings)
    for holding in collection.holdings:
        if holding.holder.total_stablecoins and holding.holder.total_stablecoins > 0:
            holders_with_balance.add(holding.holder.id)
            
# Get all holders for selected collections
if active_collections:
    holder_ids = set()
    for collection in collections:
        holder_ids.update([h.holder_id for h in collection.holdings])
    
    filtered_holders = session.query(Holder).filter(Holder.id.in_(holder_ids)).all()
    total_stablecoins = sum([h.total_stablecoins for h in filtered_holders if h.total_stablecoins])
else:
    filtered_holders = []

# Top metrics
st.markdown("## 📊 Overview")
col1, col2, col3, col4, col5 = st.columns(5)

# Calculate average for non-zero accounts
holders_with_nonzero = [h for h in filtered_holders if h.total_stablecoins and h.total_stablecoins > 0]
avg_balance_nonzero = (total_stablecoins / len(holders_with_nonzero)) if holders_with_nonzero else 0

with col1:
    st.metric(
        label="👥 Total Holders",
        value=f"{len(holder_ids) if active_collections else 0:,}",
        help="Unique wallet addresses holding selected NFTs"
    )

with col2:
    st.metric(
        label="💎 Total NFTs",
        value=f"{total_nfts:,}",
        help="Total number of NFTs in selected collections"
    )

with col3:
    st.metric(
        label="💰 With Liquid Assets",
        value=f"{len(holders_with_balance):,}",
        help="Holders with ETH or stablecoins > $0"
    )

with col4:
    st.metric(
        label="💵 Total Stablecoins",
        value=f"${total_stablecoins:,.0f}",
        help="Combined stablecoin value across all holders"
    )

with col5:
    st.metric(
        label="📊 Avg (Non-Zero)",
        value=f"${avg_balance_nonzero:,.0f}",
        help="Average stablecoin balance for holders with non-zero balance"
    )

st.markdown("---")

# Collection breakdown
if collections:
    st.markdown("## 🎨 Collection Breakdown")
    
    col1, col2 = st.columns(2)
    
    for idx, collection in enumerate(collections):
        with col1 if idx % 2 == 0 else col2:
            with st.container():
                st.markdown(f"### {collection.name}")
                
                # Collection metrics
                c1, c2, c3, c4 = st.columns(4)
                
                with c1:
                    st.metric("Holders", f"{collection.total_holders:,}")
                
                with c2:
                    # Calculate total supply from holdings
                    supply = sum(holding.token_count for holding in collection.holdings)
                    st.metric("Supply", f"{supply:,}")
                
                with c3:
                    # Get holders with balance for this collection
                    coll_holders_with_balance = len([h for h in collection.holdings 
                                                     if h.holder.total_stablecoins and h.holder.total_stablecoins > 0])
                    st.metric("With Assets", f"{coll_holders_with_balance:,}")
                
                with c4:
                    # Average for non-zero holders
                    coll_total_stable = sum([h.holder.total_stablecoins for h in collection.holdings 
                                            if h.holder.total_stablecoins])
                    coll_avg = (coll_total_stable / coll_holders_with_balance) if coll_holders_with_balance > 0 else 0
                    st.metric("Avg (Non-Zero)", f"${coll_avg:,.0f}")
                
                # Total stablecoins for this collection
                st.info(f"💰 Total Stablecoins: **${coll_total_stable:,.0f}**")

st.markdown("---")

# Stablecoin distribution charts
if filtered_holders and any(h.total_stablecoins and h.total_stablecoins > 0 for h in filtered_holders):
    st.markdown("## 📈 Stablecoin Analysis")
    
    # Get holders with stablecoins
    holders_with_stable = [h for h in filtered_holders if h.total_stablecoins and h.total_stablecoins > 0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution by stablecoin type
        st.markdown("### 💎 Stablecoin Distribution")
        
        stablecoin_totals = {
            'USDC': 0,
            'USDT': 0,
            'DAI': 0,
            'ETH': 0
        }
        
        for holder in holders_with_stable:
            for balance in holder.stablecoin_balances:
                if balance.stablecoin_name in stablecoin_totals:
                    stablecoin_totals[balance.stablecoin_name] += balance.balance
        
        # Create pie chart
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(stablecoin_totals.keys()),
            values=list(stablecoin_totals.values()),
            hole=0.4,
            marker=dict(colors=['#2E86DE', '#54A0FF', '#5F27CD', '#C8D6E5'])
        )])
        
        fig_pie.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=0, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Top holders bar chart
        st.markdown("### 🏆 Top 10 Holders by Stablecoins")
        
        top_holders = sorted(holders_with_stable, key=lambda h: h.total_stablecoins, reverse=True)[:10]
        
        df_top = pd.DataFrame([
            {
                'Address': h.address[:8] + '...' + h.address[-6:],
                'Value': h.total_stablecoins
            }
            for h in top_holders
        ])
        
        fig_bar = px.bar(
            df_top,
            x='Value',
            y='Address',
            orientation='h',
            color='Value',
            color_continuous_scale='Viridis'
        )
        
        fig_bar.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Stablecoin Value ($)",
            yaxis_title="",
            margin=dict(t=0, b=0, l=0, r=40)
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Histogram of holder balances
    st.markdown("### 📊 Balance Distribution")
    
    balance_ranges = {
        '$0-$1K': 0,
        '$1K-$10K': 0,
        '$10K-$50K': 0,
        '$50K-$100K': 0,
        '$100K-$500K': 0,
        '$500K+': 0
    }
    
    for holder in holders_with_stable:
        val = holder.total_stablecoins
        if val < 1000:
            balance_ranges['$0-$1K'] += 1
        elif val < 10000:
            balance_ranges['$1K-$10K'] += 1
        elif val < 50000:
            balance_ranges['$10K-$50K'] += 1
        elif val < 100000:
            balance_ranges['$50K-$100K'] += 1
        elif val < 500000:
            balance_ranges['$100K-$500K'] += 1
        else:
            balance_ranges['$500K+'] += 1
    
    df_dist = pd.DataFrame([
        {'Range': k, 'Count': v}
        for k, v in balance_ranges.items()
    ])
    
    fig_hist = px.bar(
        df_dist,
        x='Range',
        y='Count',
        color='Count',
        color_continuous_scale='Blues'
    )
    
    fig_hist.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Balance Range",
        yaxis_title="Number of Holders"
    )
    
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# Punk + Milady Crossover Analysis
if show_milady and show_punks:
    st.markdown("## 👥 Milady × CryptoPunks Crossover")
    
    milady_coll = session.query(NFTCollection).filter_by(name='Milady').first()
    punk_coll = session.query(NFTCollection).filter_by(name='CryptoPunks').first()
    
    if milady_coll and punk_coll:
        milady_holder_ids = set([h.holder_id for h in milady_coll.holdings])
        punk_holder_ids = set([h.holder_id for h in punk_coll.holdings])
        crossover_ids = milady_holder_ids.intersection(punk_holder_ids)
        
        crossover_holders = session.query(Holder).filter(Holder.id.in_(crossover_ids)).all()
        crossover_holders_sorted = sorted(crossover_holders, key=lambda h: h.total_stablecoins or 0, reverse=True)
        
        # Crossover metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🤝 Crossover Holders", f"{len(crossover_holders):,}")
        
        with col2:
            crossover_stable = sum([h.total_stablecoins for h in crossover_holders if h.total_stablecoins])
            st.metric("💰 Total Stablecoins", f"${crossover_stable:,.0f}")
        
        with col3:
            avg_stable = crossover_stable / len([h for h in crossover_holders if h.total_stablecoins and h.total_stablecoins > 0]) if any(h.total_stablecoins and h.total_stablecoins > 0 for h in crossover_holders) else 0
            st.metric("📊 Avg Stablecoins", f"${avg_stable:,.0f}")
        
        with col4:
            percentage = (len(crossover_holders) / len(milady_holder_ids)) * 100
            st.metric("📈 % of Milady", f"{percentage:.1f}%")
        
        # Filters
        st.markdown("### 🔍 Filter Crossover Holders")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_punks = st.slider("Min Punks", 0, 10, 0, key="min_punks")
        
        with col2:
            min_miladys = st.slider("Min Miladys", 0, 20, 0, key="min_miladys")
        
        with col3:
            min_balance = st.slider("Min Balance ($)", 0, 100000, 0, step=1000, key="min_balance")
        
        # Build table data
        if crossover_holders_sorted:
            crossover_data = []
            
            for holder in crossover_holders_sorted:
                punk_holding = next((h for h in holder.holdings if h.collection.name == 'CryptoPunks'), None)
                milady_holding = next((h for h in holder.holdings if h.collection.name == 'Milady'), None)
                
                punks_count = punk_holding.token_count if punk_holding else 0
                miladys_count = milady_holding.token_count if milady_holding else 0
                
                eth_balance = 0
                usdc = usdt = dai = 0
                
                for sb in holder.stablecoin_balances:
                    if sb.stablecoin_name == 'ETH':
                        eth_balance = sb.balance
                    elif sb.stablecoin_name == 'USDC':
                        usdc = sb.balance
                    elif sb.stablecoin_name == 'USDT':
                        usdt = sb.balance
                    elif sb.stablecoin_name == 'DAI':
                        dai = sb.balance
                
                row = {
                    'Address': holder.address[:10] + '...',
                    'Full Address': holder.address,
                    'Punks': punks_count,
                    'Miladys': miladys_count,
                    'ETH': f"{eth_balance:.4f}",
                    'USDC': f"${usdc:,.2f}",
                    'USDT': f"${usdt:,.2f}",
                    'DAI': f"${dai:,.2f}",
                    'Total': holder.total_stablecoins or 0,
                    'Total Display': f"${holder.total_stablecoins:,.2f}" if holder.total_stablecoins else "$0.00"
                }
                
                crossover_data.append(row)
            
            df_crossover = pd.DataFrame(crossover_data)
            
            # Apply filters
            df_filtered = df_crossover[
                (df_crossover['Punks'] >= min_punks) &
                (df_crossover['Miladys'] >= min_miladys) &
                (df_crossover['Total'] >= min_balance)
            ]
            
            st.markdown(f"**Showing {len(df_filtered)} of {len(crossover_holders)} crossover holders**")
            
            # Display table
            display_df = df_filtered.drop(columns=['Full Address', 'Total'])
            st.dataframe(display_df, width='stretch', hide_index=True, height=400)
            
            # Download button
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Download Crossover Data CSV",
                data=csv,
                file_name=f'milady_punks_crossover_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.info("No crossover holders found.")

st.markdown("---")

# All holders table
if filtered_holders:
    st.markdown("## 📋 All Holders")
    
    # Build full holders table
    holders_data = []
    
    for holder in sorted(filtered_holders, key=lambda h: h.total_stablecoins or 0, reverse=True):
        collections_owned = [h.collection.name for h in holder.holdings]
        
        eth_balance = 0
        for sb in holder.stablecoin_balances:
            if sb.stablecoin_name == 'ETH':
                eth_balance = sb.balance
                break
        
        holders_data.append({
            'Address': holder.address[:12] + '...',
            'Collections': ', '.join(collections_owned),
            'NFTs': holder.total_nfts,
            'ETH': f"{eth_balance:.4f}",
            'Stablecoins': f"${holder.total_stablecoins:,.2f}" if holder.total_stablecoins else "$0.00"
        })
    
    df_all = pd.DataFrame(holders_data)
    
    # Search filter
    search_term = st.text_input("🔍 Search by address", "")
    
    if search_term:
        df_all = df_all[df_all['Address'].str.contains(search_term, case=False)]
    
    st.dataframe(df_all, width='stretch', hide_index=True, height=500)
    
    # Download all data
    csv_all = df_all.to_csv(index=False)
    st.download_button(
        label="📥 Download All Holders CSV",
        data=csv_all,
        file_name=f'all_holders_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>💎 Milady & CryptoPunks Holder Analysis</p>
    <p style='font-size: 0.9rem;'>Data powered by Alchemy API • Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)

session.close()

