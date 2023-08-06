



import os
import time
import traceback
import sys
import abc

from .EnumLogLevel import *
from .AbstractLogger import *





#
# This logger will broadcast log messages to additional loggers.
#
class NamedMulticastLogger(AbstractLogger):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, loggerMap = None, idCounter = None, indentationLevel = 0, parentLogEntryID = 0):
		super().__init__(idCounter)
		self._indentationLevel = indentationLevel
		self._parentLogEntryID = parentLogEntryID

		if loggerMap is not None:
			assert isinstance(loggerMap, dict)
			for k, v in loggerMap.items():
				assert isinstance(k, str)
				assert isinstance(v, AbstractLogger)
			self.__loggerMap = loggerMap
		else:
			self.__loggerMap = {}
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	@property
	def loggers(self) -> dict:
		return dict(self.__loggerMap)
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption):
		for logger in self.__loggerMap.values():
			logger._logi(logEntryStruct, True)
	#

	def _descend(self, logEntryStruct):
		nextID = logEntryStruct[1]
		newMap = {}
		for loggerName in self.__loggerMap.keys():
			logger = self.__loggerMap[loggerName]
			newMap[loggerName] = logger._descend(logEntryStruct)
		return NamedMulticastLogger(newMap, self._idCounter, self._indentationLevel + 1, nextID)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def getLogger(self, loggerName) -> AbstractLogger:
		return self.__loggerMap.get(loggerName)
	#

	def addLogger(self, loggerName:str, logger):
		assert isinstance(loggerName, str)
		assert isinstance(logger, AbstractLogger)
		if self.__loggerMap.get(loggerName, None) is not None:
			del self.__loggerMap[loggerName]
		self.__loggerMap[loggerName] = logger
	#

	def removeLogger(self, loggerName:str):
		assert isinstance(loggerName, str)
		if self.__loggerMap.get(loggerName, None) is not None:
			del self.__loggerMap[loggerName]
	#

	def removeAllLoggers(self):
		self.__loggerMap = {}
	#

	def clear(self):
		for logger in self.__loggerMap.values():
			logger.clear()
	#

	def close(self):
		for logger in self.__loggerMap.values():
			logger.close()
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	@staticmethod
	def create(**kwargs):
		return NamedMulticastLogger(loggerMap = kwargs)
	#

#




