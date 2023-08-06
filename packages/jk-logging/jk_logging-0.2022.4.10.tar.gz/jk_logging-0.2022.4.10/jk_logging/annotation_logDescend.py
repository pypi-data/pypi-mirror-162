


import inspect
import re

from .AbstractLogger import AbstractLogger









def logDescend(logText, bWithFinalSuccessMsg:bool = False):
	if isinstance(logText, str):
		bIsCallable = False
		bCheckForNamedArguments = re.match(r"^.*\{.*\}", logText) is not None
	elif callable(logText):
		# we don't know at this time; we must resolve at runtime in any cas :-/
		bIsCallable = True
		bCheckForNamedArguments = True
	else:
		raise Exception("Log text or callable expected!")

	# ----

	assert isinstance(bWithFinalSuccessMsg, bool)

	def wrapper(func):
		if bCheckForNamedArguments:
			#print("-"*20)
			#print(func)
			argsList = inspect.getfullargspec(func).args
			#print(x)
			#print("-"*20)

			if not argsList:
				# we might have a wrapper that hides all arguments
				# in this case we will not be able to resolve arguments later if they are not provided explicitely; well, that's some limitiation we have to live with;
				regularArgNames = None
			else:
				# verify that this is indeed a method
				if argsList[0] != "self":
					raise Exception("logDescend() can only be used for methods!")
				# get the regular arguments that are provided as a list;
				regularArgNames = argsList[1:]
		else:
			regularArgNames = None

		def func_wrapper(*args, **kwargs):
			# build the argument map the log text build process can consider
			argMap = dict(kwargs)
			if regularArgNames is not None: 		# if regular list of argument names not available -> skip this step
				for argName, argValue in zip(regularArgNames, args[1:]):
					argMap[argName] = argValue
			# build the log text
			if bIsCallable:
				s = logText(args[0]).format(**argMap)
			else:
				s = logText.format(**argMap)

			if args:
				log = args[-1]
				if log is None:
					retVal = func(*args, **kwargs)
					return retVal
				elif isinstance(log, AbstractLogger):
					with log.descend(s) as log2:
						args2 = list(args)
						args2[-1] = log2
						retVal = func(*args2, **kwargs)
						if bWithFinalSuccessMsg:
							log2.success("Success.")
						return retVal
				else:
					print("WARNING: Wrapped method " + repr(func) + " did not receive a valid logger: " + str(func))
					retVal = func(*args, **kwargs)
					return retVal
			elif "log" in kwargs:
				log = kwargs["log"]
				if isinstance(log, AbstractLogger):
					with log.descend(s) as log2:
						kwargs2 = dict(kwargs)
						kwargs2[log] = log2
						retVal = func(*args, **kwargs2)
						if bWithFinalSuccessMsg:
							log2.success("Success.")
						return retVal
				elif log is None:
					retVal = func(*args, **kwargs)
					return retVal
				else:
					print("WARNING: Wrapped method " + repr(func) + " did not receive a valid logger: " + str(func))
					retVal = func(*args, **kwargs)
					return retVal
			else:
				print("WARNING: Wrapped method " + repr(func) + " does not have a logger: " + str(func))
		#

		return func_wrapper
	#

	return wrapper
#










