



from ..EnumLogLevel import EnumLogLevel









def createLogMsgTypeStrMap(bPrefixWithSpacesToSameLength = False):

	def _getLogLevelStr(logLevel):
		s = str(logLevel)
		pos = s.rfind(".")
		if pos >= 0:
			s = s[pos+1:]
		return s
	#

	maxLogLevelLength = len("STACKTRACE")
	for logLevel in EnumLogLevel:
		s = _getLogLevelStr(logLevel)
		logLevelLength = len(s)
		if logLevelLength > maxLogLevelLength:
			maxLogLevelLength = logLevelLength

	logLevelToStrDict = {}
	for logLevel in EnumLogLevel:
		s = _getLogLevelStr(logLevel)
		if bPrefixWithSpacesToSameLength:
			while len(s) < maxLogLevelLength:
				s = " " + s
		logLevelToStrDict[logLevel] = s

	return logLevelToStrDict
#









