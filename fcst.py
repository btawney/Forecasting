# fcst.py

class Scenario (object):
	events = []

	def __init__(self, es):
		self.events = es

	def probability(self, signals, givens = [], turns = 1):
		cs =  self.cases(turns)
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

	def cases(self, turns = 1):
		lookup = {}
		self._cases(1.0, self.events, [], lookup, [], turns)
		allCases = []
		for cKey in lookup:
			allCases.append(lookup[cKey])
		return allCases

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

				isDefaultOutcome = False
				for s in o.signals:
					if s[0] == "~":
						isDefaultOutcome = True
					if not s in nextSignalsRaised:
						nextSignalsRaised.append(s)

				nextDefaultEvents = list(defaultEvents)
				if isDefaultOutcome:
					nextDefaultEvents.append(nextEvent)

				self._cases(probability * o.probability,
					nextUnprocessedEvents,
					nextSignalsRaised,
					caseLookup,
					nextDefaultEvents,
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
					if signature != "":
						signature += ","
					signature += s

				if signature in caseLookup:
					caseLookup[signature].probability += probability
				else:
					newCase = Case(signalsRaised, probability)
					caseLookup[signature] = newCase
			else:
				# Process the next turn. First, remove any default signals,
				# then process a new turn with the unprocessed events and the
				# default events
				nonDefaultSignalsRaised = []
				for s in signalsRaised:
					if s[0] != "~":
						nonDefaultSignalsRaised.append(s)

				self._cases(probability,
					unprocessedEvents + defaultEvents,
					nonDefaultSignalsRaised,
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

	def defaultProbability(self):
		dp = 1.0

		for o in self.outcomes:
			dp -= o.probability
		
		if dp < 0.0:
			return 0.0
		
		return dp

	def CombinedWith(self, other):
		newOutcomes = []

		selfDefaultProbability = self.defaultProbability()
		otherDefaultProbability = other.defaultProbability()

		# Determine whether a default outcome should exist for either event
		for selfOutcome in self.outcomes:
			for otherOutcome in other.outcomes:
				newOutcomes.append(Outcome(
					selfOutcome.probability * otherOutcome.probability,
					signalSummary(selfOutcome.signals + otherOutcome.signals)))

			if otherDefaultProbability > 0:
				newOutcomes.append(Outcome(
					selfOutcome.probability * otherDefaultProbability,
					signalSummary(selfOutcome.signals)))

		if selfDefaultProbability > 0:
			for otherOutcome in other.outcomes:
				newOutcomes.append(Outcome(
					selfDefaultProbability * otherOutcome.probability,
					signalSummary(otherOutcome.signals)))

			if otherDefaultProbability > 0:
				newOutcomes.append(Outcome(
					selfDefaultProbability * otherDefaultProbability,
					[]))

		return Event(newOutcomes)

	def Grouped(self, groupSize):
		# Build a collection of groups in powers of two
		binaryLookup = {}
		n = 1
		model = Event(self.outcomes)
		binaryLookup[n] = model
		while n * 2 <= groupSize:
			n *= 2
			model = model.CombinedWith(model)
			binaryLookup[n] = model

		# Combine the appropriate generated groups to make one of the correct size
		# note that model is already by definition one of the groups we want
		remainder = groupSize - n
		n /= 2
		while remainder > 0:
			if remainder >= n:
				remainder -= n
				model = model.CombinedWith(binaryLookup[n])
			n /= 2

		return model


def signalSummary(signals):
	tally = {}
	for signal in signals:
		if "*" in signal:
			baseSignal = signal[0:signal.index("*")]
			baseCount = int(signal[signal.index("*")+1:])
		else:
			baseSignal = signal
			baseCount = 1

		if baseSignal not in tally:
			tally[baseSignal] = 0

		tally[baseSignal] += baseCount

	result = []
	for signal in tally:
		result.append(signal + "*" + str(tally[signal]))

	return result


class Outcome (object):
	probability = 0
	signals = []

	def __init__(self, p, sigs):
		self.probability = p
		self.signals = sigs
