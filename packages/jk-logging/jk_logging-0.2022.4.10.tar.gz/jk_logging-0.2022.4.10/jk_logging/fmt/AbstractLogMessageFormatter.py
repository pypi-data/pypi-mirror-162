


import typing
import abc


from ..EnumLogLevel import EnumLogLevel
from ..impl.createLogMsgTypeStrMap import createLogMsgTypeStrMap
from .AbstractTimeStampFormatter import AbstractTimeStampFormatter








class AbstractLogMessageFormatter(object):

	################################################################################################################################
	## Constants
	################################################################################################################################

	LOG_LEVEL_TO_STR_MAP__LEFT_ALIGNED = createLogMsgTypeStrMap(False)
	LOG_LEVEL_TO_STR_MAP__RIGHT_ALIGNED = createLogMsgTypeStrMap(True)

	################################################################################################################################
	## Constructor
	################################################################################################################################

	################################################################################################################################
	## Properties
	################################################################################################################################

	@property
	def timeStampFormatter(self) -> typing.Union[AbstractTimeStampFormatter,None]:
		return None
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# Create and return a string representation of the specified log entry. Overwrite this method to implement a log message formatter.
	#
	# @param		list logEntryStruct			A log entry structure. See <c>AbstractLogger._logi()</c> for a detailed description.
	# @return		str							Returns the string representation of the log message.
	#
	@abc.abstractmethod
	def format(self, logEntryStruct):
		raise NotImplementedError()
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

#




