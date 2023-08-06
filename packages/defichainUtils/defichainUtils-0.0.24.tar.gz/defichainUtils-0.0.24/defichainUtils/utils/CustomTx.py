import defichainUtils.utils.utils as utils
#import utils.utils as utils
from dataclasses import dataclass, is_dataclass



DECIMALS = 100000000
class DfTx():
    def __init__(self):
        self.params = []
        self.DfTxMarker = 'DfTx'
    
    def hex(self):
        h = self.DfTxMarker.encode('utf-8').hex()
        lengthInfo = ''
        for i,p in enumerate(self.params):
            h = h + self.__handleParam(p,i==0)
            # TODO: This part is not understood yet. It is a workaround. Some Functions have 4c before the Byte handling the length. Some not. Semms to depend on length. 
            if i == 0 and p not in [CustomTxType.DepositToVault]:
                lengthInfo = '4c'

        return OPCodes.OP_RETURN + lengthInfo + utils.int2hex(int(len(h)/2),'little') + h

    def __handleParam(self,p,isCustomTxType=False):
        if isCustomTxType:
            return p.encode('utf-8').hex()
        elif not is_dataclass(p):
            return p
        
        
        if p.__class__.__name__ == 'Vault':
            return utils.convert_hex(p.value,'big','little')
        elif p.__class__.__name__ == 'Address':
            return utils.encodeBech32AddressToHex(p.value)
        # elif p.__class__.__name__ == 'Addresses':
        #     h = ''
        #     for address in p.value:
        #         h = h + encodeBech32AddressToHex(address)
        #     return int2hex(len(p.value),'little') + h
        elif p.__class__.__name__ == 'Amounts':
            h = ''
            for amount in p.value:
                h = h + utils.int2hex(amount[1],'little',4) + utils.int2hex(int(amount[0]*DECIMALS),'little',8)
            return utils.int2hex(len(p.value),'little') + h
        elif p.__class__.__name__ == 'AddressesWithAmount':
            d = p.toDict()
            h = ''
            for address in d:
                # 01 means, count of addresses (=1)
                h = h + '01' + utils.encodeBech32AddressToHex(address) + utils.int2hex(len(d[address].keys()),'little')
                for tokenId in d[address]:
                    h = h + utils.int2hex(tokenId,'little',4) + utils.int2hex(int(d[address][tokenId]*DECIMALS),'little',8)
            return h
        else:
            return ''

@dataclass
class CustomTxType:
    Reject:str = 1
    # masternodes:
    CreateMasternode:str = 'C'
    ResignMasternode:str = 'R'
    UpdateMasternode:str = 'm'
    SetForcedRewardAddress:str = 'F'
    RemForcedRewardAddress:str = 'f'
    
    # custom tokens:
    CreateToken:str = 'T'
    MintToken:str   = 'M'
    UpdateToken:str = 'N' # previous type, only DAT flag triggers
    UpdateTokenAny:str = 'n' # new type of token's update with any flags/fields possible
    
    # dex orders - just not to overlap in future
    # CreateOrder:str = 'O'
    # DestroyOrder:str = 'E'
    # MatchOrders:str = 'A'
    
    # poolpair
    CreatePoolPair:str = 'p'
    UpdatePoolPair:str = 'u'
    PoolSwap:str = 's'
    PoolSwapV2:str = 'i'
    AddPoolLiquidity:str = 'l'
    RemovePoolLiquidity:str = 'r'
    
    # accounts
    UtxosToAccount:str = 'U'
    AccountToUtxos:str = 'b'
    AccountToAccount:str = 'B'
    AnyAccountsToAccounts = 'a'
    SmartContract:str = 'K'
    DFIP2203:str = 'Q'
    # set governance variable
    SetGovVariable:str = 'G'
    SetGovVariableHeight:str = 'j'
    # Auto auth TX
    AutoAuthPrep:str  = 'A'
    # oracles
    AppointOracle:str = 'o'
    RemoveOracleAppoint:str = 'h'
    UpdateOracleAppoint:str = 't'
    SetOracleData:str = 'y'
    # ICX
    ICXCreateOrder:str = '1'
    ICXMakeOffer:str = '2'
    ICXSubmitDFCHTLC:str = '3'
    ICXSubmitEXTHTLC:str = '4'
    ICXClaimDFCHTLC:str = '5'
    ICXCloseOrder:str = '6'
    ICXCloseOffer:str = '7'
    
    # Loans
    SetLoanCollateralToken:str = 'c'
    SetLoanToken:str = 'g'
    UpdateLoanToken:str = 'x'
    LoanScheme:str = 'L'
    DefaultLoanScheme:str = 'd'
    DestroyLoanScheme:str = 'D'
    Vault:str = 'V'
    CloseVault:str = 'e'
    UpdateVault:str = 'v'
    DepositToVault:str = 'S'
    WithdrawFromVault:str = 'J'
    TakeLoan:str = 'X'
    PaybackLoan:str = 'H'
    PaybackLoanV2:str = 'k'
    AuctionBid:str = 'I'
    
    # Marker TXs
    FutureSwapExecution:str = 'q'
    FutureSwapRefund:str = 'w'

@dataclass
class OPCodes:
    OP_RETURN:str = '6a'