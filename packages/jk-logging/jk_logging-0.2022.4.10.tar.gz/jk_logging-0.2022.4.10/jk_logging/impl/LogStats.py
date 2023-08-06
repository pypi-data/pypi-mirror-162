


import time
import typing

from ..EnumLogLevel import *






#
# This class counts log messages that occurred and provides various ways of retrieving this information later.
#
class LogStats(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self):
		self.__logLevelCounterMap = {}				# int -> int
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	#
	# Get the maximum log level seen.
	#
	# @return		EnumLogLevel maxLogLevel		The maximum log level seen (or <c>None</c> if no log message has yet been emitted.)
	#
	@property
	def maxLogLevelSeen(self) -> typing.Union[EnumLogLevel,None]:
		if self.__logLevelCounterMap:
			n = max(self.__logLevelCounterMap.keys())
			return EnumLogLevel.parse(n)
		else:
			return None
	#

	@property
	def hasAtLeastWarning(self) -> bool:
		_maxLogLevelSeen = self.maxLogLevelSeen
		if _maxLogLevelSeen is None:
			return False
		else:
			return int(_maxLogLevelSeen) >= int(EnumLogLevel.WARNING)
	#

	@property
	def hasAtLeastError(self) -> bool:
		_maxLogLevelSeen = self.maxLogLevelSeen
		if _maxLogLevelSeen is None:
			return False
		else:
			return int(_maxLogLevelSeen) >= int(EnumLogLevel.ERROR)
	#

	@property
	def hasAtLeastException(self) -> bool:
		_maxLogLevelSeen = self.maxLogLevelSeen
		if _maxLogLevelSeen is None:
			return False
		else:
			return int(_maxLogLevelSeen) >= int(EnumLogLevel.EXCEPTION)
	#

	@property
	def hasException(self) -> bool:
		return self.hasLogMsg(EnumLogLevel.EXCEPTION)
	#

	@property
	def hasStdErr(self) -> bool:
		return self.hasLogMsg(EnumLogLevel.STDERR)
	#

	@property
	def hasError(self) -> bool:
		return self.hasLogMsg(EnumLogLevel.ERROR)
	#

	#
	# This property returns <c>True</c> if this seen any of these log levels: ERROR, STDERR, EXCEPTION.
	#
	@property
	def hasAnyError(self) -> bool:
		return self.hasLogMsg(EnumLogLevel.ERROR) or self.hasLogMsg(EnumLogLevel.STDERR) or  self.hasLogMsg(EnumLogLevel.EXCEPTION)
	#

	@property
	def hasStdOut(self) -> bool:
		return self.hasLogMsg(EnumLogLevel.STDOUT)
	#

	@property
	def hasWarning(self) -> bool:
		return self.hasLogMsg(EnumLogLevel.WARNING)
	#

	@property
	def hasInfo(self) -> bool:
		return self.hasLogMsg(EnumLogLevel.INFO)
	#

	@property
	def hasNotice(self) -> bool:
		return self.hasLogMsg(EnumLogLevel.NOTICE)
	#

	@property
	def hasDebug(self) -> bool:
		return self.hasLogMsg(EnumLogLevel.DEBUG)
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# Returns the number of log messages issued for a specific log level.
	#
	def getLogMsgCount(self, logLevel:typing.Union[int,EnumLogLevel]) -> int:
		nLogLevel = int(logLevel)
		return self.__logLevelCounterMap.get(nLogLevel, 0)
	#

	#
	# Returns the number of log messages seen.
	#
	def __len__(self):
		return sum(self.__logLevelCounterMap.values())
	#

	#
	# If invoked this method will increment the specified counter for a log level.
	#
	def increment(self, logLevel:typing.Union[int,EnumLogLevel]):
		nLogLevel = int(logLevel)
		self.__logLevelCounterMap[nLogLevel] = self.__logLevelCounterMap.get(nLogLevel, 0) + 1
	#

	#
	# Returns the number of log messages issued. The returned data dictionary uses integers as keys.
	#
	def getLogMsgCountsIntMap(self) -> typing.Dict[int,int]:
		ret = {}
		for logLevel in EnumLogLevel:
			ret[int(logLevel)] = self.__logLevelCounterMap.get(int(logLevel), 0)
		return ret
	#

	#
	# Returns the number of log messages issued. The returned data dictionary uses strings as keys.
	#
	def getLogMsgCountsStrMap(self) -> typing.Dict[str,int]:
		ret = {}
		for logLevel in EnumLogLevel:
			ret[str(logLevel)] = self.__logLevelCounterMap.get(int(logLevel), 0)
		return ret
	#

	#
	# Indicates whether this logger has ever seen such a log message.
	#
	def hasLogMsg(self, logLevel:typing.Union[int,EnumLogLevel]):
		return self.__logLevelCounterMap.get(int(logLevel), 0) > 0
	#

	#
	# Clear the log message counters.
	#
	# NOTE: Please be aware that nested detection loggers will share the same (!!) objects that count log messages.
	# Invoking this method will therefore affect all log instances of the same tree!
	#
	def clear(self):
		self.__logLevelCounterMap = {}
	#

#









