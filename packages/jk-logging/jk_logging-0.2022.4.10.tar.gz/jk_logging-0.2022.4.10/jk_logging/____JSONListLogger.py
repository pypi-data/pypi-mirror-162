



import os
import json

from .EnumLogLevel import *
from .AbstractLogger import *
from .BufferLogger import BufferLogger





"""
NOTE: This class is somehow the same as BufferLogger/BufferLogger2

#
# This logger will buffer log messages in an internal array. Later this data can be forwarded to
# other loggers, f.e. in order to store them on disk.
#
class JSONListLogger(BufferLogger):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructors
	################################################################################################################################

	def __init__(self, idCounter = None, parentID = None, indentLevel = 0, logItemList = None, rootParent = None):
		super().__init__(idCounter, parentID, indentLevel, logItemList)

		if rootParent is not None:
			assert isinstance(rootParent, JSONListLogger)

		self.__rootParent = rootParent
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _descend(self, logEntryStruct):
		nextID = logEntryStruct[1]
		newList = logEntryStruct[7]
		return JSONListLogger(
			self._idCounter,
			nextID,
			self._indentationLevel + 1,
			newList,
			self.__rootParent if self.__rootParent else self,
		)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __str__(self):
		return "<JSONListLogger(" + hex(id(self)) + ", indent=" + str(self._indentationLevel) + ",parentID=" + str(self._parentLogEntryID) + ")>"
	#

	def __repr__(self):
		return "<JSONListLogger(" + hex(id(self)) + ", indent=" + str(self._indentationLevel) + ",parentID=" + str(self._parentLogEntryID) + ")>"
	#

	def toJSON(self) -> list:
		return self.getDataAsJSON()
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
				item[7] = JSONListLogger.__convertRawLogData(item[7])
			else:
				raise Exception("Implementation Error!")
			ret.append(item)
		return ret
	#

	@staticmethod
	def create():
		return JSONListLogger(None, None, 0, None, None)
	#

#
"""





