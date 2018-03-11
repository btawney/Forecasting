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
			Outcome(0.01, ["ServerOverheats"]),
			Outcome(0.99, ["~ServerOverheats"])
			]),
		Event([
			Outcome(0.9, ["Ws1KE33", "Ws2KE33", "Ws3KE33"])
			], [
			"ServerOverheats"
			]),

		Event([
			Outcome(0.05, ["Ws1Venus"]),
			Outcome(0.95, ["~Ws1Venus"])
			]),
		Event([
			Outcome(0.4, ["Ws1KE33"])
			], [
			"Ws1Venus",
			"~ServerOverheats"
			]),
		Event([
			Outcome(0.01, ["Ws1KE33"])
			], [
			"~Ws1Venus",
			"~ServerOverheats"
			]),

		Event([
			Outcome(0.05, ["Ws2Venus"]),
			Outcome(0.95, ["~Ws2Venus"])
			]),
		Event([
			Outcome(0.4, ["Ws2KE33"])
			], [
			"Ws2Venus",
			"~ServerOverheats"
			]),
		Event([
			Outcome(0.01, ["Ws2KE33"])
			], [
			"~Ws2Venus",
			"~ServerOverheats"
			]),

		Event([
			Outcome(0.05, ["Ws3Venus"]),
			Outcome(0.95, ["~Ws3Venus"])
			]),
		Event([
			Outcome(0.4, ["Ws3KE33"])
			], [
			"Ws3Venus",
			"~ServerOverheats"
			]),
		Event([
			Outcome(0.01, ["Ws3KE33"])
			], [
			"~Ws3Venus",
			"~ServerOverheats"
			])
		])

	check("001.1", s.probability(["ServerOverheats"], ["Ws1KE33"]), 0.235571260306)
	check("001.2", s.probability(["Ws1Venus"],        ["Ws1KE33"]), 0.530035335689)
	check("001.3", s.probability(["Ws3KE33"],         ["Ws1KE33"]), 0.258121908127)
	check("001.4", s.probability(["Ws1Venus"],        ["Ws1KE33", "ServerOverheats"]), 0.05)
	check("001.5", s.probability(["ServerOverheats"], ["Ws1KE33", "Ws1Venus"]), 0.0222222222)
	check("001.6", s.probability(["Ws3KE33"],         ["Ws1KE33", "Ws1Venus"]), 0.051066666666666)
	check("001.7", s.probability(["ServerOverheats"], ["Ws1KE33", "Ws1Venus", "Ws2KE33", "Ws2Venus"]), 0.0537634408602150)
	check("001.8", s.probability(["Ws3KE33"],         ["Ws1KE33", "Ws1Venus", "Ws2KE33", "Ws2Venus"]), 0.08167741935483870)
	check("001.9", s.probability(["ServerOverheats"], ["Ws1KE33", "Ws1Venus", "Ws2KE33", "Ws2Venus", "Ws3KE33", "Ws3Venus"]), 0.1243781094527363)


test001()
