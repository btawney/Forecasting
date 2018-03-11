# tests.py

from fcst import Scenario
from fcst import Event
from fcst import Outcome

# Scenario(events)
# Event(outcomes [, triggers])
# Outcome(probability, signals)

def check(label, actual, shouldBe):
	if round(actual, 4) == round(shouldBe, 4):
		print "    PASS " + label
	else:
		print "*** FAIL " + label
		print actual
		print shouldBe
	return None

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

test001()
