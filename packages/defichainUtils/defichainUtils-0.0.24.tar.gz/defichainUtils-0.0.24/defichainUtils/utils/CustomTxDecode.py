import defichainUtils.utils.utils as utils
#import utils.utils as utils

def decodeCustomTx(hex):
    '''
    Hex String without OP_RETURN and DfTx Marker
    ''' 
    functionMarker = utils.hexToString(hex[:2])
    if functionMarker == 'j':
        res = decodeSetGovVariableHeight(hex[2:])
        if res != None:
            res['name'] = 'setgovheight'
    elif functionMarker == 's':
        res = decodePoolSwap(hex[2:])
        if res != None:
            res['name'] = 'poolswap'
    elif functionMarker == 'i':
        res = decodePoolSwapV2(hex[2:])
        if res != None:
            res['name'] = 'compositeswap'
    elif functionMarker == 'l':
        res = decodeAddPoolLiquidity(hex[2:])
        if res != None:
            res['name'] = 'addpoolliquidity'
    elif functionMarker == 'r':
        res = decodeRemovePoolLiquidity(hex[2:])
        if res != None:
            res['name'] = 'removepoolliquidity'
    else:
        return None
    return res


def decodeSetGovVariableHeight(hex):
    # Only data part of hex string!
    govVariable = hex[2:2+2*int(hex[:2],16)]
    hex = hex[2+2*int(hex[:2],16):]
    if utils.stringToHex('ATTRIBUTES') == govVariable:
        # if hex[:2] != '01':
        #     return {
        #         'error': 1,
        #         'msg': 'Expected only one value in this function. Please contact package DEV.'
        #     }
        variables = [
            {'key':'attributes', 'type': [
                {'bytesCount': 4, 'key': None, 'type': int,'endian':None},
                {'bytesCount': 1, 'key': 'type', 'type': str,'endian':None},
                {'bytesCount': 1, 'key': 'typeId', 'type': int,'endian':None},
                {'bytesCount': 4, 'key': 'key', 'type': str,'endian':'big'},
                {'bytesCount': 4, 'key': 'keyId', 'type': int,'endian':'little'},
                {'bytesCount': 8, 'key': 'value', 'type': int,'endian':'little'}]
            },
            {'bytesCount': 4, 'key': 'height', 'type': int,'endian':'little'}
        ]
        return searchHex(variables,hex)
    elif utils.stringToHex('ICX_TAKERFEE_PER_BTC') == govVariable:
        # TODO: write Decoding
        pass
    elif utils.stringToHex('LP_LOAN_TOKEN_SPLITS') == govVariable:
        # TODO: write Decoding
        pass
    elif utils.stringToHex('LP_SPLITS') == govVariable:
        # TODO: write Decoding
        pass
    elif utils.stringToHex('ORACLE_DEVIATION') == govVariable:
        # TODO: write Decoding
        pass
    else:
        return None

def decodePoolSwap(hex):
    variables = [
        {'key': 'from', 'type': 'address','endian':None},
        {'bytesCount':1, 'key': 'fromTokenId', 'type': int,'endian':None},
        {'bytesCount': 8, 'key': 'fromAmount', 'type': int,'endian':'big'},
        {'key': 'to', 'type': 'address','endian':None},
        {'bytesCount':1, 'key': 'toTokenId', 'type': int,'endian':None},
        {'bytesCount': 8, 'key': 'maxPriceCounter', 'type': int,'endian':'big'},
        {'bytesCount': 8, 'key': 'maxPriceDenominator', 'type': int,'endian':'big'}
    ]
    return searchHex(variables,hex)
def decodePoolSwapV2(hex):
    variables = [
        {'key': 'from', 'type': 'address','endian':None},
        {'bytesCount':1, 'key': 'fromTokenId', 'type': int,'endian':None},
        {'bytesCount': 8, 'key': 'fromAmount', 'type': int,'endian':'big'},
        {'key': 'to', 'type': 'address','endian':None},
        {'bytesCount':1, 'key': 'toTokenId', 'type': int,'endian':None},
        {'bytesCount': 8, 'key': 'maxPriceCounter', 'type': int,'endian':'big'},
        {'bytesCount': 8, 'key': 'maxPriceDenominator', 'type': int,'endian':'big'},
        {'key':'pools', 'type':
            [{'bytesCount': 1, 'type': int,'endian':None}]
        }
    ]
    return searchHex(variables,hex)
