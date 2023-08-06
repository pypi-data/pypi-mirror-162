

import typing

from .AbstractTimeStampFormatter import AbstractTimeStampFormatter
from .AbstractLogMessageFormatter import AbstractLogMessageFormatter
from .DefaultTimeStampFormatter import DefaultTimeStampFormatter






#
# This is a default formatter for log messages. It produces human readable output for log messages.
#
class JSONLogMessageFormatter(AbstractLogMessageFormatter):

	################################################################################################################################
	## Constants
	################################################################################################################################

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, bIncludeIDs = False, fillChar = "\t", timeStampFormatter = None):
		self.__fillChar = fillChar
		self.__indentBuffer = fillChar
		self.__includeIDs = bIncludeIDs

		if timeStampFormatter is None:
			timeStampFormatter = DefaultTimeStampFormatter()
		else:
			assert callable(timeStampFormatter)
		self.__timeStampFormatter = timeStampFormatter
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	@property
	def timeStampFormatter(self) -> typing.Union[AbstractTimeStampFormatter,None]:
		return self.__timeStampFormatter
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def format(self, logEntryStruct):
		sID = str(logEntryStruct[1]) if (logEntryStruct != None) else "-"
		indentationLevel = logEntryStruct[2]
		while indentationLevel > len(self.__indentBuffer):
			self.__indentBuffer += self.__fillChar
		sIndent = self.__indentBuffer[0:indentationLevel]
		sParentID = str(logEntryStruct[3]) if (logEntryStruct != None) else "-"
		sTimeStamp = "[" + self.__timeStampFormatter(logEntryStruct[4]) + "]"
		sLogType = AbstractLogMessageFormatter.LOG_LEVEL_TO_STR_MAP__RIGHT_ALIGNED[logEntryStruct[5]]

		s = sIndent
		if self.__includeIDs:
			s += "(" + sParentID + "|" + sID + ") "
		s += sTimeStamp + " "

		if logEntryStruct[0] == "txt":
			sLogMsg = logEntryStruct[6]
			return s + sLogType + ": " + sLogMsg
		elif logEntryStruct[0] == "ex":
			sExClass = logEntryStruct[6]
			sLogMsg = logEntryStruct[7]
			ret = []
			if logEntryStruct[8] != None:
				for (stPath, stLineNo, stModuleName, stLine) in logEntryStruct[8]:
					ret.append(s + "STACKTRACE: " + stPath + ":" + str(stLineNo) + " " + stModuleName + "    # " + stLine)
			ret.append(s + " "  + sLogType + ": " + sExClass + ": " + sLogMsg)
			return ret
		elif logEntryStruct[0] == "desc":
			sLogMsg = logEntryStruct[6]
			return s + sLogType + ": " + sLogMsg
		else:
			raise Exception()
	#

#



JSON_LOG_MESSAGE_FORMATTER = JSONLogMessageFormatter()








