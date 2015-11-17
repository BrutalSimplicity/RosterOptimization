import random
import operator
from deap import base, creator, tools, gp

# + maximizes
# - minimizes
creator.create('FitnessMax', base.Fitness, weights=(1.0,))
creator.create('Individual', list, fitness=creator.FitnessMax)

IND_SIZE = 20

# create individuals based on weights
toolbox = base.Toolbox()
toolbox.register('attr_float', random.random)
toolbox.register('individual', tools.initRepeat, creator.Individual,
	toolbox.attr_float, n=IND_SIZE)

# create based on permutations
toolbox.register('indices', random.sample, range(IND_SIZE), IND_SIZE)
toolbox.register('individual', tools.initIterate, creator.Individual,
	toolbox.indices)

pset = gp.PrimitiveSet('MAIN', arity=1)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
creator.create('Individual', gp.PrimitiveTree, fitness=creator.FitnessMax,
	pset=pset)

toolbox.register('expr', gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
toolbox.register('individual', tools.initIterate, creator.Individual,
	toolbox.expr)

