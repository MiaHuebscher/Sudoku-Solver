from functools import reduce
import random as rnd
import pickle
import copy
import time


class Environment:

    def __init__(self):
        # Dict that maps evaluation of fulfilled objectives to solutions
        self.pop = {}

        # Dict that maps each objective (name) to an evaluation function
        self.objective = {}

        # Dict that maps each agent name to a tuple of (operator, num of solutions needed to run agent)
        self.agents = {}

    def size(self):
        """Returns the number of solutions in the population"""
        return len(self.pop)

    def add_objective(self, name, f):
        """Registers an objective with the evo framework"""
        self.objective[name] = f

    def add_agent(self, name, op, k=1):
        """Registers an agent with the evo framework"""
        self.agents[name] = (op, k)

    def add_solution(self, sol):
        """Adds a solution to the population"""
        evaluation = tuple([(name, f(sol)) for name, f in self.objective.items()])
        self.pop[evaluation] = sol

    def get_random_solutions(self, k=1):
        """Pick k random solutions from the population"""
        # If the size of the population is zero, return empty list
        if self.size() == 0:
            return []
        # Else return a list of copies of the chosen solutions
        else:
            all_sols = tuple(self.pop.values())
            return [copy.deepcopy(rnd.choice(all_sols)) for _ in range(k)]

    def run_agent(self, name):
        """Invoke an agent against the population"""
        op, k = self.agents[name]
        picks = self.get_random_solutions(k)
        new_solution = op(picks)
        self.add_solution(new_solution)

    @staticmethod
    def _dominates(p, q):
        """
        Returns true if p solution dominates q solution

        :param p: evaluation of p solution ((obj1, score1), (obj2, score2), etc.))
        :param q: evaluation of q solution ((obj1, score1), (obj2, score2), etc.))
        :return:a boolean
        """
        # Obtain the scores of each objective for each solution
        pscores = [score for _, score in p]
        qscores = [score for _, score in q]

        # Calculate the score differences, and find the max and min vals
        score_diffs = list(map(lambda x, y: x-y, pscores, qscores))
        min_diff = min(score_diffs)
        max_diff = max(score_diffs)

        # If p has a greater score for every objective (or equal score for all except for one) return True
        return min_diff >= 0.0 and max_diff > 0.0

    @staticmethod
    def _reduce_nds(S, p):
        """Reduces the population to only include non-dominated solutions"""
        return S - {q for q in S if Environment._dominates(p,q)}

    def remove_dominated(self):
        """Remove dominated solutions from the population"""
        nds = reduce(self._reduce_nds, self.pop.keys(), self.pop.keys())
        self.pop = {k: self.pop[k] for k in nds}

    def evolve(self, n=1, dom=100, status=10000, sync=1000, time_lim=600.0):
        """Run n random agents against the population to get optimal solutions"""
        # Get the names of all agents and set a timer
        agent_names = list(self.agents.keys())
        start = time.time()

        # Run agents against the population for the amount of times the user desires (n)
        for i in range(n):
            # Break this loop once it exceeds the time_lim of 10 minutes
            if time.time() - start > time_lim:
                break

            pick_ag = rnd.choice(agent_names)
            self.run_agent(pick_ag)

            # Regularly remove dominated solutions and report the progress of the computing
            if i % dom == 0:
                self.remove_dominated()

            if i % status == 0:
                self.remove_dominated()
                print('Iteration: ', i)
                print('Population Size: ', self.size())
                print(self)

            if i % sync == 0:

                # Load saved solutions and merge them into our population, leaving existing solutions unchanged
                try:
                    with open('solutions.dat', 'rb') as file:
                        loaded = pickle.load(file)
                        for eval, sol in loaded.items():
                            self.pop[eval] = sol

                except Exception as e:
                    # If an exception occurs, skip it and try again later
                    print(e)

                # Remove dominated solutions before saving to disk
                self.remove_dominated()

                # Save the solutions
                with open('solutions.dat', 'wb') as file:
                    pickle.dump(self.pop, file)

        self.remove_dominated()

    def __str__(self):
        """Outputs the solution in the population"""
        # Return a print result that displays each objective score for a solution and its corresponding solution
        rslt = ""
        for eval, sol in self.pop.items():
            rslt += str(dict(eval)) + ":\t" + str(sol) + "\n"
        return rslt