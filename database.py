"""Database models and operations - Enhanced to store raw API data"""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import config
import json

Base = declarative_base()

class NFTCollection(Base):
    __tablename__ = 'nft_collections'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    contract_address = Column(String, nullable=False)
    total_holders = Column(Integer, default=0)
    total_supply = Column(Integer, default=0)
    last_fetched = Column(DateTime, default=datetime.utcnow)
    raw_api_response = Column(Text)  # Store full Alchemy response as JSON
    
    holdings = relationship("NFTHolding", back_populates="collection", cascade="all, delete-orphan")

class Holder(Base):
    __tablename__ = 'holders'
    
    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    total_nfts = Column(Integer, default=0)
    total_stablecoins = Column(Float, default=0.0)
    total_eth = Column(Float, default=0.0)
    total_wallet_value = Column(Float, default=0.0)
    last_updated = Column(DateTime)
    last_analyzed = Column(DateTime)
    raw_balance_response = Column(Text)  # Store full balance API response
    
    holdings = relationship("NFTHolding", back_populates="holder", cascade="all, delete-orphan")
    stablecoin_balances = relationship("StablecoinBalance", back_populates="holder", cascade="all, delete-orphan")

class NFTHolding(Base):
    __tablename__ = 'nft_holdings'
    
    id = Column(Integer, primary_key=True)
    holder_id = Column(Integer, ForeignKey('holders.id'))
    collection_id = Column(Integer, ForeignKey('nft_collections.id'))
    token_count = Column(Integer, default=1)
    token_ids = Column(Text)  # JSON array of token IDs
    raw_tokens_data = Column(Text)  # Full token metadata from API
    
    holder = relationship("Holder", back_populates="holdings")
    collection = relationship("NFTCollection", back_populates="holdings")

class StablecoinBalance(Base):
    __tablename__ = 'stablecoin_balances'
    
    id = Column(Integer, primary_key=True)
    holder_id = Column(Integer, ForeignKey('holders.id'))
    stablecoin_name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    raw_balance = Column(String)  # Store actual wei/raw value
    decimals = Column(Integer, default=18)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    holder = relationship("Holder", back_populates="stablecoin_balances")

# Create database engine and session with WAL mode for better concurrency
engine = create_engine(
    f'sqlite:///{config.DB_PATH}',
    connect_args={
        'timeout': 30,  # 30 second timeout for locks
        'check_same_thread': False
    },
    pool_pre_ping=True
)

# Enable WAL mode for better concurrent access
with engine.connect() as conn:
    conn.execute(text('PRAGMA journal_mode=WAL'))
    conn.execute(text('PRAGMA synchronous=NORMAL'))
    conn.commit()

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    """Get a new database session"""
    return Session()

def init_collections():
    """Initialize NFT collections in database"""
    session = get_session()
    try:
        for name, address in config.NFT_CONTRACTS.items():
            existing = session.query(NFTCollection).filter_by(name=name).first()
            if not existing:
                collection = NFTCollection(
                    name=name, 
                    contract_address=address,
                    total_supply=10000 if name == 'Milady' else 10000  # Known supply
                )
                session.add(collection)
        session.commit()
    finally:
        session.close()

def wipe_all_data():
    """Wipe all data from database (keep schema)"""
    session = get_session()
    try:
        print("🗑️  Wiping all data from database...")
        session.query(StablecoinBalance).delete()
        session.query(NFTHolding).delete()
        session.query(Holder).delete()
        session.query(NFTCollection).delete()
        session.commit()
        print("✅ Database wiped clean!")
    except Exception as e:
        session.rollback()
        print(f"❌ Error wiping database: {e}")
    finally:
        session.close()
