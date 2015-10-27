import csv
import operator
import random as rand
import math

player_pool = {}
dk_roster =\
(
  'QB',
  'RB',
  'RB',
  'WR',
  'WR',
  'WR',
  'TE',
  'FLEX',
  'DST',
)

fd_roster =\
(
  'QB',
  'RB',
  'RB',
  'WR',
  'WR',
  'WR',
  'TE',
  'K',
  'DST',
)

dk_salary_cap = 50000
fd_salary_cap = 60000

rank_factor = 0.5
max_acceptance_rate = 0.5
min_acceptance_rate = 0.1
num_generations = 100
population_size = 1000

salary_cap = dk_salary_cap
roster_slots = dk_roster

with open('DKSalaries.csv') as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    pos = row['Position']
    if pos not in player_pool:
      player_pool[pos] = []
    player_pool[pos].append( (row['Position'], row['Name'], int(row['Salary']), float(row['AvgPointsPerGame'])) )

for pos in player_pool:
  player_pool[pos] = sorted(player_pool[pos], key=operator.itemgetter(3))

def populate_roster(population, rank=0.5):
  roster = {}
  for pos in roster_slots:
    if pos not in roster:
      roster[pos] = []
    if pos == 'FLEX':
      local_pool = population['WR']+population['RB']+population['TE']
      size = len(local_pool)
      roster[pos].append(rand.choice(local_pool[:int(rank*size)]))
    else:
      size = len(population[pos])
      roster[pos].append(rand.choice(population[pos][:int(rank*size)]))
  return (roster, get_roster_salary(roster), get_roster_ffpoints(roster))

def reproduce(roster1, roster2, fn, pool, rank=0.5, mutation_factor=0.1):
  roster = {pos: [] for pos in roster_slots}
  r1 = roster1[0]
  r2 = roster2[0]
  for pos in r1:
    for player_idx in range(len(r1[pos])):
      # crossover genes (players)
      recombinant = fn(r1[pos][player_idx],r2[pos][player_idx])

      mutation_flag = False
      if recombinant in roster[pos]:
        mutation_flag = True

      if "FLEX" in roster:
        if recombinant in roster[pos]+roster['FLEX'] or (pos == 'FLEX' and recombinant in roster['WR']+roster['RB']+roster['TE']):
          mutation_flag = True

      # mutation
      if rand.random() < mutation_factor or mutation_flag:
        size = len(pool)
        flag = False
        while not flag:
          recombinant = rand.choice(pool)[0][pos][0]
          if "FLEX" in roster:
            flag = False if recombinant in roster[pos]+roster['FLEX'] or (pos == 'FLEX' and recombinant in roster['WR']+roster['RB']+roster['TE']) else True
          else:
            flag = False if recombinant in roster[pos] else True
      roster[pos].append(recombinant)

  return (roster, get_roster_salary(roster), get_roster_ffpoints(roster))

def compare_player(player1, player2):
  if player1[3] > player2[3]:
    return player1
  else:
    return player2

def generate_population(pool, n, seed=1.0):
  population = []
  local_pool = {pos: sorted(pool[pos],key=operator.itemgetter(3), reverse=True) for pos in pool}
  for i in xrange(n):
    population.append(populate_roster(local_pool, seed))
  return population

def selection(pool, acceptance_rate=max_acceptance_rate):
  acceptable = []

  # remove solutions breaking the constraint (salary cap)
  acceptable = filter(is_acceptable, pool)

  # only return the most fit (highest ffpoint value)
  return sorted(acceptable, key=operator.itemgetter(2), reverse=True)[:int(math.ceil(len(pool)*acceptance_rate))]

def evolution(pool, initial_n=100, generations=100, rank_factor=0.5, initial_acceptance_rate=0.5,final_acceptance_rate=0.1, converge=True):
  initial_population = generate_population(pool, initial_n, rank_factor)
  population = initial_population
  acceptance_rate = initial_acceptance_rate
  for generation in xrange(generations):
    mating_set = set()
    children = []
    for index in xrange(len(population) / 2):
      found_mates = False
      while not found_mates:
        p1_id = rand.randrange(0, len(population))
        p2_id = rand.randrange(0, len(population))
        if p1_id != p2_id and\
           (p1_id, p2_id) not in mating_set and\
           (p2_id, p1_id) not in mating_set:
           found_mates = True
      mating_set.add((p1_id, p2_id))
      children.append(reproduce(population[p1_id], population[p2_id],compare_player,initial_population))
    population.extend(children)
    population = selection(population,acceptance_rate)
    if converge:
      acceptance_rate = (population[0][2] - population[-1][2]) / 100
      if acceptance_rate < final_acceptance_rate:
        acceptance_rate = final_acceptance_rate
      elif acceptance_rate > initial_acceptance_rate:
        acceptance_rate = initial_acceptance_rate
  return population

def is_acceptable(roster):
  return roster[1] <= salary_cap    

def get_max_ffpoint_roster(pool):
  roster = {}
  local_pool = {pos: sorted(pool[pos],key=operator.itemgetter(3)) for pos in pool}
  for pos in roster_slots:
    if pos not in roster:
      roster[pos] = []
    if pos == 'FLEX':
      chosen = reduce(lambda a,b: a if a > b else b, local_pool['WR']+local_pool['RB']+local_pool['TE'])
      roster[pos].append(local_pool[chosen[0]].pop())
    else:
      roster[pos].append(local_pool[pos].pop())
  return roster

def get_roster_ffpoints(roster):
  return sum([player[3] for pos in roster for player in roster[pos]])

def get_roster_salary(roster):
  return sum([player[2] for pos in roster for player in roster[pos]])

chosen = []
for i in range(5):
  temp = reduce(lambda a,b: a if a[2] > b[2] else b, [evolution(player_pool,10000,100,1.0,converge=False)[0] for i in range(10)])
  for pos in temp[0]:
    for player in temp[0][pos]:
      for pos2 in player_pool:
        if player in player_pool[pos2]:
          player_pool[pos2].remove(player)
  chosen.append(temp)

chosen = sorted(chosen, key=operator.itemgetter(2), reverse=True)
print chosen
