from cy_xdoc.repos.base import Base
import cy_docs

class Accounts(Base):
    def __init__(self):
        Base.__init__(self)

    def validate(self, app_name, username, password):
        cy_docs.get_doc(
            
        )
