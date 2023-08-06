from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Vault:
    value:str

@dataclass
class Address:
    value:str

# @dataclass
# class Addresses:
#     value:list[str]

@dataclass
class AddressesWithAmount:
    '''
    List of Adress Amount Tuples. Tuple has str (address), float (number of dTokens) and int (ID of dToken)
    '''
    value:list[tuple[str,float,int]]
    
    def toDict(self):
        d = {}
        for v in self.value:
            if v[0] not in d:
                d[v[0]] = {}

            if v[2] not in d[v[0]]:
                d[v[0]][v[2]] = v[1]
            else:
                d[v[0]][v[2]] = d[v[0]][v[2]] + v[1]
        return d

@dataclass
class Amounts:
    '''
    List of Amount Tuples. Amount Tuple has float (number of dTokens) and int (ID of dToken)
    '''
    value:list[tuple[float, int]]