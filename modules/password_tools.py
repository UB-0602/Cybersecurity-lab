import math,string

def strength(p):
    score=0
    if any(c.islower() for c in p):score+=1
    if any(c.isupper() for c in p):score+=1
    if any(c.isdigit() for c in p):score+=1
    if any(c in string.punctuation for c in p):score+=1
    if len(p)>7:score+=1
    return score

def crack_time(p):
    charset=94
    combos=charset**len(p)
    return round(combos/1e6,2)