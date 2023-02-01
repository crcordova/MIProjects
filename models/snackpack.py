from mip import Model, xsum, maximize, BINARY, OptimizationStatus
import pandas as pd

# DATA
# df_products = pd.read_csv("data\Productos.csv")
# Items = df_products['Item'].tolist()
# weight = df_products['Peso'].tolist()
# utility = df_products['Utilidad'].tolist()
# volumne = df_products['Peso'].tolist()

class Snackpack:
    def __init__(self):
        self.model = Model("knapsack")

    def parameters(self, df, volumne, weight):
        self.items = df['Item'].tolist()
        self.weights = df['Peso'].tolist()
        self.profits = df['Utilidad'].tolist()
        self.volumnes = df['Peso'].tolist()
        self.volumne_max = volumne
        self.weight_max = weight

    def variables(self):
        self.x = [self.model.add_var(var_type=BINARY, name=f"naem:{item} cod: {i}") for i, item in enumerate(self.items)]

    # add FO
    def objetive(self):
        self.model.objective = maximize(xsum(self.profits[i] * self.x[i] for i in range(len(self.items))))

    #Constrains
    def constrains(self):
        self.model += xsum(self.weights[i] * self.x[i] for i in range(len(self.items))) <= self.weight_max
        self.model += xsum(self.volumnes[i] * self.x[i] for i in range(len(self.items))) <= self.volumne_max


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

        selected = [f"{name}" for i, name in enumerate(self.items) if self.x[i].x >= 0.99]
        print("selected items: {}".format(selected))
        return selected