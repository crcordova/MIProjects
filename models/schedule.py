from mip import Model, xsum, minimize, BINARY, OptimizationStatus, CONTINUOUS
from pandas import DataFrame

class Scheduler():
    def __init__(self) -> None:
        self.model = Model('schedule')

    def add_sets(self, weeks: list, periods: list):
        self.days = range(7)
        self.weeks = weeks
        self.periods = periods

    def parameters(self, collaborators, demand, availability):
        self.collaborators = collaborators
        self.collaborators_range = range(len(collaborators))
        self.demand = demand
        self.availability = availability
        self.cu = 20
        self.co = 10
        self.max_days_work = 5

    def variables(self):
        self.x = [[[[self.model.add_var(var_type=BINARY, name=f"week:{w}, day:{d}, period:{p}, collab{c}") for p in self.periods] for d in self.days] for w in self.weeks] for c in self.collaborators]

        self.y_over = [[[self.model.add_var(var_type = CONTINUOUS, name = f'y_over_{p}_{d}_{w}') for p in self.periods] for d in self.days] for w in self.weeks]
        self.y_under = [[[self.model.add_var(var_type = CONTINUOUS, name = f'y_under_{w}_{d}_{p}') for p in self.periods] for d in self.days] for w in self.weeks]

    def constrains(self):


        for p in self.periods:
            for d in self.days:
                for w, week in enumerate(self.weeks):
                    # self.model += xsum(self.x[p][d][w][c] for c in self.collaborators) >= self.demand # cubrir demanda

                    self.model += self.y_under[w][d][p] >= self.demand[week][d][p] - xsum(self.x[c][w][d][p] for c in self.collaborators_range), f'definicion_y_under'
                    self.model += self.y_over[w][d][p] >= xsum(self.x[c][w][d][p]  for c in self.collaborators_range) - self.demand[week][d][p], f'definicion_y_over'

        for d in self.days:
            for w, week in enumerate(self.weeks):
                for c in self.collaborators_range:
                    self.model += xsum(self.x[c][w][d][p] for p in self.periods) <= 1 # no puede trabajar dos periodes del mismo día
        
        # Collabr cannot work 5 days into a week
        for c in self.collaborators_range:
            for w, wk in enumerate(self.weeks):
                self.model += xsum(self.x[c][w][d][p] for p in self.periods for d in self.days) <= self.max_days_work

        # collab cannot work two perdios into one day
        for c in self.collaborators_range:
            for w, wk in enumerate(self.weeks):
                for d in self.days:
                    self.model += xsum(self.x[c][w][d][p] for p in self.periods) <= 1

        for c, collab in enumerate(self.collaborators):
            for w, wk in enumerate(self.weeks):
                for d in self.days:
                    for p in self.periods:
                        self.model += self.x[c][w][d][p] <= self.availability[collab][p]

        # por lo menos cubrir la mitad
        for w, wk in enumerate(self.weeks):
            for d in self.days:
                for p in self.periods:
                    self.model += xsum(self.x[c][w][d][p] for c in self.collaborators_range) >= self.demand[wk][d][p]/2 

    def objetive(self):
        self.model.objective = minimize(
            xsum(self.cu*self.y_under[w][d][p] for p in self.periods for d in self.days for w in range(len(self.weeks))) + 
            xsum(self.co*self.y_over[w][d][p] for p in self.periods for d in self.days for w in range(len(self.weeks)))
            )

    def run_model(self):
        status = self.model.optimize()

        print("#############################################")
        if status == OptimizationStatus.OPTIMAL:
            print('[OPTIMAL] optimal solution profit {} found'.format(self.model.objective_value))
        elif status == OptimizationStatus.FEASIBLE:
            print('[FEASIBLE]  sol.profit {} found, best possible: {}'.format(self.model.objective_value, self.model.objective_bound))
        elif status == OptimizationStatus.NO_SOLUTION_FOUND:
            print('[Not Found] no feasible solution found, lower bound is: {}'.format(self.model.objective_bound))

    def print_result(self):
        df_result = DataFrame(columns=['Person','week','day','period'])
        for c, collab in enumerate(self.collaborators):
            for w, wk in enumerate(self.weeks):
                for d in self.days:
                    for p in self.periods:
                        if self.x[c][w][d][p].x >= 0.99:
                            print(f'Collaborador {collab} week:{wk}, day:{d}, periodo:{p}')
                            df_result.loc[len(df_result)] = [collab, wk, d, p]

        return df_result.set_index(['Person','week'])
                            