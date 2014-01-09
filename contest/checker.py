class EvaluatingException(Exception):
	def __init__(self, text='general'):
		super().__init__()
		self.text = text

	def __unicode__(self):
		return 'Evaulation exception ({})'.format(self.text)

	def __str__(self):
		return self.__unicode__()


def getints(line):
	return map(int, line.split())
	
input = """5 5
1 2
2 3
3 4
4 1
1 5
"""

output = """4
1 2 3 4
"""

output = """0"""

output = """3
1 2 3
"""

def read_input(input):
	inp = input.split('\n')
	if inp[-1]=='':
		inp = inp[:-1]

	n, m = getints(inp[0])

	lines = inp[1:]
	adj = [ [] for _ in range(n+1) ]

	for l in lines:
		a, b = getints(l)
		adj[a].append(b), adj[b].append(a)

	return (n, adj)

def longest_cycle_evaluate(input, output):
	try:
		n, adj = read_input(input)
	except:
		raise EvaluatingException('Reading input failed')
	try:
		out = list(map(int, output.split()))

		if len(out) == 0 or len(out) != out[0]+1 or out[0]==1 or out[0]==2:
			raise EvaluatingException('Wrong output size!')

		l = out[0]
		cycle = out[1:]

		if l == 0: return 0

		visited = [ False for _ in range(n+1) ]

		x = cycle[-1]
		if not (1 <= x <= n):
			return EvaluatingException('Out of range')
		for y in cycle:
			if y not in adj[x] or visited[y]:
				raise EvaluatingException('Not a cycle')
			visited[y] = True
			x = y

		# Everything OK
		from math import log
		return log(l + 2) 
	except EvaluatingException as e:
		raise e
	except:
		raise EvaluatingException()

#print(longest_cycle_evaluate(input, output))

__all__ = [ EvaluatingException, longest_cycle_evaluate ]

