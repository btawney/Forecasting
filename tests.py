# tests.py

from fcst import Scenario
from fcst import Event
from fcst import Outcome

# Scenario(events)
# Event(outcomes [, triggers])
# Outcome(probability, signals)

passCount = 0
failCount = 0
verbose = False

def check(label, actual, shouldBe):
	global verbose
	global passCount
	global failCount

	if round(actual, 4) == round(shouldBe, 4):
		if verbose:
			print "    PASS " + label
		passCount += 1
	else:
		print "*** FAIL " + label
		print "    Actual:    " + str(actual)
		print "    Should Be: " + str(shouldBe)
		failCount += 1
	return None

def summary():
	global passCount
	global failCount

	print "Total Passed: " + str(passCount)
	print "Total Failed: " + str(failCount)	

def test001():
	s = Scenario([
		Event([
			Outcome(0.01, ["A"]),
			Outcome(0.99, ["~A"])
			]),
		Event([
			Outcome(0.9, ["Ws1B", "Ws2B", "Ws3B"])
			], [
			"A"
			]),

		Event([
			Outcome(0.05, ["Ws1C"]),
			Outcome(0.95, ["~Ws1C"])
			]),
		Event([
			Outcome(0.4, ["Ws1B"])
			], [
			"Ws1C",
			"~A"
			]),
		Event([
			Outcome(0.01, ["Ws1B"])
			], [
			"~Ws1C",
			"~A"
			]),

		Event([
			Outcome(0.05, ["Ws2C"]),
			Outcome(0.95, ["~Ws2C"])
			]),
		Event([
			Outcome(0.4, ["Ws2B"])
			], [
			"Ws2C",
			"~A"
			]),
		Event([
			Outcome(0.01, ["Ws2B"])
			], [
			"~Ws2C",
			"~A"
			]),

		Event([
			Outcome(0.05, ["Ws3C"]),
			Outcome(0.95, ["~Ws3C"])
			]),
		Event([
			Outcome(0.4, ["Ws3B"])
			], [
			"Ws3C",
			"~A"
			]),
		Event([
			Outcome(0.01, ["Ws3B"])
			], [
			"~Ws3C",
			"~A"
			])
		])

	check("001.1", s.probability(["A"],    ["Ws1B"]), 0.235571260306)
	check("001.2", s.probability(["Ws1C"], ["Ws1B"]), 0.530035335689)
	check("001.3", s.probability(["Ws3B"], ["Ws1B"]), 0.258121908127)
	check("001.4", s.probability(["Ws1C"], ["Ws1B", "A"]), 0.05)
	check("001.5", s.probability(["A"],    ["Ws1B", "Ws1C"]), 0.0222222222)
	check("001.6", s.probability(["Ws3B"], ["Ws1B", "Ws1C"]), 0.051066666666666)
	check("001.7", s.probability(["A"],    ["Ws1B", "Ws1C", "Ws2B", "Ws2C"]), 0.0537634408602150)
	check("001.8", s.probability(["Ws3B"], ["Ws1B", "Ws1C", "Ws2B", "Ws2C"]), 0.08167741935483870)
	check("001.9", s.probability(["A"],    ["Ws1B", "Ws1C", "Ws2B", "Ws2C", "Ws3B", "Ws3C"]), 0.1243781094527363)

def test002():
	# Odds of at least one coin coming up heads over 8 tosses
	# Modeled as an event (the coin toss) with one signal-generating outcome (heads)
	s = Scenario([
		Event([Outcome(0.5, ["Heads"])])
		])
	oddsOfNot = 0.5
	for turns in range(1, 9):
		check("002." + str(turns), s.probability(["Heads"], [], turns), 1.0 - oddsOfNot)
		oddsOfNot *= 0.5

def test003():
	# Odds of at least one coin coming up heads over 8 tosses
	# Modeled as an event (the coin toss) with two signal-generating outcomes, one of which is a default
	s = Scenario([
		Event([Outcome(0.5, ["Heads"]), Outcome(0.5, "~Heads")])
		])
	oddsOfNot = 0.5
	for turns in range(1, 9):
		check("003." + str(turns), s.probability(["Heads"], [], turns), 1.0 - oddsOfNot)
		oddsOfNot *= 0.5


def test004():
	# A group event modeling the tossing of 11 coins
	s = Scenario([
		Event([Outcome(0.5, ["Heads"])]).Grouped(11)
		])

	def factorial(x):
		if x > 1:
			return x * factorial(x - 1)
		else:
			return 1

	for coins in range(1, 12):
		odds = factorial(11) / factorial(coins) / factorial(11 - coins) / pow(2, 11)
		check("004." + str(coins), s.probability("Heads*" + str(coins)), odds)


test001()
test002()
test003()
test004()

summary()
