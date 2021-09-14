import json
from flask_restful import Resource
from pymitter import EventEmitter


class eventReceiver(Resource):
    def __init__(self) -> None:
        pass

    @classmethod
    def withEmitter(cls, eventEmitter: EventEmitter):
        cls.app_state = {}
        cls.ee = eventEmitter
        cls.state_watchers(cls)
        return cls

    def get(self, event_id):
        try:
            res = json.dumps(self.app_state[event_id])
        except:
            res = json.dumps({"status": "error"})
        return res

    def post(self, event_id):
        self.ee.emit(event_id)
        return "OK " + event_id

    def state_watchers(self):
        def prodigy_start():
            self.app_state["prodigy"] = {"status": "running"}

        self.ee.on("prodigy.start", prodigy_start)

        def prodigy_stop():
            self.app_state["prodigy"] = {"status": "stopped"}

        self.ee.on("prodigy.stop", prodigy_stop)

        def dw_start():
            self.app_state["directory_watcher"] = {"status": "running"}

        self.ee.on("directory_watcher.start", dw_start)

        def dw_stop():
            self.app_state["directory_watcher"] = {"status": "stopped"}

        self.ee.on("directory_watcher.start", dw_stop)
