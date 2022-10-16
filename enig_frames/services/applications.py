import enig_frames.repositories.applications
import enig
class Applications(enig.Singleton):
    def __init__(self, repo=enig.depen(enig_frames.repositories.applications.Applications)):
        self.repo:enig_frames.repositories.application.Applications=repo
    def create(self, name:str, login_url:str, domain:str,description:str):
        return self.repo.create(
            name=name,
            domain=domain,
            login_url=login_url,
            description=description)
