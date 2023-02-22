from mip import Model, xsum, minimize, BINARY, OptimizationStatus
from itertools import product
from sys import stdout as out

class Salesman():
    def __init__(self) -> None:
        self.model = Model('Salesman')

    def parameters(self, mtx_distance, places):
        self.distances = mtx_distance
        self.places = places
        self.V = set(range(len(self.places)))

    def variables(self):
        self.x = [[self.model.add_var(var_type=BINARY, name =f"from {j} to {i}") for j in self.places] for i in self.places]
        self.y = [self.model.add_var() for i in self.places]

    def objetive(self):
        self.model.objective = minimize(xsum(self.distances.loc[t][f] * self.x[i][j] for i, t in enumerate(self.places) for j, f in enumerate(self.places)))

    def constrains(self):
        # leave one city
        for i, place in enumerate(self.places):
            self.model += xsum(self.x[i][j] for j, place in enumerate(self.places)) == 1
            self.model += self.x[i][i] == 0

        # Arrive one city
        for j, place in enumerate(self.places):
            self.model += xsum(self.x[i][j] for i, place in enumerate(self.places)) == 1

        # subtour elimination
        n = len(self.places)
        for (i, j) in product(self.V - {0}, self.V - {0}):
            if i != j:
                self.model += self.y[i] - (n + 1) * self.x[i][j] >= self.y[j] - n

    def run_model(self):
        self.model.optimize()

        # checking if a solution was found
        if self.model.num_solutions:
            out.write('route with total distance %g found: %s'
                    % (self.model.objective_value, self.places[0]))
            nc = 0
            while True:
                nc = [i for i in self.V if self.x[nc][i].x >= 0.99][0]
                out.write(' -> %s' % self.places[nc])
                if nc == 0:
                    break
            out.write('\n')