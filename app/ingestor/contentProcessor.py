import spacy
from datetime import datetime
from hashlib import sha1
from elastic.ElasticManager import ElasticManager
import logging
import re
from conf import cfg

class contentProcessor:
    def __init__(self) -> None:
        self.nlp = spacy.load("en_core_web_trf")
        self.em = ElasticManager()
        self.em_ents = ElasticManager(elastic_index=cfg['elastic']['ents_index'])
        self.expr = re.compile(r'[a-z]\b\s[a-z]',flags=re.IGNORECASE)
    
    def process(self, body: str, file, timestamp):

        file_id = sha1(str(body).encode("utf-8")).hexdigest()
        
        logging.info(f"Reading {file} as id: {file_id}")
        
        if self.alreadyIngested(file_id) is True:
            logging.info(f"Skipping {file} (id: {file_id}) that already exists in the database")
            return
        
        created_time = datetime.fromtimestamp(timestamp)
        
        content = body.replace('\r\n',' ')
        content = content.replace('\n',' ')
        content = content.encode("ascii", "ignore")
        content = content.decode()
        
        doc = self.nlp(content)
        docs = [sent for sent in doc.sents]
        
        line_list = []
                
        for doc in docs:
            sent = doc.text
            body = str(sent)
            line = {}
            line["body"] = {}
            line["body"]["text"] = body
            line["body"]["meta"] = {}
            line["body"]["meta"]["source"] = str(file)
            line["body"]["meta"]["source_hash"] = str(file_id)
            line["body"]["meta"]["timestamp"] = str(created_time)
            line["body"]["meta"]["id"] = str(sha1((str(file)+str(sent)).encode("utf-8")).hexdigest())
            line["body"]["meta"]["ents"] = {}
            line["id"] = line["body"]["meta"]["id"]
            
            for ent in doc.ents:
                label_int = ent.label
                label = ent.label_
                text = ent.text
                
                try:
                    if isinstance(line["body"]["meta"]["ents"][label], list) and isinstance(line["body"]["meta"]["ents"][label_int], list):
                        line["body"]["meta"]["ents"][label].append(text)
                        line["body"]["meta"]["ents"][label_int].append(text)
                    else:
                        line["body"]["meta"]["ents"][label] = [text]
                        line["body"]["meta"]["ents"][label_int] = [text]
                        
                except:
                    line["body"]["meta"]["ents"][label] = [text]
                    line["body"]["meta"]["ents"][label_int] = [text]
            
            if self.expr.search(body) and len(body) > 20:
                line_list.append(line)
            else:
                logging.info(f"Skipping: {body}")
        
        logging.info(f"File {str(file)} read with id: {file_id}")
        
        for line in line_list:
            self.em.add(line["body"], line["id"])
            
    def alreadyIngested(self,source_hash) -> bool:
        query = {"size":1, "query" : { "bool": { "must": [
                    {"match": {
                        "meta.source_hash": f"{source_hash}"
                    }}]
                }}}
        result = self.em.search(query)
        hits = result["hits"]["total"]["value"]
        
        return hits > 0