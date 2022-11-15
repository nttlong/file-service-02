import datetime
import bson
import ReCompact
import cy_docs
@cy_docs.define(
    name="SYS_SingleSignOn",
    indexes=["Token","Applications","Applications,Token","Applications,SSOID","ReturnUrlAfterSignIn"],
    uniques=[ "SSOID"]
)

class SSO:
    _id:bson.ObjectId
    Token:str
    SSOID:str
    CreatedOn:datetime.datetime
    Application:str
    ReturnUrlAfterSignIn:str