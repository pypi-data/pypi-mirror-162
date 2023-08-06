


from .EnumLogLevel import EnumLogLevel
from .AbstractLogger import AbstractLogger
from .impl.LogStats import LogStats








#
# This logger keeps track of how many log messages of what type have been issued.
#
# NOTE: Be aware that all nested detection loggers will share the same (!!) LogStats object to count log messages.
#
class DetectionLogger(AbstractLogger):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, logger:AbstractLogger, logStats:LogStats = None):
		super().__init__(None)

		assert isinstance(logger, AbstractLogger)
		self.__logger = logger

		if logStats is None:
			self.__logStats = LogStats()
		else:
			assert isinstance(logStats, LogStats)
			self.__logStats = logStats
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	#
	# Returns the LogStats object that is used by this and all nested DetetionLogger instances to count log messages.
	#
	# NOTE: Be aware that all nested detection loggers will share the same (!!) LogStats object to count log messages.
	#
	@property
	def stats(self) -> LogStats:
		return self.__logStats
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _descend(self, logEntryStruct):
		self.__logStats.increment(logEntryStruct[5])
		descendedLogger = self.__logger._descend(logEntryStruct)
		return DetectionLogger(descendedLogger, self.__logStats)
	#

	def _logi(self, logEntryStruct, bNeedsIndentationLevelAdaption:bool):
		self.__logStats.increment(logEntryStruct[5])
		self.__logger._logi(logEntryStruct, bNeedsIndentationLevelAdaption)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def descend(self, text, logLevel:EnumLogLevel = None) -> AbstractLogger:
		return DetectionLogger(self.__logger.descend(text, logLevel), self.__logStats)
	#

	#
	# Clear the log message counters.
	#
	# NOTE: Please be aware that nested detection loggers will share the same (!!) objects that count log messages.
	# Invoking this method will therefore affect all log instances of the same tree!
	#
	def clear(self):
		self.__logStats.clear()
		self.__logger.clear()
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	@staticmethod
	def create(logger:AbstractLogger):
		assert isinstance(logger, AbstractLogger)
		return DetectionLogger(logger)
	#

#


