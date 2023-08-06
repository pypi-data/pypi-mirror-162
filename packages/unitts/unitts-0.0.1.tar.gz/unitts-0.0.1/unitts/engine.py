from text2sentences import text_to_sentences
from appPublic.uniqueID import getID
import importlib

def buildDriver(tts, driverName):
	_module = importlib.import_module(driverName)
	return _module.buildDriver(tts)
	
class TTSEngine:
	"""
	Usages:
	"""
	def __init__(self, driverName):
		self.driver = buildDriver(self, driverName)
		self._connects = {}
		self._sentences = []
		self.current_id = None
		self.current_sentences = None

	def connect(self, subject, func):
		if subject in ['started-sentence', 'started-word',
						'started-text', 'finished-text']:
			self._connects.update({subject:func})
	
	def disconnect(self, subject):
		if subject in ['started-sentence', 'started-word',
						'started-text', 'finished-text']:
			del self._connects[subject]
		
	def say(self, text, pos=0):
		sentences = text_to_sentences(text)
		id = getID()
		self._sentences.append([id,sentences])
		if self.current_id is None:
			self.go_next_text()
			self.say_current_sentences(pos)
		return id

	def go_next_text(self):
		if len(self._sentences) < 1:
			return False
		self.current_id, self.current_sentences = \
			self._sentences.pop(0)
		return True

	def get_next_sentence(self):
		if len(self.current_sentences) < 1:
			return None
		return self.current_sentences.pop(0)

	def notify(self, subject, *args, **kw):
		for s,f in self._connects.items():
			if s == subject:
				f(*args, **kw)

	def isBusy(self):
		return self.driver.isBusy()

	def say_current_sentences(self):
		while True:
			s = self.get_next_sentence()
			if s is None:
				self.notify('finished-text', id=self.current_id)
				f = self.go_next_text()
				if not f:
					return
				self.ccurrent_pos = 0
				self.notify('started-text', id=self.current_id)
			if s is None:
				return
			pos = s.start_pos + len(s.text)
			if s.start<= self.current_pos and \
							pos >= self.ccurrent_pos:
				break
		self.current_pos += len(s.text)
		self.driver.say(s)

	def stop(self):
		pass

	def pause(self):
		pass

	def resume(self):
		pass


