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
	def cases(self, turns = 1):
		if self._allCases is None:
			lookup = {}
			self._cases(1.0, self.events, [], lookup, [], turns)
			self._allCases = []
			for cKey in lookup:
				self._allCases.append(lookup[cKey])
		return self._allCases

	def _cases(self, probability, unprocessedEvents, signalsRaised, caseLookup, defaultEvents, turns):
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

			defaultProbability = 1.0
			for o in nextEvent.outcomes:
				defaultProbability -= o.probability

				nextSignalsRaised = list(signalsRaised)

				for s in o.signals:
					if not s in nextSignalsRaised:
						nextSignalsRaised.append(s)

				self._cases(probability * o.probability,
					nextUnprocessedEvents,
					nextSignalsRaised,
					caseLookup,
					defaultEvents,
					turns)

			# If default probability is not zero then process the default outcome
			if defaultProbability > 0:
				self._cases(probability * defaultProbability,
					nextUnprocessedEvents,
					signalsRaised,
					caseLookup,
					defaultEvents + [nextEvent],
					turns)
		else:
			# If this is the last turn, or if there are no default events, then add to cases
			if turns == 1 or len(defaultEvents) == 0 or probability == 0:
				# Calculate signature from signals
				signature = ""

				for s in sorted(signalsRaised):
					signature += s + "+"

				if signature in caseLookup:
					caseLookup[signature].probability += probability
				else:
					newCase = Case(signalsRaised, probability)
					caseLookup[signature] = newCase
			else:
				# Process the next turn using the default events as the unprocessed events
				self._cases(probability,
					defaultEvents,
					signalsRaised,
					caseLookup,
					[],
					turns - 1)


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
