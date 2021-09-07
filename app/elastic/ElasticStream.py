import json
from . import ElasticManager

from conf import cfg

class ElasticStream:
    def __init__(self, elastic_query={"match_all": {}}, additional=None, elastic_host=cfg['elastic']['host'], elastic_index=cfg['elastic']['ingestion_index']) -> None:
        
        self.es = ElasticManager.ElasticManager(elastic_host, elastic_index)
        
        self.query = {"query": elastic_query}
        self.results = None

        if additional is None:
            self.additional = []
        else:
            self.additional = additional
            
    def __iter__(self):
        self.n = 0
        if self.results is None:
            self.set_query(self.query)
        return self
    
    def __next__(self):
        self.current_result = next(self.results)
        line = {}
        line["text"] = self.current_result["_source"]["text"]
        line["meta"] = {"source": self.current_result["_source"]["meta"]["source"], "id": self.current_result["_id"]}
        line.update(self.additional)
        return line
    
    def set_query(self, query):
        self.query = query
        self.results = self.es.scan(query=self.query)
        return