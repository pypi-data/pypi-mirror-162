


import typing

from .EnumLogLevel import *
from .AbstractLogger import *







class IntContainer(object):

	def __init__(self, initialValue = 0):
		self.value = initialValue
	#

#






#
# This logger keeps track of how many log messages of what type have been issued.
#
# NOTE: Be aware that nested detection loggers will share the same (!!) objects that count log messages.
#
class DetectionLogger_v0(AbstractLogger):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, logger, logLevelCounterMap:dict = None, maxLogLevelSeen:IntContainer = None):
		super().__init__(None)

		self.__logger = logger
		if logLevelCounterMap is None:
			self.__logLevelCounterMap = {}
		else:
			assert isinstance(logLevelCounterMap, dict)
			self.__logLevelCounterMap = logLevelCounterMap

		if maxLogLevelSeen is None:
			self.__maxLogLevelSeen = IntContainer()
		else:
			assert isinstance(maxLogLevelSeen, IntContainer)
			self.__maxLogLevelSeen = maxLogLevelSeen
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _descend(self, logEntryStruct):
		descendedLogger = self.__logger._descend(logEntryStruct)
		return DetectionLogger_v0(descendedLogger, self.__logLevelCounterMap, self.__maxLogLevelSeen)
	#

	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption:bool):
		nLogLevel = int(logEntryStruct[5])
		self.__logLevelCounterMap[nLogLevel] = self.__logLevelCounterMap.get(nLogLevel, 0) + 1
		if nLogLevel > self.__maxLogLevelSeen.value:
			self.__maxLogLevelSeen.value = nLogLevel
		self.__logger._logi(logEntryStruct, bNeedsIndentationLevelAdaption)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# Returns the number of log messages issued.
	#
	def getLogMsgCount(self, logLevel):
		return self.__logLevelCounterMap.get(int(logLevel), 0)
	#

	#
	# Returns the number of log messages issued. The returned data dictionary uses integers as keys.
	#
	def getLogMsgCountsIntMap(self) -> typing.Dict[int,int]:
		return {
			int(EnumLogLevel.TRACE) : self.__logLevelCounterMap.get(int(EnumLogLevel.TRACE), 0),
			int(EnumLogLevel.DEBUG) : self.__logLevelCounterMap.get(int(EnumLogLevel.DEBUG), 0),
			int(EnumLogLevel.NOTICE) : self.__logLevelCounterMap.get(int(EnumLogLevel.NOTICE), 0),
			int(EnumLogLevel.INFO) : self.__logLevelCounterMap.get(int(EnumLogLevel.INFO), 0),
			int(EnumLogLevel.STDOUT) : self.__logLevelCounterMap.get(int(EnumLogLevel.STDOUT), 0),
			int(EnumLogLevel.SUCCESS) : self.__logLevelCounterMap.get(int(EnumLogLevel.SUCCESS), 0),
			int(EnumLogLevel.WARNING) : self.__logLevelCounterMap.get(int(EnumLogLevel.WARNING), 0),
			int(EnumLogLevel.ERROR) : self.__logLevelCounterMap.get(int(EnumLogLevel.ERROR), 0),
			int(EnumLogLevel.STDERR) : self.__logLevelCounterMap.get(int(EnumLogLevel.STDERR), 0),
			int(EnumLogLevel.EXCEPTION) : self.__logLevelCounterMap.get(int(EnumLogLevel.EXCEPTION), 0),
		}
	#

	#
	# Returns the number of log messages issued. The returned data dictionary uses strings as keys.
	#
	def getLogMsgCountsStrMap(self) -> typing.Dict[str,int]:
		return {
			str(EnumLogLevel.TRACE) : self.__logLevelCounterMap.get(int(EnumLogLevel.TRACE), 0),
			str(EnumLogLevel.DEBUG) : self.__logLevelCounterMap.get(int(EnumLogLevel.DEBUG), 0),
			str(EnumLogLevel.NOTICE) : self.__logLevelCounterMap.get(int(EnumLogLevel.NOTICE), 0),
			str(EnumLogLevel.INFO) : self.__logLevelCounterMap.get(int(EnumLogLevel.INFO), 0),
			str(EnumLogLevel.STDOUT) : self.__logLevelCounterMap.get(int(EnumLogLevel.STDOUT), 0),
			str(EnumLogLevel.SUCCESS) : self.__logLevelCounterMap.get(int(EnumLogLevel.SUCCESS), 0),
			str(EnumLogLevel.WARNING) : self.__logLevelCounterMap.get(int(EnumLogLevel.WARNING), 0),
			str(EnumLogLevel.ERROR) : self.__logLevelCounterMap.get(int(EnumLogLevel.ERROR), 0),
			str(EnumLogLevel.STDERR) : self.__logLevelCounterMap.get(int(EnumLogLevel.STDERR), 0),
			str(EnumLogLevel.EXCEPTION) : self.__logLevelCounterMap.get(int(EnumLogLevel.EXCEPTION), 0),
		}
	#

	#
	# Indicates whether this logger has ever seen such a log message.
	#
	def hasLogMsg(self, logLevel):
		return self.__logLevelCounterMap.get(int(logLevel), 0) > 0
	#

	def hasAtLeastWarning(self):
		return self.__maxLogLevelSeen.value >= int(EnumLogLevel.WARNING)
	#

	def hasAtLeastError(self):
		return self.__maxLogLevelSeen.value >= int(EnumLogLevel.ERROR)
	#

	def hasAtLeastException(self):
		return self.__maxLogLevelSeen.value >= int(EnumLogLevel.EXCEPTION)
	#

	def hasException(self):
		return self.hasLogMsg(EnumLogLevel.EXCEPTION)
	#

	def hasStdErr(self):
		return self.hasLogMsg(EnumLogLevel.STDERR)
	#

	def hasError(self):
		return self.hasLogMsg(EnumLogLevel.ERROR)
	#

	def hasStdOut(self):
		return self.hasLogMsg(EnumLogLevel.STDOUT)
	#

	def hasWarning(self):
		return self.hasLogMsg(EnumLogLevel.WARNING)
	#

	def hasInfo(self):
		return self.hasLogMsg(EnumLogLevel.INFO)
	#

	def hasNotice(self):
		return self.hasLogMsg(EnumLogLevel.NOTICE)
	#

	def hasDebug(self):
		return self.hasLogMsg(EnumLogLevel.DEBUG)
	#

	def descend(self, text, logLevel:EnumLogLevel = None) -> AbstractLogger:
		return DetectionLogger_v0(self.__logger.descend(text, logLevel), self.__logLevelCounterMap, self.__maxLogLevelSeen)
	#

	#
	# Clear the log message counters.
	#
	# NOTE: Please be aware that nested detection loggers will share the same (!!) objects that count log messages.
	# Invoking this method will therefore affect all log instances of the same tree!
	#
	def clear(self):
		self.__logLevelCounterMap = {}
		self.__maxLogLevelSeen.value = 0
		self.__logger.clear()
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	@staticmethod
	def create(logger:AbstractLogger):
		assert isinstance(logger, AbstractLogger)
		return DetectionLogger_v0(logger)
	#

#