def decodeAddPoolLiquidity(hex):
    variables = [
        {'key':'addresses', 'type': [
            {'key': 'from', 'type': 'address','endian':None},
            {'key': 'amounts', 'type': [
                {'bytesCount': 4,'key': 'tokenId', 'type': int,'endian':'big'},
                {'bytesCount': 8, 'key': 'amount', 'type': int,'endian':'big'}
                ]}
        ]},
        {'key': 'shareAddress', 'type': 'address','endian':None}
    ]
    return searchHex(variables,hex)
def decodeRemovePoolLiquidity(hex):
    variables = [
        {'key': 'from', 'type': 'address','endian':None},
        {'bytesCount':1, 'key': 'tokenId', 'type': int,'endian':None},
        {'bytesCount': 8, 'key': 'amount', 'type': int,'endian':'big'}
    ]
    return searchHex(variables,hex)

def recursiveSearchHex(variable,hex):
    if type(variable['type']) == list:
        cnt = int(hex[:2],16)
        hex = hex[2:]
        arr = []
        for i in range(0,cnt):
            res = {}
            for idx,listVariable in enumerate(variable['type']):
                (key,value,hex) = recursiveSearchHex(listVariable,hex)
                if key is None and idx == len(variable['type']) - 1:
                    res = value
                else:
                    res[key] = value
            arr.append(res)
        return variable['key'],arr,hex
    else:
        return getValue(variable,hex)

def searchHex(variables:list,hex:str):
    res = {}
    for variable in variables:
        (key,value,hex) = recursiveSearchHex(variable,hex)
        res[key] = value
   
    return res

def getValue(variable,hex):
    # Select subString from hex depending on length info in hex String or length info from variable input
    if variable['type'] == 'address':
        # START - Remove leading zeros
        while True:
            if len(hex) >= 2 and hex[:2] == '00':
                hex = hex[2:]
            else:
                break
        if len(hex) < 2:
            return None,None,None
        # END - Remove leading zeros
        hexLength = int(hex[:2],16)
        if hex[2:6] == '76a9' and hexLength == 25:
            addressType = 'base58'
            addressVersion = 18
            addressLength = int(hex[6:8],16)
            hexOfInterest = hex[8:8+2*addressLength]
            hex = hex[2+2*hexLength:]
        elif hex[2:4] == 'a9' and hexLength == 23: 
            addressType = 'base58'
            addressVersion = 90
            addressLength = int(hex[4:6],16)
            hexOfInterest = hex[6:6+2*addressLength]
            hex = hex[2+2*hexLength:]
        else:
            addressType = 'bech32'
            addressVersion = hex[2:4]
            addressLength = int(hex[4:6],16)
            hexOfInterest = hex[6:6+2*addressLength]
            hex = hex[2+2*hexLength:]
    else:
        hexOfInterest = hex[:2*variable['bytesCount']]
        hex = hex[2*variable['bytesCount']:]

    # Handle Endian Transformation
    if variable['endian'] == 'big':
        hexOfInterest = utils.convert_hex(hexOfInterest,'big','little')
    elif variable['endian'] == 'little':
        hexOfInterest = utils.convert_hex(hexOfInterest,'little','big')

    # Extract Value
    if variable['type'] == int:
        if hexOfInterest == '':
            valueOfInterest = 0
        else:
            valueOfInterest = int(hexOfInterest,16)
    elif variable['type'] == str:
        if hexOfInterest == '':
            valueOfInterest = hexOfInterest
        else:
            valueOfInterest = utils.hexToString(hexOfInterest)
    elif variable['type'] == 'address':
        valueOfInterest = utils.decodeHexToAddress(hexOfInterest,addressType,addressVersion)
    else:
        valueOfInterest = None
    
    if 'key' not in variable:
        return None,valueOfInterest,hex
    if variable['key'] != None:
        return variable['key'],valueOfInterest,hex
    return None,None,hex