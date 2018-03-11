# fcst.py

class Scenario (object):
	events = []
	allCases = []

	def __init__(self, es):
		self.events = es

	def probability(self, signals, givens = []):
		cs =  self.cases()
		numerator = 0.0
		denominator = 0.0
		for c in cs:
			if c.hasAll(givens):
				denominator += c.probability

				if c.hasAll(signals):
					numerator += c.probability

		if denominator == 0.0:
			return 0.0
		else:
			return numerator / denominator

	_caseLookup = None
	def cases(self):
		if self._caseLookup is None:
			self._caseLookup = {}
			self._cases(1.0, [], [])
			for cKey in self._caseLookup:
				self.allCases.append(self._caseLookup[cKey])
		return self.allCases

	def _cases(self, probability, eventsProcessed, signalsRaised):
		# Find first unprocessed event that has been triggered
		nextEvent = None
		for e in self.events:
			if e not in eventsProcessed:
				if e.isTriggered(signalsRaised):
					nextEvent = e
					break

		if nextEvent is not None:
			nextEventsProcessed = list(eventsProcessed)
			nextEventsProcessed.append(nextEvent)

			for o in nextEvent.outcomes:
				nextSignalsRaised = list(signalsRaised)

				for s in o.signals:
					if not s in nextSignalsRaised:
						nextSignalsRaised.append(s)

				self._cases(probability * o.probability, nextEventsProcessed, nextSignalsRaised)
		else:
			# Calculate signature from signals
			signature = ""

			for s in sorted(signalsRaised):
				signature += s + "+"

			if signature in self._caseLookup:
				self._caseLookup[signature].probability += probability
			else:
				newCase = Case(signalsRaised, probability)
				self._caseLookup[signature] = newCase



class Case (object):
	signals = []
	probability = 0

	def __init__(self, ss, p):
		self.signals = ss
		self.probability = p

	def hasAll(self, ss):
		for s in ss:
			if s not in self.signals:
				return False
		return True


class Event (object):
	scenario = None
	outcomes = []
	triggers = []

	def __init__(self, os, trigs = None):
		self.outcomes = os
		if trigs is not None:
			self.triggers = trigs

		# Make sure a default outcome exists
		d = 1.0
		for o in os:
			d -= o.probability

		if d > 0.0:
			self.outcomes.append(Outcome(d, []))

	def isTriggered(self, ss):
		for t in self.triggers:
			if t not in ss:
				return False
		return True



class Outcome (object):
	probability = 0
	signals = []

	def __init__(self, p, sigs):
		self.probability = p
		self.signals = sigs
