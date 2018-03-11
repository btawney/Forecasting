# fcst.py

class Scenario (object):
	events = []

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

	_allCases = None
	def cases(self):
		if self._allCases is None:
			lookup = {}
			self._cases(1.0, self.events, [], lookup)
			self._allCases = []
			for cKey in lookup:
				self._allCases.append(lookup[cKey])
		return self._allCases

	def _cases(self, probability, unprocessedEvents, signalsRaised, caseLookup):
		# Find first unprocessed event that has been triggered
		nextEvent = None
		idx = 0
		for e in unprocessedEvents:
			if e.isTriggered(signalsRaised):
				nextEvent = e
				break
			idx += 1

		if nextEvent is not None:
			nextUnprocessedEvents = unprocessedEvents[0:idx] + unprocessedEvents[idx + 1:]

			for o in nextEvent.outcomes:
				nextSignalsRaised = list(signalsRaised)

				for s in o.signals:
					if not s in nextSignalsRaised:
						nextSignalsRaised.append(s)

				self._cases(probability * o.probability,
					nextUnprocessedEvents,
					nextSignalsRaised,
					caseLookup)
		else:
			# Calculate signature from signals
			signature = ""

			for s in sorted(signalsRaised):
				signature += s + "+"

			if signature in caseLookup:
				caseLookup[signature].probability += probability
			else:
				newCase = Case(signalsRaised, probability)
				caseLookup[signature] = newCase



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
