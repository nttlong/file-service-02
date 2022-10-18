import api_models.documents
import enig
import enig_frames.db_context
import enig_frames.repositories.accounts
import enig_frames.services.sercurities
import enig_frames.config
import enig_frames.db_context

class Accounts(enig.Singleton):
    def __init__(self,
                 repo=enig.depen(enig_frames.repositories.accounts.Accounts),
                 sercurity=enig.depen(enig_frames.services.sercurities.Sercurities),
                 configuration=enig.depen(enig_frames.config.Configuration),
                 db_context = enig.depen(enig_frames.db_context.DbContext)
                 ):
        self.repo: enig_frames.repositories.accounts.Accounts = repo
        self.sercurity: enig_frames.services.sercurities.Sercurities = sercurity
        self.configuration: enig_frames.config.Configuration =configuration
        self.db_context =db_context
        self.check_root_user()
    async def authenticate_user_async(self, app_name: str, username: str, password: str):
        db_name = self.db_context.get_db_name(app_name)


        check = self.verify(
            app_name=app_name,
            username=username,
            password=password
        )
        if not check:
            return False
        user = await  self.get_user_by_username_async(
            app_name=app_name,
            username=username
        )
        return user
    def verify(self, app_name, username, password):
        """
        Kiểm tra user
        :param app_name:
        :param username:
        :param password:
        :return:
        """
        """
        Kiểm tra xem đã có user mặc định chưa?
        """


        user = self.repo.get_user_by_username(
            app_name=app_name,
            username=username
        )
        if user is None:
            return False
        if not self.sercurity.verify_password(
                plain_password=username.lower() + "/" + password,
                hashed_password=user[api_models.documents.Users.HashPassword]
        ):
            return False
        else:
            return True

    def check_root_user(self):
        app_name = "admin"
        username = "root"
        password = "root"
        admin_roor_user = self.repo.get_user_by_username('admin', 'root')
        if admin_roor_user is None:
            hash_password = self.sercurity.get_password_hash(username.lower() + "/" + password)
            admin_roor_user = self.repo.create(
                app_name=app_name,
                username=username,
                hash_password=hash_password,
                email="",
                is_sys_admin=True

            )
            return admin_roor_user

    def get_sso_login(self, SSOID):
        sso_info = self.repo.get_sso_info(SSOID)
        return sso_info

    async def get_sso_login_asycn(self, SSOID):
        sso_info = await self.repo.get_sso_info_async(SSOID)
        return sso_info

    async def get_user_by_username_async(self, app_name, username):
        return await self.repo.get_user_by_username_async(
            app_name=app_name,
            username=username
        )


