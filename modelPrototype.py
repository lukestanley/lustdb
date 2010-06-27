# __dict__ is used to get varible acceptable names and types from class instance
# class init takes model parameters and compares with original
class Model(dict):
	verifiedFakeSQL = ''
	modelData = {}
	def __init__(self, *unused, **keys):
		justTheClass = self.__class__
		verifiedFakeSQL = []
		for key in keys:
			keyName = key
			keyValue = keys[key]
			fakeSQL = keyName, keyValue, type(keyValue)
			#print fakeSQL
			assert keyName in justTheClass.__dict__ #verify we don't have any extra arguments
			#print keyName,'value item type',type(keyValue),'justTheClass type',type(justTheClass.__dict__[keyName]) #verify the type is the same
			assert type(keyValue) == type(justTheClass.__dict__[keyName]) #verify the type is the same
		keysToIgnore = ['__module__','__doc__']
		for baseModelkey in justTheClass.__dict__:
			if (baseModelkey not in keysToIgnore) and (baseModelkey[0] != '_'):
				basekeyName = baseModelkey
				basekeyValue = justTheClass.__dict__[baseModelkey]
				keyName = baseModelkey
				
				if basekeyName not in keys: #use default model value if not set
					fakeSQL = baseModelkey, basekeyValue, type(basekeyValue)
					self.modelData[baseModelkey]=basekeyValue
				else: #model value given, using that
					keyValue = keys[baseModelkey]
					fakeSQL = keyName, keyValue, type(keyValue)
					self.modelData[keyName]=keyValue
				verifiedFakeSQL.append(fakeSQL)
		#enable attribute access
		for modelKey in self.modelData:
			setattr(self, modelKey, self.modelData[modelKey])
			dict.__setitem__(self, modelKey, self.modelData[modelKey])
		
		dict.__setitem__(self, '__model__',justTheClass.__name__)
		self.__setattr__ = self.__setitem__
		self.__getattr__ = self.__getitem__

		self.verifiedFakeSQL = verifiedFakeSQL
	def __str__(self):
		return str(self.verifiedFakeSQL)
	def SQL(self):
		SQLInsert = 'INSERT INTO ????????' + self.__class__.__name__ + '???????? '
		keyListString = ",".join(self.modelData.keys())
		valuesList = []
		for modelOb in self.modelData:
			modelObValue = self.modelData[modelOb]
			ourType = type(modelObValue)
			if ourType in (bool,long,int): valuesList.append(str(modelObValue))
			if ourType is str: valuesList.append("'" + str(modelObValue) + "'")
				
		valueListString = ",".join(valuesList)
		SQLInsert = SQLInsert + '(' + keyListString +') VALUES (' + valueListString + ');'
		return SQLInsert 
	"""def __getattr__(self, attr):
		return self[attr]"""
