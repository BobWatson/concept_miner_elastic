import json
from flask_restful import Resource
from pymitter import EventEmitter

class eventReceiver(Resource):
    def __init__(self) -> None:
        pass
        
    @classmethod
    def withEmitter(cls, eventEmitter: EventEmitter):
        cls.ee = eventEmitter
        return cls
    
    def get(self, event_id):
        event = {"none": event_id}
        event_str = json.dumps(event)
        return event_str
    
    def post(self,event_id):
        self.ee.emit(event_id)
        return "OK "+event_id