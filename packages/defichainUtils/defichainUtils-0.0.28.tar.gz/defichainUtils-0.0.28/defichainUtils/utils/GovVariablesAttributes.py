from __future__ import annotations
from dataclasses import dataclass

@dataclass
class AttributeType:
    Live      = 'l'
    Oracles   = 'o'
    Param     = 'a'
    Token     = 't'
    Poolpairs = 'p'
    Locks     = 'L'

@dataclass
class ParamIDs:
    DFIP2201  = 'a'
    DFIP2203  = 'b'
    TokenID   = 'c'
    Economy   = 'e'
    DFIP2206A = 'f'
    DFIP2206F = 'g'

@dataclass
class OracleIDs:
    Splits    = 'a'

@dataclass
class EconomyKeys:
    PaybackDFITokens  = 'a'
    PaybackTokens     = 'b'
    DFIP2203Current   = 'c'
    DFIP2203Burned    = 'd'
    DFIP2203Minted    = 'e'
    DFIP2206FCurrent  = 'f'
    DFIP2206FBurned   = 'g'
    DFIP2206FMinted   = 'h'
    DexTokens         = 'i'

@dataclass
class DFIPKeys:
    Active           = 'a'
    Premium          = 'b'
    MinSwap          = 'c'
    RewardPct        = 'd'
    BlockPeriod      = 'e'
    DUSDInterestBurn = 'g'
    DUSDLoanBurn     = 'h'
    StartBlock       = 'i'

@dataclass
class TokenKeys:
    PaybackDFI            = 'a'
    PaybackDFIFeePCT      = 'b'
    LoanPayback           = 'c'
    LoanPaybackFeePCT     = 'd'
    DexInFeePct           = 'e'
    DexOutFeePct          = 'f'
    DFIP2203Enabled       = 'g'
    FixedIntervalPriceId  = 'h'
    LoanCollateralEnabled = 'i'
    LoanCollateralFactor  = 'j'
    LoanMintingEnabled    = 'k'
    LoanMintingInterest   = 'l'
    Ascendant             = 'm'
    Descendant            = 'n'
    Epitaph               = 'o'

@dataclass
class PoolKeys:
    TokenAFeePCT = 'a'
    TokenBFeePCT = 'b'
    TokenAFeeDir = 'c'
    TokenBFeeDir = 'd'
