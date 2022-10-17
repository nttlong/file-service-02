import enig_frames.repositories.applications
import enig


class Applications(enig.Singleton):
    def __init__(self, repo=enig.depen(enig_frames.repositories.applications.Applications)):
        self.repo: enig_frames.repositories.application.Applications = repo

    def create(self, name: str, login_url: str, domain: str, description: str):
        return self.repo.create(
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
