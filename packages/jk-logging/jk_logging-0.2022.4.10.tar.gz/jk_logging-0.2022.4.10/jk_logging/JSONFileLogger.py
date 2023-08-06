



import os
import json

from .EnumLogLevel import *
from .AbstractLogger import *
from .BufferLogger import BufferLogger





#
# This logger will buffer log messages in an internal array. Later this data can be forwarded to
# other loggers, f.e. in order to store them on disk.
#
class JSONFileLogger(BufferLogger):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructors
	################################################################################################################################

	def __init__(self, idCounter = None, parentID = None, indentLevel = 0, logItemList = None, rootParent = None, filePath = None):
		super().__init__(idCounter, parentID, indentLevel, logItemList)

		if rootParent is not None:
			assert isinstance(rootParent, JSONFileLogger)
		assert isinstance(filePath, str)

		self.__filePath = filePath
		self.__filePathTmp = filePath + ".tmp"

		self.__rootParent = rootParent
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption):
		super()._logi(logEntryStruct, bNeedsIndentationLevelAdaption)

		if self.__rootParent is None:
			self._saveLogData()
		else:
			self.__rootParent._saveLogData()
	#

	def _saveLogData(self):
		with open(self.__filePathTmp, "w") as f:
			#json.dump(self.getDataAsJSON(), f)
			json.dump(self.toJSON(), f)
		
		if os.path.isfile(self.__filePath):
			os.unlink(self.__filePath)
		os.rename(self.__filePathTmp, self.__filePath)
	#

	def _descend(self, logEntryStruct):
		nextID = logEntryStruct[1]
		newList = logEntryStruct[7]
		return JSONFileLogger(
			self._idCounter,
			nextID,
			self._indentationLevel + 1,
			newList,
			self.__rootParent if self.__rootParent else self,
			self.__filePath,
		)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __str__(self):
		return "<JSONFileLogger(" + hex(id(self)) + ", indent=" + str(self._indentationLevel) + ",parentID=" + str(self._parentLogEntryID) + ")>"
	#

	def __repr__(self):
		return "<JSONFileLogger(" + hex(id(self)) + ", indent=" + str(self._indentationLevel) + ",parentID=" + str(self._parentLogEntryID) + ")>"
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	@staticmethod
	def __convertRawLogData(items):
		ret = []
		for item in items:
			item = list(item)
			item[5] = EnumLogLevel.parse(item[5])
			if item[0] == "txt":
				pass
			elif item[0] == "ex":
				pass
			elif item[0] == "desc":
				item[7] = JSONFileLogger.__convertRawLogData(item[7])
			else:
				raise Exception("Implementation Error!")
			ret.append(item)
		return ret
	#

	@staticmethod
	def create(filePath:str):
		assert isinstance(filePath, str)

		if os.path.isfile(filePath):
			with open(filePath, "r") as f:
				jsonRawData = json.load(f)
			jsonRawData = JSONFileLogger.__convertRawLogData(jsonRawData)
		else:
			jsonRawData = None

		return JSONFileLogger(None, None, 0, jsonRawData, None, filePath)
	#

#






