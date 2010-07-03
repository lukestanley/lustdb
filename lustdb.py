#Copyright Luke Stanley 2010
#License: LGPL

try:
	from simplejson import dumps, loads
except ImportError:
	from json import dumps, loads
from sys import modules

filename=''

def getMainGlobals():
	m = modules['__main__']
	md = dir(m)
	fakeGlobals = {}
	for ob in md:
		#print ob
		thisOb = getattr(m,ob)
		fakeGlobals[ob]=thisOb
	return fakeGlobals
def findModelInstances(parentglobalRef):
	modelInstances = {}
	for globalObject in parentglobalRef: 
		#print dir(globalObject)
		if 'modelData' in dir(parentglobalRef[globalObject]):
			#print globalObject
			if globalObject != 'Model':
				modelInstances[globalObject] = parentglobalRef[globalObject]
	
	return modelInstances


def enableSmartDatabaseModels(parentglobalRef):
	global db
	#assert db != {}
	ModelInstances = findModelInstances(parentglobalRef)
	#print 'ModelInstances',ModelInstances
	#print 'test accesing ModelInstances by creating Task instance'
	#taskTest = ModelInstances['Task'](title='fish')
	#print taskTest
	
	replaceDumbModelInstances(db, modelInstances = ModelInstances)



def replaceDumbModelInstances(child, parent=None, childKeyOrItem=None, modelInstances=None):
	if isinstance(child, dict):
		#print 'found dict', child
		if '__model__' in child:
			#print 'found __model__ in dict'
			originalDictCopy = {}
			childModelName = child['__model__']
			
			for originalKey in child:
				if originalKey != '__model__':
					if type(child[originalKey]) == unicode:
						 child[originalKey] = str(child[originalKey])
					originalDictCopy[str(originalKey)] = child[originalKey]
			#print 'originalDictCopy',originalDictCopy
			child = modelInstances[childModelName](**originalDictCopy)
			parent[childKeyOrItem] = child
			#print 'updated to use task model'	
		else:
			#print 'no __model__ child', child
			for k in child:
				value = child[k]
				replaceDumbModelInstances(value, child, childKeyOrItem=k, modelInstances=modelInstances)
	if isinstance(child, (list, tuple)):
		for value in xrange(len(child)):
			replaceDumbModelInstances(child[value], child, childKeyOrItem=value, modelInstances=modelInstances)




def saveDB():
	global db
	global filename
	#print db
	f = open(filename,'w')
	
	content = dumps(db, indent=4)
	f.write(content)
	f.close()
	#print 'saveDB called, saved as'
	#print content
	assert "__methods__" not in loads(content)

_loading = True

class dotlistify(list):
	def append(self, value):
		super(dotlistify, self).append(value)
		saveDB()
		#print 'append!'
	
		
class dotdictify(dict):
	marker = object()
	def sync(self):
		saveDB()
	def __init__(self, value=None):
		if value is None:
			pass
		elif isinstance(value, dict):
			for key in value:
				self.__setitem__(key, value[key])
				#del self.__methods__
				#del self.__members__
		else:
			raise TypeError, 'expected dict'

	def __setitem__(self, key, value):
		if isinstance(value, dict) and not isinstance(value, dotdictify):
			value = dotdictify(value)		
		if 'modelData' in dir(value):
			value = value.modelData
		if isinstance(value,list):
			value = dotlistify(value)
		dict.__setitem__(self, key, value)
		global _loading
		if _loading == False:
			#print '__setitem__', key, value
			saveDB()
			
	def __getitem__(self, key):
		found = self.get(key, dotdictify.marker)
		if found is dotdictify.marker:
			if key not in ['__methods__','__members__']:
				found = dotdictify()
				dict.__setitem__(self, key, found)
				
				print 'setitem called in getitem for',key
		#print '__getitem__', key, found
		return found
	def __repr__(self):
		keys = self.keys()
		keys.sort()
		args = ', '.join(['%s=%r' % (key, self[key]) for key in keys])
		return '%s(%s)' % (self.__class__.__name__, args)
		
	__setattr__ = __setitem__
	__getattr__ = __getitem__




def loadDB(filenameVar='test1.json'):
	global db
	global filename
	global _loading
	filename = filenameVar
	#content = db
	_loading = True
	try:
		f = open(filename,'r')
		content = loads(f.read())
		f.close()
	except:
		content = {}
	#print content
	db = content
	#print 'loadDB called'
	enableSmartDatabaseModels(getMainGlobals())
	
	
	db = dotdictify(db)
	_loading = False
	return db
notdb = {'bigBang' :
		  {'stars':
			   {'planets': {}
				}
		   }
}
db = {}
loadDB()
globals()['db'] = db

