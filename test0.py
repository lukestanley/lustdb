from modelPrototype import Model

class Task(Model): 
    title = ''
    done = False

from lustdb import * 

db.taskList = []

db.taskList.append(Task(title='push to git', done=True))

