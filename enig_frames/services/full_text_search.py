import enig
import enig_frames.repositories.full_text_search
class FullTextSearch(enig.Singleton):
    def __init__(self,
                 repo:enig_frames.repositories.full_text_search.FullTextSearch=enig.depen(
                     enig_frames.repositories.full_text_search.FullTextSearch
                 )):
        self.repo:enig_frames.repositories.full_text_search.FullTextSearch=repo
    def search(self,index:str,search_definition):


        return self.repo.search(
            index=index,
            definition=search_definition
        )