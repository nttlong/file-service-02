import enig_frames.repositories.applications
import enig
import enig_frames.config

class Applications(enig.Singleton):
    def __init__(self,
                 repo=enig.depen(enig_frames.repositories.applications.Applications),
                 configuration=enig.depen(enig_frames.config.Configuration)
                 ):
        self.repo: enig_frames.repositories.application.Applications = repo
        self.configuration=configuration
        self.check_admin_app()

    def create(self, name: str, login_url: str, domain: str, description: str):
        return self.repo.create(
            name=name,
            domain=domain,
            login_url=login_url,
            description=description)

    async def create_async(self, name: str, login_url: str, domain: str, description: str):
        return await self.repo.create_async(
            name=name,
            domain=domain,
            login_url=login_url,
            description=description)

    def get_list(self, app_name: str, page_index: int, page_size: int, value_search: str):
        if app_name != 'admin':
            return None
        ret_list = self.repo.get_list(app_name, page_index, page_size, value_search)
        return ret_list

    async def get_list_async(self, app_name: str, page_index: int, page_size: int, value_search: str):
        if app_name != 'admin':
            return None
        ret_list = await self.repo.get_list_async(app_name, page_index, page_size, value_search)
        return ret_list

    def check_admin_app(self):
        admin_app = self.repo.get_app_by_name('admin')
        if admin_app is None:
            self.repo.create(
                name='admin',
                login_url=None,
                domain=None,
                description='Administrator app',


            )

    def get_app_by_name(self,name:str):
        return self.repo.get_app_by_name(app_name=name)