from datetime import datetime

import cc.services.node
from cc.database import mongo, database

__author__ = "Mickey.Mouse"

class LogService:
    def __init__(self):
        pass

    @staticmethod
    def get_log_by_monkey_id(monkey_id):
        log = mongo.db.log.find_one({'monkey_id': monkey_id})
        if log: 
            log_file = database.gridfs.get(log['file_id'])
            monkey_label = cc.services.node.NodeService.get_monkey_label(
                cc.services.node.NodeService.get_monkey_by_id(log['monkey_id']))

            return \
                {
                    'monkey_label': monkey_label,
                    'log': log_file.read(),
                    'timestamp': log['timestamp']
                } 

    @staticmethod
    def remove_logs_by_monkey_id(monkey_id):
        log = mongo.db.log.find_one({'monkey_id': monkey_id})
        if log is not None:
            database.gridfs.delete(log['file_id'])
            mongo.db.log.delete_one({'monkey_id': monkey_id})

    @staticmethod
    def add_log(monkey_id, log_data, timestamp=datetime.now()):
        LogService.remove_logs_by_monkey_id(monkey_id)
        file_id = database.gridfs.put(log_data)

        return mongo.db.log.insert(
            {
                'monkey_id': monkey_id,
                'file_id': file_id,
                'timestamp': timestamp
            }
        ) 

    @staticmethod
    def log_exists(monkey_id):
        return mongo.db.log.find_one({'monkey_id': monkey_id}) is not None