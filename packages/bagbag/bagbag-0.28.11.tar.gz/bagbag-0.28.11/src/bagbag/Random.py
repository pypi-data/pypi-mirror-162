import random 
from typing import Any

def Int(min:int, max:int) -> int:
    return random.randint(min, max)

def Choice(obj:list|str) -> Any:
    return random.choice(obj)

def String(length:int, charset:str="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") -> str:
    res = []
    while len(res) < length:
        res.append(random.choice(charset))
    
    return "".join(res)

if __name__ == "__main__":
    print(Choice("doijwoefwe"))
    print(String(5))
