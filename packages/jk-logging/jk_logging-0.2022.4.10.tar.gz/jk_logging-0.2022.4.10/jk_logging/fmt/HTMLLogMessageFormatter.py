

import typing

from ..EnumLogLevel import EnumLogLevel
from .AbstractTimeStampFormatter import AbstractTimeStampFormatter
from .AbstractLogMessageFormatter import AbstractLogMessageFormatter
from .DefaultTimeStampFormatter import DefaultTimeStampFormatter
from ..EnumExtensitivity import EnumExtensitivity





#
# This is a default formatter for log messages. It produces human readable output for log messages.
#
class HTMLLogMessageFormatter(AbstractLogMessageFormatter):

	################################################################################################################################
	## Nested Classes
	################################################################################################################################

	################################################################################################################################
	## Constants
	################################################################################################################################

	LOG_LEVEL_TO_COLOR_MAP = {
		EnumLogLevel.TRACE: "#a0a0a0",
		EnumLogLevel.DEBUG: "#a0a0a0",
		EnumLogLevel.NOTICE: "#a0a0a0",
		EnumLogLevel.STDOUT: "#404040",
		EnumLogLevel.INFO: "#404040",
		EnumLogLevel.WARNING: "#804040",
		EnumLogLevel.ERROR: "#800000",
		EnumLogLevel.STDERR: "#900000",
		EnumLogLevel.EXCEPTION: "#900000",
		EnumLogLevel.SUCCESS: "#009000",
	}
	#STACKTRACE_COLOR = "\033[38;2;204;102;0m"
	#STACKTRACE_COLOR = "#800000"
	STACKTRACE_COLOR = "#700000"

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self,
			bIncludeIDs:bool = False,
			fillChar:str = "&nbsp;&nbsp;&nbsp;&nbsp;",
			bLinesWithBRTag:bool = False,
			extensitivity:EnumExtensitivity = EnumExtensitivity.FULL,
			timeStampFormatter = None
		):

		assert isinstance(bIncludeIDs, bool)
		self.__fillChar = fillChar

		assert isinstance(fillChar, str)
		self.__indentBuffer = fillChar

		assert isinstance(bIncludeIDs, bool)
		self.__includeIDs = bIncludeIDs

		assert isinstance(extensitivity, EnumExtensitivity)
		self.__outputMode = extensitivity

		assert isinstance(bLinesWithBRTag, bool)
		self.__bLinesWithBRTag = bLinesWithBRTag

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

	@property
	def outputMode(self) -> EnumExtensitivity:
		return self.__outputMode
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# REMOVED: Instances of this class must be read-only and must not be changable at runtime.
	#
	#def setOutputMode(self, outputMode:typing.Union[EnumExtensitivity,None]):
	#	if outputMode is None:
	#		outputMode = EnumExtensitivity.FULL
	#	self.__outputMode = outputMode
	#

	#
	# Create and return a string representation of the specified log entry.
	#
	# @param		list logEntryStruct			A log entry structure. See <c>AbstractLogger._logi()</c> for a detailed description.
	# @return		str							Returns the string representation of the log message.
	#
	def format(self, logEntryStruct):
		term = "</span>"
		if self.__bLinesWithBRTag:
			term += "</br>"

		sID = str(logEntryStruct[1]) if (logEntryStruct != None) else "-"
		indentationLevel = logEntryStruct[2]
		while indentationLevel > len(self.__indentBuffer):
			self.__indentBuffer += self.__fillChar
		sIndent = self.__indentBuffer[0:indentationLevel*len(self.__fillChar)]
		sParentID = str(logEntryStruct[3]) if (logEntryStruct != None) else "-"
		sTimeStamp = "[" + self.__timeStampFormatter(logEntryStruct[4]) + "]"
		sLogType = AbstractLogMessageFormatter.LOG_LEVEL_TO_STR_MAP__LEFT_ALIGNED[logEntryStruct[5]]

		if self.__includeIDs:
			s3 = "(" + sParentID + "|" + sID + ") " + sTimeStamp + " "
		else:
			s3 = sTimeStamp + " "
		s1 = sIndent + "<span style=\"color:" + HTMLLogMessageFormatter.LOG_LEVEL_TO_COLOR_MAP[logEntryStruct[5]] + "\">" + s3
		s2 = sIndent + "<span style=\"color:" + HTMLLogMessageFormatter.STACKTRACE_COLOR + "\">" + s3

		if logEntryStruct[0] == "txt":
			sLogMsg = logEntryStruct[6]
			if sLogMsg is None:
				sLogMsg = ""
			return s1 + sLogType + ": " + sLogMsg + term
		elif logEntryStruct[0] == "ex":
			sExClass = logEntryStruct[6]
			sLogMsg = logEntryStruct[7]
			ret = []
			if logEntryStruct[8] != None:
				if self.__outputMode == EnumExtensitivity.FULL:
					for (stPath, stLineNo, stModuleName, stLine) in logEntryStruct[8]:
						ret.append(s2 + "STACKTRACE: " + stPath + ":" + str(stLineNo) + " " + stModuleName + "    # " + stLine + term)
				elif self.__outputMode == EnumExtensitivity.SHORTED:
					stPath, stLineNo, stModuleName, stLine = logEntryStruct[8][-1]
					ret.append(s2 + "STACKTRACE: " + stPath + ":" + str(stLineNo) + " " + stModuleName + "    # " + stLine + term)
			if sLogMsg is None:
				sLogMsg = ""
			ret.append(s1 + sLogType + ": " + sExClass + ": " + sLogMsg + term)
			return ret
		elif logEntryStruct[0] == "desc":
			sLogMsg = logEntryStruct[6]
			if sLogMsg is None:
				sLogMsg = ""
			return s1 + sLogType + ": " + sLogMsg + term
		else:
			raise Exception()
	#

#



HTML_LOG_MESSAGE_FORMATTER = HTMLLogMessageFormatter()







