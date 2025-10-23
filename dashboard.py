"""
Comprehensive NFT Holder Analysis Dashboard
Multi-tab interface with deep analytics for Milady & CryptoPunks
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from database import get_session, NFTCollection, Holder, StablecoinBalance, NFTHolding, init_collections
from token_list import ALL_TOKENS, STABLECOINS, STABLECOIN_RECEIPTS
import config

# Page config
st.set_page_config(
    page_title="NFT Holder Analytics",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_collections()

# Session
session = get_session()

# Custom CSS for better visibility
st.markdown("""
<style>
    .stMetric {
        background-color: #1e1e1e;
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
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    p {
        color: #e0e0e0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def calculate_gini(values):
    """Calculate Gini coefficient for wealth inequality"""
    sorted_values = np.sort(values)
    n = len(values)
    cumsum = np.cumsum(sorted_values)
    return (2 * np.sum((np.arange(1, n + 1)) * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n

def get_wealth_tier(balance):
    """Categorize holder by balance"""
    if balance >= 1000000:
        return "🐋 Whale"
    elif balance >= 100000:
        return "🐬 Dolphin"
    elif balance >= 10000:
        return "🐟 Regular"
    elif balance >= 1000:
        return "🦐 Small"
    else:
        return "✨ Dust"

def get_sophistication_score(holder):
    """Calculate DeFi sophistication based on tokens held"""
    balances = holder.stablecoin_balances
    protocols = set()
    
    for bal in balances:
        token_name = bal.stablecoin_name
        if token_name.startswith('a'):  # Aave
            protocols.add('Aave')
        elif token_name.startswith('c'):  # Compound
            protocols.add('Compound')
        elif token_name.startswith('yv'):  # Yearn
            protocols.add('Yearn')
        elif 'Crv' in token_name or 'cvx' in token_name:  # Curve/Convex
            protocols.add('Curve/Convex')
        elif token_name == 'sDAI':
            protocols.add('MakerDAO')
    
    return len(protocols)

# Load all data
all_holders = session.query(Holder).all()
collections = session.query(NFTCollection).all()

# Title
st.title("💎 Comprehensive NFT Holder Analytics")
st.markdown("### Milady & CryptoPunks - Deep Dive Analysis")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏠 Overview",
    "💰 Stablecoin Deep Dive", 
    "👥 Holder Segmentation",
    "💗 Milady Analysis",
    "🔷 CryptoPunks Analysis",
    "🤝 Crossover",
    "🐋 Whales",
    "🔍 Explorer"
])

# ===== TAB 1: OVERVIEW =====
with tab1:
    st.header("📊 Portfolio Overview")

    # Calculate metrics
    total_holders = len(all_holders)
    holders_with_balance = [h for h in all_holders if h.total_stablecoins and h.total_stablecoins > 0]
    total_stablecoins = sum([h.total_stablecoins for h in all_holders if h.total_stablecoins])
    avg_balance = total_stablecoins / len(holders_with_balance) if holders_with_balance else 0

    # Top metrics
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("👥 Total Holders", f"{total_holders:,}")
    c2.metric("💰 With Stablecoins", f"{len(holders_with_balance):,}")
    c3.metric("💵 Total Value", f"${total_stablecoins:,.0f}")
    c4.metric("📊 Average", f"${avg_balance:,.0f}")

    # Calculate Gini coefficient
    balances = [h.total_stablecoins for h in holders_with_balance]
    gini = calculate_gini(np.array(balances)) if len(balances) > 1 else 0
    c5.metric("📈 Gini", f"{gini:.3f}", help="Inequality: 0=equal, 1=concentrated")

    st.markdown("---")

    # Collection comparison
    col1, col2 = st.columns(2)

    for idx, collection in enumerate(collections):
        with col1 if idx == 0 else col2:
            st.subheader(f"{'💗' if collection.name == 'Milady' else '🔷'} {collection.name}")

            # Get holders for this collection
            coll_holder_ids = [h.holder_id for h in collection.holdings]
            coll_holders = [h for h in all_holders if h.id in coll_holder_ids]
            coll_with_balance = [h for h in coll_holders if h.total_stablecoins and h.total_stablecoins > 0]
            coll_total = sum([h.total_stablecoins for h in coll_holders if h.total_stablecoins])
            coll_avg = coll_total / len(coll_with_balance) if coll_with_balance else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("Holders", f"{len(coll_holders):,}")
            c2.metric("With Balance", f"{len(coll_with_balance):,}")
            c3.metric("Avg Balance", f"${coll_avg:,.0f}")

            st.info(f"💰 Total: **${coll_total:,.0f}**")

    st.markdown("---")

    # Quick insights
    st.subheader("💡 Key Insights")
    
    # Top 10% concentration
    top_10_pct_count = max(1, len(holders_with_balance) // 10)
    top_10_pct_value = sum([h.total_stablecoins for h in sorted(holders_with_balance, key=lambda x: x.total_stablecoins, reverse=True)[:top_10_pct_count]])
    concentration = (top_10_pct_value / total_stablecoins * 100) if total_stablecoins > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🎯 Top 10% Hold", f"{concentration:.1f}%", help="Concentration of wealth in top 10% of holders")
    
    with col2:
        # Yield adoption
        yield_tokens = [t for t in STABLECOIN_RECEIPTS.keys()]
        holders_with_yield = len([h for h in all_holders if any(b.stablecoin_name in yield_tokens for b in h.stablecoin_balances)])
        yield_adoption = (holders_with_yield / len(holders_with_balance) * 100) if holders_with_balance else 0
        st.metric("🌾 Yield Adoption", f"{yield_adoption:.1f}%", help="% of holders using DeFi yield products")
    
    with col3:
        # Most popular stablecoin
        token_totals = {}
        for h in all_holders:
            for bal in h.stablecoin_balances:
                if bal.stablecoin_name in STABLECOINS:
                    token_totals[bal.stablecoin_name] = token_totals.get(bal.stablecoin_name, 0) + bal.balance
        
        if token_totals:
            most_popular = max(token_totals, key=token_totals.get)
            st.metric("👑 Top Token", most_popular)

# ===== TAB 2: STABLECOIN DEEP DIVE =====
with tab2:
    st.header("💰 Stablecoin Deep Dive")
    
    # Calculate token breakdown
    token_data = {}
    for h in all_holders:
        for bal in h.stablecoin_balances:
            token_name = bal.stablecoin_name
            if token_name != 'ETH':  # Exclude ETH from stablecoin analysis
                if token_name not in token_data:
                    token_data[token_name] = {'value': 0, 'holders': set(), 'is_yield': token_name in STABLECOIN_RECEIPTS}
                token_data[token_name]['value'] += bal.balance
                token_data[token_name]['holders'].add(h.id)
    
    # Convert to dataframe
    token_df = pd.DataFrame([
        {
            'Token': token,
            'Total Value': data['value'],
            'Holders': len(data['holders']),
            'Type': '🌾 Yield' if data['is_yield'] else '💵 Plain',
            'Avg per Holder': data['value'] / len(data['holders']) if data['holders'] else 0
        }
        for token, data in token_data.items()
        if data['value'] > 0
    ]).sort_values('Total Value', ascending=False)
    
    # Summary metrics
    plain_value = token_df[token_df['Type'] == '💵 Plain']['Total Value'].sum()
    yield_value = token_df[token_df['Type'] == '🌾 Yield']['Total Value'].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💵 Plain Stablecoins", f"${plain_value:,.0f}")

    with col2:
        st.metric("🌾 Yield-Bearing", f"${yield_value:,.0f}")

    with col3:
        yield_pct = (yield_value / (plain_value + yield_value) * 100) if (plain_value + yield_value) > 0 else 0
        st.metric("% in Yield", f"{yield_pct:.1f}%")

    st.markdown("---")

    # Token breakdown charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Token Distribution")
        fig = px.pie(
            token_df.head(10),
            values='Total Value',
            names='Token',
            title='Top 10 Tokens by Value',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Top Tokens")
        st.dataframe(
            token_df.head(15)[['Token', 'Total Value', 'Holders', 'Type']].style.format({
                'Total Value': '${:,.0f}'
            }),
            hide_index=True,
            use_container_width=True
        )
    
    # Protocol breakdown
    st.markdown("---")
    st.subheader("🏛️ DeFi Protocol Adoption")
    
    protocol_stats = {
        'Aave': {'holders': set(), 'value': 0},
        'Compound': {'holders': set(), 'value': 0},
        'Yearn': {'holders': set(), 'value': 0},
        'Curve/Convex': {'holders': set(), 'value': 0},
        'MakerDAO (sDAI)': {'holders': set(), 'value': 0}
    }
    
    for h in all_holders:
        for bal in h.stablecoin_balances:
            token = bal.stablecoin_name
            if token.startswith('a') and token in STABLECOIN_RECEIPTS:
                protocol_stats['Aave']['holders'].add(h.id)
                protocol_stats['Aave']['value'] += bal.balance
            elif token.startswith('c') and token in STABLECOIN_RECEIPTS:
                protocol_stats['Compound']['holders'].add(h.id)
                protocol_stats['Compound']['value'] += bal.balance
            elif token.startswith('yv'):
                protocol_stats['Yearn']['holders'].add(h.id)
                protocol_stats['Yearn']['value'] += bal.balance
            elif 'Crv' in token or 'cvx' in token:
                protocol_stats['Curve/Convex']['holders'].add(h.id)
                protocol_stats['Curve/Convex']['value'] += bal.balance
            elif token == 'sDAI':
                protocol_stats['MakerDAO (sDAI)']['holders'].add(h.id)
                protocol_stats['MakerDAO (sDAI)']['value'] += bal.balance
    
    protocol_df = pd.DataFrame([
        {
            'Protocol': proto,
            'Users': len(data['holders']),
            'Total Value': data['value'],
            'Avg per User': data['value'] / len(data['holders']) if data['holders'] else 0
        }
        for proto, data in protocol_stats.items()
        if data['value'] > 0
    ]).sort_values('Total Value', ascending=False)
    
    if not protocol_df.empty:
        fig = px.bar(
            protocol_df,
            x='Protocol',
            y='Total Value',
            color='Users',
            title='DeFi Protocol Usage',
            labels={'Total Value': 'Total Value ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)

# ===== TAB 3: HOLDER SEGMENTATION =====
with tab3:
    st.header("👥 Holder Segmentation Analysis")
    
    # Categorize holders by wealth tier
    wealth_tiers = {
        '🐋 Whale (>$1M)': [],
        '🐬 Dolphin ($100K-$1M)': [],
        '🐟 Regular ($10K-$100K)': [],
        '🦐 Small ($1K-$10K)': [],
        '✨ Dust (<$1K)': []
    }
    
    for h in holders_with_balance:
        tier = get_wealth_tier(h.total_stablecoins)
        for tier_name in wealth_tiers.keys():
            if tier in tier_name:
                wealth_tiers[tier_name].append(h)
                break
    
    # Wealth tier metrics
    st.subheader("💰 Wealth Tier Distribution")
    
    tier_data = []
    for tier_name, tier_holders in wealth_tiers.items():
        if tier_holders:
            tier_total = sum([h.total_stablecoins for h in tier_holders])
            tier_avg = tier_total / len(tier_holders)
            tier_pct = (tier_total / total_stablecoins * 100) if total_stablecoins > 0 else 0
            
            tier_data.append({
                'Tier': tier_name,
                'Count': len(tier_holders),
                'Total Value': tier_total,
                '% of Total': tier_pct,
                'Avg Balance': tier_avg
            })
    
    tier_df = pd.DataFrame(tier_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tier distribution pie
        fig = px.pie(
            tier_df,
            values='Count',
            names='Tier',
            title='Holder Distribution by Tier',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Value distribution
        fig = px.bar(
            tier_df,
            x='Tier',
            y='% of Total',
            title='% of Total Value by Tier',
            color='% of Total',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(tier_df.style.format({
        'Total Value': '${:,.0f}',
        '% of Total': '{:.1f}%',
        'Avg Balance': '${:,.0f}'
    }), use_container_width=True, hide_index=True)

# ===== TAB 4: MILADY ANALYSIS =====
with tab4:
    st.header("💗 Milady Collection Deep Dive")
    
    milady_coll = next((c for c in collections if c.name == 'Milady'), None)
    
    if milady_coll:
        milady_holder_ids = [h.holder_id for h in milady_coll.holdings]
        milady_holders = [h for h in all_holders if h.id in milady_holder_ids]
        milady_with_balance = [h for h in milady_holders if h.total_stablecoins and h.total_stablecoins > 0]
        milady_total = sum([h.total_stablecoins for h in milady_holders if h.total_stablecoins])
        milady_avg = milady_total / len(milady_with_balance) if milady_with_balance else 0
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Holders", f"{len(milady_holders):,}")
        
        with col2:
            st.metric("💰 With Stablecoins", f"{len(milady_with_balance):,}")
        
        with col3:
            st.metric("💵 Total Value", f"${milady_total:,.0f}")
        
        with col4:
            st.metric("📊 Average", f"${milady_avg:,.0f}")
        
        st.markdown("---")
        
        # Milady-specific token preferences
        st.subheader("🪙 Token Preferences")
        
        milady_tokens = {}
        for h in milady_holders:
            for bal in h.stablecoin_balances:
                token = bal.stablecoin_name
                if token != 'ETH':
                    milady_tokens[token] = milady_tokens.get(token, 0) + bal.balance
        
        if milady_tokens:
            milady_token_df = pd.DataFrame([
                {'Token': k, 'Value': v}
                for k, v in sorted(milady_tokens.items(), key=lambda x: x[1], reverse=True)
            ]).head(10)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    milady_token_df,
                    x='Token',
                    y='Value',
                    title='Top 10 Tokens in Milady Wallets',
            color='Value',
                    color_continuous_scale='Pinkyl'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Wealth distribution
                milady_balances = [h.total_stablecoins for h in milady_with_balance]
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=milady_balances,
                    nbinsx=30,
                    name='Milady Holders',
                    marker_color='#FF6B9D'
                ))
                fig.update_layout(
                    title='Milady Balance Distribution',
                    xaxis_title='Balance ($)',
                    yaxis_title='Number of Holders',
                    showlegend=False
                )
                fig.update_xaxes(type="log")
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Top Milady holders
        st.subheader("🏆 Top 20 Milady Holders")
        
        top_milady = sorted(milady_with_balance, key=lambda x: x.total_stablecoins, reverse=True)[:20]
        
        milady_top_data = []
        for h in top_milady:
            milady_nfts = next((holding.token_count for holding in h.holdings if holding.collection.name == 'Milady'), 0)
            milady_top_data.append({
                'Address': h.address[:12] + '...',
                'Miladys Owned': milady_nfts,
                'Stablecoins': h.total_stablecoins,
                'Protocols': get_sophistication_score(h)
            })
        
        st.dataframe(
            pd.DataFrame(milady_top_data).style.format({'Stablecoins': '${:,.0f}'}),
            use_container_width=True,
            hide_index=True
        )

# ===== TAB 5: CRYPTOPUNKS ANALYSIS =====
with tab5:
    st.header("🔷 CryptoPunks Collection Deep Dive")
    
    punk_coll = next((c for c in collections if c.name == 'CryptoPunks'), None)
    
    if punk_coll:
        punk_holder_ids = [h.holder_id for h in punk_coll.holdings]
        punk_holders = [h for h in all_holders if h.id in punk_holder_ids]
        punk_with_balance = [h for h in punk_holders if h.total_stablecoins and h.total_stablecoins > 0]
        punk_total = sum([h.total_stablecoins for h in punk_holders if h.total_stablecoins])
        punk_avg = punk_total / len(punk_with_balance) if punk_with_balance else 0
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Holders", f"{len(punk_holders):,}")
        
        with col2:
            st.metric("💰 With Stablecoins", f"{len(punk_with_balance):,}")
        
        with col3:
            st.metric("💵 Total Value", f"${punk_total:,.0f}")
        
        with col4:
            st.metric("📊 Average", f"${punk_avg:,.0f}")
        
        st.markdown("---")
        
        # Punk-specific analysis
        st.subheader("🪙 Token Preferences")
        
        punk_tokens = {}
        for h in punk_holders:
            for bal in h.stablecoin_balances:
                token = bal.stablecoin_name
                if token != 'ETH':
                    punk_tokens[token] = punk_tokens.get(token, 0) + bal.balance
        
        if punk_tokens:
            punk_token_df = pd.DataFrame([
                {'Token': k, 'Value': v}
                for k, v in sorted(punk_tokens.items(), key=lambda x: x[1], reverse=True)
            ]).head(10)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    punk_token_df,
                    x='Token',
                    y='Value',
                    title='Top 10 Tokens in Punk Wallets',
                    color='Value',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Wealth distribution
                punk_balances = [h.total_stablecoins for h in punk_with_balance]
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=punk_balances,
                    nbinsx=30,
                    name='Punk Holders',
                    marker_color='#4A90E2'
                ))
                fig.update_layout(
                    title='CryptoPunks Balance Distribution',
                    xaxis_title='Balance ($)',
                    yaxis_title='Number of Holders',
                    showlegend=False
                )
                fig.update_xaxes(type="log")
                st.plotly_chart(fig, use_container_width=True)

# ===== TAB 6: CROSSOVER ANALYSIS =====
with tab6:
    st.header("🤝 Crossover Holder Analysis")
    
    if len(collections) >= 2:
        milady_ids = set([h.holder_id for h in collections[0].holdings])
        punk_ids = set([h.holder_id for h in collections[1].holdings])
        crossover_ids = milady_ids.intersection(punk_ids)
        milady_only_ids = milady_ids - punk_ids
        punk_only_ids = punk_ids - milady_ids
        
        crossover_holders = [h for h in all_holders if h.id in crossover_ids]
        milady_only_holders = [h for h in all_holders if h.id in milady_only_ids]
        punk_only_holders = [h for h in all_holders if h.id in punk_only_ids]
        
        # Calculate stats
        crossover_total = sum([h.total_stablecoins for h in crossover_holders if h.total_stablecoins])
        crossover_with_bal = [h for h in crossover_holders if h.total_stablecoins and h.total_stablecoins > 0]
        crossover_avg = crossover_total / len(crossover_with_bal) if crossover_with_bal else 0
        
        milady_only_total = sum([h.total_stablecoins for h in milady_only_holders if h.total_stablecoins])
        milady_only_with_bal = [h for h in milady_only_holders if h.total_stablecoins and h.total_stablecoins > 0]
        milady_only_avg = milady_only_total / len(milady_only_with_bal) if milady_only_with_bal else 0
        
        punk_only_total = sum([h.total_stablecoins for h in punk_only_holders if h.total_stablecoins])
        punk_only_with_bal = [h for h in punk_only_holders if h.total_stablecoins and h.total_stablecoins > 0]
        punk_only_avg = punk_only_total / len(punk_only_with_bal) if punk_only_with_bal else 0
        
        # Comparison metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🤝 Both Collections")
            st.metric("Count", f"{len(crossover_holders):,}")
            st.metric("Total Value", f"${crossover_total:,.0f}")
            st.metric("Avg (Non-Zero)", f"${crossover_avg:,.0f}")
        
        with col2:
            st.markdown("### 💗 Milady Only")
            st.metric("Count", f"{len(milady_only_holders):,}")
            st.metric("Total Value", f"${milady_only_total:,.0f}")
            st.metric("Avg (Non-Zero)", f"${milady_only_avg:,.0f}")
        
        with col3:
            st.markdown("### 🔷 Punks Only")
            st.metric("Count", f"{len(punk_only_holders):,}")
            st.metric("Total Value", f"${punk_only_total:,.0f}")
            st.metric("Avg (Non-Zero)", f"${punk_only_avg:,.0f}")
        
        st.markdown("---")
        
        # Hypothesis: Are crossover holders richer?
        st.subheader("💡 Key Finding")
        
        if crossover_avg > 0 and milady_only_avg > 0:
            multiplier = crossover_avg / ((milady_only_avg + punk_only_avg) / 2)
            st.success(f"🔍 Crossover holders are **{multiplier:.1f}x richer** on average than single-collection holders!")
        
        # Venn diagram-style visualization
        st.subheader("📊 Collection Overlap")
        
        venn_data = {
            'Category': ['Milady Only', 'Both', 'Punks Only'],
            'Holders': [len(milady_only_holders), len(crossover_holders), len(punk_only_holders)],
            'Total Value': [milady_only_total, crossover_total, punk_only_total]
        }
        
        venn_df = pd.DataFrame(venn_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                venn_df,
                x='Category',
                y='Holders',
                title='Holder Count by Category',
                color='Category',
                color_discrete_map={
                    'Milady Only': '#FF6B9D',
                    'Both': '#9B59B6',
                    'Punks Only': '#4A90E2'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                venn_df,
                x='Category',
                y='Total Value',
                title='Total Value by Category',
                color='Category',
                color_discrete_map={
                    'Milady Only': '#FF6B9D',
                    'Both': '#9B59B6',
                    'Punks Only': '#4A90E2'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

# ===== TAB 7: WHALE ANALYSIS =====
with tab7:
    st.header("🐋 Whale Analysis")
    
    # Top 100 holders
    top_100 = sorted(holders_with_balance, key=lambda x: x.total_stablecoins, reverse=True)[:100]
    top_100_total = sum([h.total_stablecoins for h in top_100])
    top_100_pct = (top_100_total / total_stablecoins * 100) if total_stablecoins > 0 else 0
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🐋 Top 100 Hold", f"${top_100_total:,.0f}")
    
    with col2:
        st.metric("📊 % of Total", f"{top_100_pct:.1f}%")
    
    with col3:
        st.metric("💎 Avg Whale", f"${top_100_total/100:,.0f}")
    
    with col4:
        top_10_total = sum([h.total_stablecoins for h in top_100[:10]])
        top_10_pct = (top_10_total / total_stablecoins * 100) if total_stablecoins > 0 else 0
        st.metric("🎯 Top 10 Hold", f"{top_10_pct:.1f}%")
    
    st.markdown("---")
    
    # Top holders table
    st.subheader("🏆 Top 50 Holders")
    
    whale_data = []
    for rank, h in enumerate(top_100[:50], 1):
        collections_owned = [holding.collection.name for holding in h.holdings]
        whale_data.append({
            'Rank': rank,
            'Address': h.address[:14] + '...',
            'Collections': ', '.join(collections_owned),
            'Stablecoins': h.total_stablecoins,
            'Tier': get_wealth_tier(h.total_stablecoins),
            'DeFi Score': get_sophistication_score(h)
        })
    
    st.dataframe(
        pd.DataFrame(whale_data).style.format({'Stablecoins': '${:,.0f}'}),
        use_container_width=True,
        hide_index=True,
        height=600
    )
    
    st.markdown("---")
    
    # Concentration curve
    st.subheader("📈 Wealth Concentration")
    
    sorted_balances = sorted([h.total_stablecoins for h in holders_with_balance], reverse=True)
    cumulative_pct = np.cumsum(sorted_balances) / sum(sorted_balances) * 100
    holder_pct = np.arange(1, len(sorted_balances) + 1) / len(sorted_balances) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=holder_pct,
        y=cumulative_pct,
        mode='lines',
        name='Cumulative Wealth',
        fill='tozeroy'
    ))
    fig.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode='lines',
        name='Perfect Equality',
        line=dict(dash='dash', color='red')
    ))
    fig.update_layout(
        title='Lorenz Curve - Wealth Concentration',
        xaxis_title='% of Holders (poorest to richest)',
        yaxis_title='% of Total Wealth',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# ===== TAB 8: WALLET EXPLORER =====
with tab8:
    st.header("🔍 Wallet Explorer")
    
    # Search
    search_address = st.text_input("🔎 Enter wallet address:")
    
    if search_address:
        found_holder = next((h for h in all_holders if search_address.lower() in h.address.lower()), None)
        
        if found_holder:
            st.success(f"✅ Found: {found_holder.address}")
            
            # Holder details
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                nft_count = sum([holding.token_count for holding in found_holder.holdings])
                st.metric("NFTs Owned", nft_count)
            
            with col2:
                st.metric("Stablecoins", f"${found_holder.total_stablecoins or 0:,.2f}")
            
            with col3:
                collections_owned = [holding.collection.name for holding in found_holder.holdings]
                st.metric("Collections", len(collections_owned))
            
            with col4:
                soph_score = get_sophistication_score(found_holder)
                st.metric("DeFi Protocols", soph_score)
            
            st.markdown("---")
            
            # Collections owned
            st.subheader("🎨 NFT Holdings")
            for holding in found_holder.holdings:
                st.info(f"**{holding.collection.name}**: {holding.token_count} NFT(s)")
            
            # Token balances
            st.subheader("💰 Token Balances")
            
            if found_holder.stablecoin_balances:
                balance_data = []
                for bal in found_holder.stablecoin_balances:
                    if bal.balance > 0:
                        balance_data.append({
                            'Token': bal.stablecoin_name,
                            'Balance': bal.balance,
                            'Type': '🌾 Yield' if bal.stablecoin_name in STABLECOIN_RECEIPTS else '💵 Plain'
                        })
                
                if balance_data:
                    st.dataframe(
                        pd.DataFrame(balance_data).sort_values('Balance', ascending=False).style.format({'Balance': '${:,.2f}'}),
                        use_container_width=True,
                        hide_index=True
                    )
            else:
                st.info("No stablecoin balances found")
        else:
            st.warning("Address not found in database")

    st.markdown("---")

    # Browse all holders
    st.subheader("📋 Browse All Holders")

    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_balance = st.number_input("Min Balance ($)", min_value=0, value=0, step=1000)
    
    with col2:
        collection_filter = st.selectbox("Collection", ["All", "Milady", "CryptoPunks", "Both"])
    
    with col3:
        sort_by = st.selectbox("Sort By", ["Stablecoins (High)", "Stablecoins (Low)", "NFTs Owned"])
    
    # Apply filters
    filtered_holders = holders_with_balance
    
    if min_balance > 0:
        filtered_holders = [h for h in filtered_holders if h.total_stablecoins >= min_balance]
    
    if collection_filter != "All":
        if collection_filter == "Both":
            milady_ids = set([h.holder_id for h in milady_coll.holdings])
            punk_ids = set([h.holder_id for h in punk_coll.holdings])
            both_ids = milady_ids.intersection(punk_ids)
            filtered_holders = [h for h in filtered_holders if h.id in both_ids]
        else:
            coll = next((c for c in collections if c.name == collection_filter), None)
            if coll:
                coll_ids = set([h.holder_id for h in coll.holdings])
                filtered_holders = [h for h in filtered_holders if h.id in coll_ids]
    
    # Sort
    if sort_by == "Stablecoins (High)":
        filtered_holders = sorted(filtered_holders, key=lambda x: x.total_stablecoins, reverse=True)
    elif sort_by == "Stablecoins (Low)":
        filtered_holders = sorted(filtered_holders, key=lambda x: x.total_stablecoins)
    else:
        filtered_holders = sorted(filtered_holders, key=lambda x: x.total_nfts, reverse=True)
    
    # Display
    browse_data = []
    for h in filtered_holders[:100]:  # Limit to 100 for performance
        collections_owned = [holding.collection.name for holding in h.holdings]
        browse_data.append({
            'Address': h.address[:16] + '...',
            'Collections': ', '.join(collections_owned),
            'NFTs': h.total_nfts,
            'Stablecoins': h.total_stablecoins,
            'Wealth Tier': get_wealth_tier(h.total_stablecoins)
        })
    
    st.write(f"Showing {len(browse_data)} of {len(filtered_holders)} holders")
    
    st.dataframe(
        pd.DataFrame(browse_data).style.format({'Stablecoins': '${:,.0f}'}),
        use_container_width=True,
        hide_index=True,
        height=500
    )

# Close session
session.close()

