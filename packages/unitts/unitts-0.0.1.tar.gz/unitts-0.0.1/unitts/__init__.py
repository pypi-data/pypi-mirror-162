import weakref
from .engine import TTSEngine
from .version import __version__

_activeEngines = weakref.WeakValueDictionary()

def init(driverName):
	try:	
		eng = _activeEngine[driverName]
	except KeyError:
		eng = TTSEngine(driverName)
		_activeEngines[driverName] = eng
	return eng
