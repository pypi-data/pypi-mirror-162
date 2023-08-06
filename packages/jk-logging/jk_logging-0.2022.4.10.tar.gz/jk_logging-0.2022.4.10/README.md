jk_logging
==========

Introduction
------------

This python module provides a logging infrastructure. It contains various classes to implement logging and aid in debugging.

Information about this module can be found here:

* [github.org](https://github.com/jkpubsrc/python-module-jk-logging)
* [pypi.python.org](https://pypi.python.org/pypi/jk_logging)

How to use this module
----------------------





Basic Architecture
------------------

Documentation of Log Objects
----------------------------

In order to use loggers you need to know which classes there are end what kind of methods they offer for use. The next subchapters
will provide you with that information.

### Common Methods

Every log object will provide the following methods for use:

```python
#
# Perform logging with log level DEBUG.
#
# @param	string text		The text to write to this logger.
#
def debug(self, text)
```

```python
#
# Perform logging with log level NOTICE.
#
# @param	string text		The text to write to this logger.
#
def notice(self, text)
```

```python
#
# Perform logging with log level INFO.
#
# @param	string text		The text to write to this logger.
#
def info(self, text)
```

```python
#
# Perform logging with log level STDOUT.
# This method is intended to be used in conjunction with STDOUT handlers.
#
# @param	string text		The text to write to this logger.
#
def stdout(self, text)
```

```python
#
# Perform logging with log level WARNING.
#
# @param	string text		The text to write to this logger.
#
def warning(self, text)
```

```python
#
# Perform logging with log level ERROR.
#
# @param	string text		The text to write to this logger.
#
def error(self, text)
```

```python
#
# Perform logging with log level STDERR.
# This method is intended to be used in conjunction with STDERR handlers.
#
# @param	string text		The text to write to this logger.
#
def stderr(self, text)
```

```python
#
# Perform logging with log level EXCEPTION.
#
# @param	Exception exception		The exception to write to this logger.
#
def exception(self, exception)
```

```python
#
# If this logger is buffering log messages, clear all log messages from this buffer.
# If this logger has references to other loggers, such as a <c>FilterLogger</c>
# or a <c>MulticastLogger</c>
#
def clear(self)
```

Other log objects will provide additional methods.

### `BufferLogger`

Objects of type `BufferLogger` will provide the following additional methods:

```python
#
# Return a list of strings that contains the data stored in this logger.
# Standard formatting is used for output.
#
# @return		string[]		Returns an array of strings ready to be written to the console or a file.
#
def getBufferDataAsStrList(self)
```

```python
#
# Return a list of tuples that contains the data stored in this logger.
#
# @return		tuple[]		Returns an array of tuples. Each tuple will contain the following fields:
#							* int timeStamp : The time stamp since Epoch in seconds.
#							* EnumLogLevel logLevel : The log level of this log entry.
#							* string|Exception textOrException : A log message or an execption object.
#
def getBufferDataAsTupleList(self)
```

```python
#
# Return a single string that contains the data stored in this logger.
# Standard formatting is used for output.
#
# @return		string		Returns a single string ready to be written to the console or a file.
#
def getBufferDataAsStr(self)
```

```python
#
# Forward the log data stord in this logger to another logger.
#
# @param		AbstractLogger logger			Another logger that will receive the log data.
#
def forwardTo(self, logger, bClear = False)
```

Instantiation Based on Configuration Information Provided
---------------------------------------------------------

Often it is convenient for applications to provide some detailed way of specifying how data should be logged. For exactly that reason
this logging framework provides a function that is capable of creating loggers from some kind of description. Example:

```python
import jk_logging

logger = jk_logging.instantiate({
	"type": "MulticastLogger",
	"nested": [
		{
			"type": "ConsoleLogger"
		},
		{
			"type": "FileLogger",
			"filePath": "mylogfile-%Y-%m-%d.log",
			"rollOver": "day"
		}
	]
})
```

(more description comeing soon)

Examples
--------

Here is some example code that demonstrates the use of the various loggers available:

```python
print()
print("-- ConsoleLogger --")
print()

clog = ConsoleLogger.create()

clog.debug("This is a test for DEBUG.")
clog.notice("This is a test for NOTICE.")
clog.info("This is a test for INFO.")
clog.warning("This is a test for WARNING.")
clog.error("This is a test for ERROR.")

print()
print("-- Exception Handling --")
print()

def produceError():
	a = 5
	b = 0
	c = a / b

try:
	clog.notice("Now let's try a calculation that will fail ...")
	produceError()
except Exception as ee:
	clog.error(ee)

print()
print("-- FilterLogger --")
print()

flog = FilterLogger.create(clog, EnumLogLevel.WARNING)

flog.notice("This message will not appear in the log output.")
flog.error("This message will appear in the log output.")

print()
print("-- DetectionLogger --")
print()

dlog = DetectionLogger.create(clog)
dlog.notice("A notice.")
dlog.debug("A debug message.")
dlog.info("An informational message.")
dlog.debug("Another debug message.")
print(dlog.getLogMsgCountsStrMap())
print("Do we have debug messages? Answer: " + str(dlog.hasDebug()))
print("Do we have error messages? Answer: " + str(dlog.hasError()))

print()
print("-- BufferLogger --")
print()

blog = BufferLogger.create()
blog.info("First we write something to a buffer.")
blog.info("And something more.")
blog.notice("And more.")
blog.debug("And even more.")
blog.info("Then we write it to the console by forwarding the data to another logger.")
blog.forwardTo(clog)

print()
print("-- MulticastLogger --")
print()

mlog = MulticastLogger.create(clog, clog)
mlog.info("This message gets written twice.")

print()
print("-- NamedMulticastLogger --")
print()

nmlog = NamedMulticastLogger.create()
nmlog.addLogger("log1", clog)
nmlog.addLogger("log2", clog)
nmlog.info("This message gets written twice.")
nmlog.removeLogger("log1")
nmlog.info("This message gets written once.")
```

Things to do
------------

Any help in implementing additional log classes and improving on the existing ones is appreciated. Feel free to contact me if you are interested in colaborating.

Contact Information
-------------------

This is Open Source code. That not only gives you the possibility of freely using this code it also
allows you to contribute. Feel free to contact the author(s) of this software listed below, either
for comments, collaboration requests, suggestions for improvement or reporting bugs:

* Jürgen Knauth: jknauth@uni-goettingen.de, pubsrc@binary-overflow.de

License
-------

This software is provided under the following license:

* Apache Software License 2.0



