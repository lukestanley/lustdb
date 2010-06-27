from modelPrototype import Model

class Task(Model): 
    title = ''
    done = False

from lustdb import * 

print 'Done tasks:'
for task in db.taskList:
	if task.done: 
		print task.title
