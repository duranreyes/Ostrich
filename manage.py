from flask.ext.script import Manager
from app import webapp

manager = Manager(webapp)

@manager.command
def hello():
    from app.scripts.pickup_schedule import pickupSchedule
    pickupSchedule()

@manager.command
def indexer():
    from app.scripts import Indexer
    Indexer().getAllDataFromDB(query_condition=' and i.item_id>958')

if __name__ == "__main__":
    manager.run()
