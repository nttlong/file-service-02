import datetime
import uuid

import cy_docs
from cy_xdoc.services.base import Base
from cy_xdoc.models.apps import App


class AppServices(Base):


    def get_list(self, app_name: str):
        docs = self.expr(App)
        ret = self.db(app_name).doc(App).aggregate().project(
            cy_docs.fields.AppId >> docs._id ,
            docs.name,
            docs.description,
            docs.domain,
            docs.login_url,
            docs.return_url_afterSignIn

        ).sort(
            docs.Name.asc(),
            docs.RegisteredOn.desc()
        )
        return ret

    def get_item(self, app_name, app_get):
        docs = self.expr(App)
        return self.db(app_name).doc(App).aggregate().project(
            cy_docs.fields.AppId >> docs.Id ,
            docs.name,
            docs.description,
            docs.domain,
            docs.login_url,
            docs.return_url_afterSignIn

        ).match(docs.Name == app_get).first_item()

    def create(self,
               Name: str,
               Description: str,
               Domain: str,
               LoginUrl: str,
               ReturnUrlAfterSignIn: str,
               UserName: str,
               Password: str):
        doc = self.expr(App)
        app_id = str(uuid.uuid4())
        secret_key = str(uuid.uuid4())
        self.db('admin').doc(App).insert_one(
            doc.Id << app_id,
            doc.Name << Name,
            doc.ReturnUrlAfterSignIn << ReturnUrlAfterSignIn,
            doc.Domain << Domain,
            doc.LoginUrl << LoginUrl,
            doc.Description << Description,
            doc.Username << UserName,
            doc.Password << Password,
            doc.SecretKey << secret_key,
            doc.RegisteredOn << datetime.datetime.utcnow()

        )
        ret = cy_docs.DocumentObject(
            AppId=app_id,
            Name=Name,
            ReturnUrlAfterSignIn=ReturnUrlAfterSignIn,
            Domain=Domain,
            LoginUrl=LoginUrl,
            Description=Description,
            Username = UserName,
            SecretKey = secret_key,
            RegisteredOn= datetime.datetime.utcnow()
        )
        return ret
