import ReCompact.dbm
import datetime
import bson
import ReCompact
@ReCompact.document(
    name="SYS_SingleSignOn",
    keys=[ "SSOID"],
    indexes=["Token","Applications","Applications,Token","Applications,SSOID","ReturnUrlAfterSignIn"]

)
class SSO:
    _id = (bson.ObjectId)
    Token = (str)
    SSOID = (str)
    CreatedOn = (datetime.datetime)
    Application = (str)
    ReturnUrlAfterSignIn =(str)