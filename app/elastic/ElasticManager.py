import json
import random

from elasticsearch import Elasticsearch, helpers, RequestError
from .ElasticStream import ElasticStream


from conf import cfg

class ElasticManager:
    def __init__(self, elastic_host=cfg['elastic']['host'], elastic_index=cfg['elastic']['ingestion_index']) -> None:
        
        self.es = Elasticsearch(elastic_host,timeout=60)
        self.elastic_index = elastic_index
        
        try:
            self.es.indices.create(index=self.elastic_index)
            
        except RequestError as e:
            if e.args[0] != 400: # 400 is 'already exists'
                raise e
    
    def get_index(self):
        return self.elastic_index
    
    def scan(self, query):
        scan = helpers.scan(self.es,query=query,index=self.elastic_index, preserve_order=True)
        return scan
    
    def add(self, body, id):
        self.es.index(index=self.elastic_index,body=body, id=id)
        
    def update(self, body, id):
        doc = {"doc": body}
        try:
            self.es.update(index=self.elastic_index,body=doc, id=id)
        except:
            self.add(body=body, id=id)
        
    def search(self, query):
        result = self.es.search(index=self.elastic_index,body=query)
        return result
    
    @staticmethod
    def build_jsonl(batch_size=1_000_000):
        
        query_seed = random.getrandbits(64)
        
        query = {
                    "function_score": {
                        "query": {
                            "bool": {
                                "must_not": {
                                    "exists": {
                                        "field": "answer"
                                    }
                                }
                            }
                        },
                        "functions": [{
                            "random_score": {
                                "seed": f"{query_seed}",
                                "field": "_seq_no"
                            }
                        }],
                        "boost_mode": "replace"
                    }
                }
        
        es = ElasticStream(query)

        jsonl = ""

        for index, result in enumerate(es):
            if index == batch_size:
                break
            jsonl += json.dumps(result) + "\n"
            
        jsonl = jsonl.encode("ascii","ignore")
        jsonl = jsonl.decode()
            
        return jsonl.strip()