



import typing

from .EnumLogLevel import *
from .AbstractLogger import *





#
# This logger serves as a filter. Logging events are passed on to other loggers if they are within the
# accepting range of the filter.
#
class FilterLogger(AbstractLogger):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, logger:AbstractLogger, minLogLevel:typing.Union[int,EnumLogLevel]):
		super().__init__(None)

		assert isinstance(logger, AbstractLogger)
		self.__logger = logger

		assert isinstance(minLogLevel, (int,EnumLogLevel))
		self.__minLogLevel = int(minLogLevel)
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	@property
	def minLogLevel(self) -> EnumLogLevel:
		return EnumLogLevel.parse(self.__minLogLevel)
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption):
		if int(logEntryStruct[5]) >= self.__minLogLevel:
			self.__logger._logi(logEntryStruct, True)
	#

	def _log(self, timeStamp, logLevel, textOrException):
		if int(logLevel) >= self.__minLogLevel:
			self.__logger._log(timeStamp, logLevel, textOrException)
	#

	def _descend(self, logEntryStruct):
		return FilterLogger(self.__logger._descend(logEntryStruct), self.__minLogLevel)
	#

	def clear(self):
		self.__logger.clear()
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def setMinLogLevel(self, minLogLevel:typing.Union[EnumLogLevel,int]):
		assert isinstance(minLogLevel, (EnumLogLevel,int))

		self.__minLogLevel = int(minLogLevel)
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	@staticmethod
	def create(logger:AbstractLogger, minLogLevel:typing.Union[EnumLogLevel,int] = EnumLogLevel.WARNING):
		assert isinstance(logger, AbstractLogger)
		assert isinstance(minLogLevel, (int,EnumLogLevel))

		return FilterLogger(logger, minLogLevel)
	#

#






