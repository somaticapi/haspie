import argparse
import subprocess
import re
import sys
import os
sys.path.append('./out_module') 
import Out


class Chord:
	"""Class that stores information about a chord in the score"""
	def __init__(self, time, name):
		self.name = name
		self.time = time

	def __str__(self):
		return self.name + ", " + str(self.time)

class Error:
	"""Class that stores information about an error in the score"""
	def __init__(self, voice, grade, time):
		self.voice = voice
		self.grade = grade
		self.time = time

	def __str__(self):
		return "Voice: " + str(self.voice) + ", Grade: " + str(self.grade) + ", " + str(self.time)

class HaspSolution:
	"""Class that stores information of a single solution of the harmony
	deducing module"""
	def __init__(self, chords, notes, errors, num_error, num_unison):
		self.chords = chords
		self.errors = errors
		self.notes = notes
		self.num_error = num_error
		self.num_unison = num_unison

	def __str__(self):
		ret = "Chords: "
		for ch in self.chords:
			ret += str(ch) + " // "
		ret += "\n"
		if len(self.errors) > 0:
			ret += "Errors: "
			for er in self.errors:
				ret += str(er) + " // "
			ret += "\n["
		ret += str(self.notes) + "\n"
		ret += "Errors: " + str(self.num_error) + " // Unisons: " + str(self.num_unison)
		return ret

class ClaspResult:
	"""Class that parses and stores output of a clasp execution
	It's created with the textual output of clasp and then stores
	satisfability, optimization status and all of it's solutions
	with its optimization values"""
	def __init__(self, asp_out):
		self.raw_output = asp_out
		self.optimum = self.parse_optimum()
		sols = self.parse_solutions()
		self.min_error = sols[1]
		self.min_unison = sols[2]
		self.solutions = []
		raw_sols = sols[0]
		for sol in raw_sols:
			#Check min_unisons, not working properly
			if (sol.num_error == self.min_error):
				self.solutions += [sol]

	def parse_solutions(self):
		out = self.raw_output
		answers = re.split('Answer:\s*[0-9]+', out)
		min_er = sys.maxint
		min_un = sys.maxint
		solutions = []
		for ans in answers:
			if len(ans) > 0:
				notes = re.findall('out_note\(([0-9]+),([0-9]+),([0-9]+)\)', ans)
				chords = [Chord(int(ch[0]),ch[1]) for ch in re.findall('chord\(([0-9]+),([ivxmo]+)\)', ans)]
				errors = [Error(int(er[0]),int(er[1]),int(er[2])) for er in re.findall('error\(([0-9]+),([0-9]+),([0-9]+)\)', ans)]
				optimums = re.search('Optimization:\s*([0-9]+)\s*([0-9]+)', ans)
				if optimums == None:
					optimums = re.search('Optimization:\s*([0-9]+)', ans)
					n_er = int(optimums.group(1))
					n_un = 0
				else:
					n_er = int(optimums.group(1))
					n_un = int(optimums.group(2))

				if (n_er < min_er):
					min_er = n_er
				if (n_un < min_un):
					min_un = n_un
				solutions += [HaspSolution(chords,notes,errors,n_er,n_un)]
		return (solutions, min_er, min_un)

	def parse_optimum(self):
		out = self.raw_output
		m = re.search('OPTIMUM FOUND', out)
		if m != None:
			return True
		else:
			return False

	def __str__(self):
		ret = ""
		for sol in self.solutions:
			ret += str(sol) + "\n\n"
		if self.optimum == True:
			ret += "Optimum found, optimal solution(s) have " + str(self.min_error) + " errors and " + str(self.min_unison) + " unisons."
		return ret

		
def main():
	parser = argparse.ArgumentParser(description='Harmonizing music with ASP')
	parser.add_argument('xml_score', metavar='XML_SCORE',
	                   help='input musicXML score for armonizing')
	parser.add_argument('-n', '--num_sols', metavar='N', nargs=1, default=0, type=int,
	                   help='max number of ASP solutions, by default all of them')
	parser.add_argument('-s', '--span', metavar='S', nargs=1, default=1, type=int,
	                   help='horizontal span to consider while harmonizing, by default 1')
	parser.add_argument('-d', '--divide', metavar='32|16|8|4|2|1', nargs=1, default=0, type=int,
	                   help='forces subdivision of the notes in the score to a specific value, by default it\'s automatically calculated')
	parser.add_argument('-m', '--mode', metavar='major|minor', nargs=1, default="major", choices=['major', 'minor'],
	                   help='mode of the scale, major by default')
	parser.add_argument('-v', '--voices', metavar='V', nargs=1, default="0", type=int,
	                   help='number of extra voices that should be added to the score for harmonization')

	args = parser.parse_args()

	infile = args.xml_score

	n = args.num_sols
	if args.num_sols != 0:
		n = args.num_sols[0]

	opt_all = ""
	if n == 0:
		pass
		#opt_all = "--opt-all"

	mode = args.mode
	if args.mode != "major":
		mode = args.mode[0]

	sub = args.divide
	if args.divide != 0:
		sub = args.divide[0]

	span = args.span
	if args.span != 1:
		span = args.span[0]

	voices = args.voices
	if args.voices != 0:
		voices = args.voices[0]

	asp_outfile_name = re.search('/(.*?)\.xml', infile)
	outname = asp_outfile_name.group(1)
	lp_outname = outname + ".lp"
	xml_parser_args = ("parser/mxml_asp", infile, "-o", "asp/generated_logic_music/" + lp_outname, "-s", str(sub))
	xml_parser_ret = subprocess.call(xml_parser_args)
	
	if xml_parser_ret != 0:
		sys.exit("Parsing error, stopping execution.")

	asp_args = ("clingo", "asp/assign_chords.lp", "asp/include/" + mode + "_mode.lp", "asp/include/" + mode + "_chords.lp",
		"asp/include/conversions.lp", "asp/generated_logic_music/" + lp_outname, "-n", str(n), "--const", "span=" + str(span), 
		"--const", "extra_voices="+ str(voices), opt_all)

	asp_proc = subprocess.Popen(asp_args, stdout=subprocess.PIPE)
	asp_out = asp_proc.stdout.read()

	res = ClaspResult(asp_out)
	print res

if __name__ == "__main__":
    main()