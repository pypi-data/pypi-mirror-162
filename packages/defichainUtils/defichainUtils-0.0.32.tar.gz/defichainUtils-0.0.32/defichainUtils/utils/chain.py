import math

MINIMUM_LIQUIDITY = 1000
SLOPE_SWAP_RATE = 1000
# https://github.com/DeFiCh/ain/blob/master/src/chainparams.cpp
BAY_FRONT_GARDENS_HEIGHT = 488300
FORT_CANNING_HILL_HEIGHT = 1604999

def addPoolLiquidity(amountA,amountB,reserveA,reserveB,totalLiquidity):
    # No Checks included! Only useable for valid block transactions!
    # https://github.com/DeFiCh/ain/blob/a7d914f15f762d121ac2c5d07d38d30cf7e09d4d/src/masternodes/poolpairs.cpp
    if totalLiquidity == 0:
        liquidity = int(math.sqrt(amountA*amountB))
        if liquidity < MINIMUM_LIQUIDITY:
            return 0
        else:
            return liquidity - MINIMUM_LIQUIDITY

    liqA = amountA * totalLiquidity / reserveA
    liqB = amountB * totalLiquidity / reserveB

    return min(liqA, liqB)

def addPoolLiquidityOptimiser():
    # TODO: build opitimiser
    # How to get max liquidity(tokens) from amountA, amountB input
    #########################
    # liquidity -= MINIMUM_LIQUIDITY;
    #     // MINIMUM_LIQUIDITY is a hack for non-zero division
    #     totalLiquidity = MINIMUM_LIQUIDITY;
    ####################################
    # if ((std::max(liqA, liqB) - liquidity) * 100 / liquidity >= 3) {
    #             return Res::Err("Exceeds max ratio slippage protection of 3%%");
    #         }
    pass

def removePoolLiquidity(liquidity,reserveA,reserveB,totalLiquidity):
    # No Checks included! Only useable for valid block transactions!
    # https://github.com/DeFiCh/ain/blob/a7d914f15f762d121ac2c5d07d38d30cf7e09d4d/src/masternodes/poolpairs.cpp
    amountA = liquidity * reserveA / totalLiquidity
    amountB = liquidity * reserveB / totalLiquidity

    return amountA,amountB

def poolSwap(block,tokenFrom,poolSymbol,fromAmount,reserveA,reserveB,commission=0,dexfeeInPct=0):
    # No Checks included! Only useable for valid block transactions!
    # https://github.com/DeFiCh/ain/blob/a7d914f15f762d121ac2c5d07d38d30cf7e09d4d/src/masternodes/poolpairs.cpp


    # bool const forward = in.nTokenId == idTokenA;
    # auto& reserveF = forward ? reserveA : reserveB;
    # auto& reserveT = forward ? reserveB : reserveA;
    if tokenFrom == poolSymbol.split('-')[0]:
        bForward = True
    else:
        bForward = False

    if bForward:
        reserveF = reserveA
        reserveT = reserveB
    else:
        reserveT = reserveA
        reserveF = reserveB

    # claim trading fee
    tradeFee = fromAmount * commission
    fromAmount = fromAmount - tradeFee

    # claim dex fee
    dexfeeInAmount = fromAmount * dexfeeInPct
    fromAmount = fromAmount - dexfeeInAmount

    unswapped = fromAmount
    swapped = 0
    poolFrom = reserveF
    poolTo = reserveT
    if poolFrom/SLOPE_SWAP_RATE < unswapped:
        chunk = poolFrom/SLOPE_SWAP_RATE
    else:
        chunk = unswapped
    if block < BAY_FRONT_GARDENS_HEIGHT:
        while unswapped > 0:
            stepFrom = min(chunk,unswapped)
            stepTo = poolTo * stepFrom / poolFrom
            poolFrom = poolFrom + stepFrom
            poolTo = poolTo - stepTo
            unswapped = unswapped - stepFrom
            swapped = swapped + stepTo
    else:
        swapped = poolTo - (poolTo * poolFrom / (poolFrom + unswapped))
        if block >= FORT_CANNING_HILL_HEIGHT and swapped != 0:
            swapped = math.floor(swapped)

        poolFrom = poolFrom + unswapped
        poolTo = poolTo - swapped
    
    return poolFrom,poolTo,swapped