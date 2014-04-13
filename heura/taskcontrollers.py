from heura.utils import getints
from heura.exceptions import EvaluatingException

controllers = dict()

class TaskController(object):
	pass

def registered_controller(controller):
	controllers[controller.get_name()] = controller
	return controller

@registered_controller
class LongestCycleController(TaskController):
	@staticmethod
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

	@classmethod
	def evaluate(cls, input, output):
		try:
			n, adj = cls.read_input(input)
		except:
			raise #EvaluatingException('Reading input failed')
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

	@staticmethod
	def get_name():
		return 'longest_cycle'

	@staticmethod
	def get_template():
		return 'longest_cycle.html'
