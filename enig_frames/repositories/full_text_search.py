import enig
import enig_frames.config
from elasticsearch import Elasticsearch
class FullTextSearch(enig.Singleton):
    def __init__(self,
                 configuration:enig_frames.config.Configuration= enig.depen(enig_frames.config.Configuration)):
        self.configuration:enig_frames.config.Configuration=configuration
        self.client=Elasticsearch(hosts=self.configuration.config.elastic_search.server)

    def search(self, index, definition):
        args = dict(
            index=index
        )
        ret= self.client.search(
            **{**args, **definition}
        )
        return ret

    def delete_by_id(self, index, id):
        self.client.delete(index= index, id= id)
