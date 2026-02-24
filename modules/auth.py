import jwt,datetime
from config import SECRET

def create_token(user,role):
    return jwt.encode({
        "user":user,
        "role":role,
        "exp":datetime.datetime.utcnow()+datetime.timedelta(hours=2)
    },SECRET)

def verify(token):
    return jwt.decode(token,SECRET,algorithms=["HS256"])