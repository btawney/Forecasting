# fcst.py

anonymousSignalNumber = 0
def anonymousSignal():
	global anonymousSignalNumber
	anonymousSignalNumber += 1
	return ")" + str(anonymousSignalNumber)

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

	def cases(self):
		lookup = {}
		self._cases(1.0, self.events, [], lookup, [], 0.0)
		allCases = []
		for cKey in lookup:
			allCases.append(lookup[cKey])
		return allCases

	def _cases(self, probability, unprocessedEvents, signalsRaised, caseLookup, defaultEvents, time):
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
					time + o.duration)

			# If default probability is not zero then process the default outcome
			if defaultProbability > 0:
				self._cases(probability * defaultProbability,
					nextUnprocessedEvents,
					signalsRaised,
					caseLookup,
					defaultEvents + [nextEvent],
					time)
		else:
			# Calculate signature from signals and time
			signature = str(time)

			for s in sorted(signalsRaised):
				signature += "," + s

			if signature in caseLookup:
				caseLookup[signature].probability += probability
			else:
				newCase = Case(signalsRaised, probability, time)
				caseLookup[signature] = newCase

class Case (object):
	signals = []
	probability = 0.0
	time = 0.0

	def __init__(self, ss, p, t):
		self.signals = ss
		self.probability = p
		self.time = t

	def hasAll(self, ss):
		for s in ss:
			if s not in self.signals:
				return False
		return True

class Event (object):
	outcomes = []
	triggers = []

	def __init__(self, os):
		self.outcomes = os

	def withTriggers(self, trigs):
		self.triggers = trigs
		return self

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

	def combinedWithArray(self, others):
		workingEvent = None
		for other in others:
			if workingEvent is None:
				workingEvent = self.combinedWith(other)
			else:
				workingEvent = workingEvent.combinedWith(other)
		return workingEvent

	def combinedWith(self, other):
		newOutcomes = []

		selfDefaultProbability = self.defaultProbability()
		otherDefaultProbability = other.defaultProbability()

		# Putting this here to keep the module namespace clean
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

		# Calculate the intersection of each outcome for each event,
		# including checking for a default outcome that is not an
		# explicitly listed outcome.
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

	def grouped(self, groupSize):
		# Build a collection of groups in powers of two
		binaryLookup = {}
		n = 1
		model = Event(self.outcomes)
		binaryLookup[n] = model
		while n * 2 <= groupSize:
			n *= 2
			model = model.combinedWith(model)
			binaryLookup[n] = model

		# Combine the appropriate generated groups to make one of the correct size
		# note that model is already by definition one of the groups we want
		remainder = groupSize - n
		n /= 2
		while remainder > 0:
			if remainder >= n:
				remainder -= n
				model = model.combinedWith(binaryLookup[n])
			n /= 2

		return model

	def chained(self, chainTriggeringSignal, chainLength):
		# Return an array of events that are copies of this event,
		# except that some signal of the first triggers
		# the second, and so on
		chain = []
		newOutcomes = []
		nextSignal = None
		for o in self.outcomes:

			newOutcome = Outcome(o.probability, o.signals[:])
			if chainTriggeringSignal in o.signals:
				if nextSignal is None:
					nextSignal = anonymousSignal()
				newOutcome.signals.append(nextSignal)
			newOutcomes.append(newOutcome)

		if nextSignal is None:
			nextSignal = anonymousSignal()
			newOutcome = Outcome(self.defaultProbability(), [nextSignal])
			newOutcomes.append(newOutcome)

		link = Event(newOutcomes).withTriggers(self.triggers)
		chain.append(link)

		for i in range(1, chainLength):
			newOutcomes = []
			lastSignal = nextSignal
			nextSignal = None

			for o in self.outcomes:
				newOutcome = Outcome(o.probability, o.signals[:])
				if chainTriggeringSignal in o.signals:
					if nextSignal is None:
						nextSignal = anonymousSignal()
					newOutcome.signals.append(nextSignal)
				newOutcomes.append(newOutcome)

			if nextSignal is None:
				nextSignal = anonymousSignal()
				newOutcome = Outcome(self.defaultProbability(), [nextSignal])
				newOutcomes.append(newOutcome)

			link = Event(newOutcomes).withTriggers([lastSignal])
			chain.append(link)

		return chain

class Outcome (object):
	probability = 0
	signals = []
	duration = 0.0

	def __init__(self, p, sigs):
		self.probability = p
		self.signals = sigs

	def withDuration(self, d):
		self.duration = d
		return self

