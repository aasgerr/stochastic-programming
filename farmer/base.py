from pyomo.environ import ConcreteModel, Var, NonNegativeReals, SolverFactory


class farmer:

    def __init__(self, weathers="fair"):
        self.weathers = weathers

        if type(weathers) is str:
            if weathers == "good":
                predicted = 1.2
            if weathers == "fair":
                predicted = 1
            if weathers == "bad":
                predicted = 0.8

            self.crop_yield = {
                "wheat": 2.5 * predicted,
                "corn": 3 * predicted,
                "beets": 20 * predicted,
            }

        elif type(weathers) is list:

            crop_yield = {}

            for weather in self.weathers:
                if weather == "good":
                    predicted = 1.2
                if weather == "fair":
                    predicted = 1
                if weather == "bad":
                    predicted = 0.8

                crop_yield[weather] = {
                    "wheat": 2.5 * predicted,
                    "corn": 3 * predicted,
                    "beets": 20 * predicted,
                }

            self.crop_yield = crop_yield

        self.total_land = 500
        self.plant_crops = ["wheat", "corn", "beets"]
        self.planting_cost = {"wheat": 150, "corn": 230, "beets": 260}
        self.sell_crops = ["wheat", "corn", "beets_under", "beets_over"]
        self.selling_price = {
            "wheat": 170,
            "corn": 150,
            "beets_under": 36,
            "beets_over": 10,
        }
        self.purchase_crops = ["wheat", "corn"]
        self.purchasing_price = {"wheat": 238, "corn": 210}
        self.req_crops = ["wheat", "corn"]
        self.min_req = {"wheat": 200, "corn": 240}
        self.beets_quota = 6000

    def build_detmodel(self):
        m = ConcreteModel()
        m.x = Var(self.plant_crops, within=NonNegativeReals)
        m.y = Var(self.purchase_crops, within=NonNegativeReals)
        m.w = Var(self.sell_crops, within=NonNegativeReals)

        @m.Constraint()
        def total_land_constraint(m):
            return sum(m.x[crop] for crop in self.plant_crops) <= self.total_land

        @m.Constraint(self.req_crops)
        def min_requirement(m, crop):
            return (
                self.crop_yield[crop] * m.x[crop] + m.y[crop] - m.w[crop]
                >= self.min_req[crop]
            )

        @m.Constraint()
        def beet_balance(m):
            return (
                m.w["beets_under"] + m.w["beets_over"]
                <= self.crop_yield["beets"] * m.x["beets"]
            )

        @m.Constraint()
        def quota(m):
            return m.w["beets_under"] <= self.beets_quota

        @m.Objective()
        def objective(m):
            return (
                sum(self.planting_cost[crop] * m.x[crop] for crop in self.plant_crops)
                - sum(self.selling_price[crop] * m.w[crop] for crop in self.sell_crops)
                + sum(
                    self.purchasing_price[crop] * m.y[crop]
                    for crop in self.purchase_crops
                )
            )

        self.model = m

    def build_extmodel(self):
        m = ConcreteModel()
        m.x = Var(self.plant_crops, within=NonNegativeReals)
        m.y = Var(self.purchase_crops, self.weathers, within=NonNegativeReals)
        m.w = Var(self.sell_crops, self.weathers, within=NonNegativeReals)

        @m.Constraint()
        def total_land_constraint(m):
            return sum(m.x[crop] for crop in self.plant_crops) <= self.total_land

        @m.Constraint(self.req_crops, self.weathers)
        def min_requirement(m, crop, weather):
            return (
                self.crop_yield[weather][crop] * m.x[crop]
                + m.y[crop, weather]
                - m.w[crop, weather]
                >= self.min_req[crop]
            )

        @m.Constraint(self.weathers)
        def beet_balance(m, weather):
            return (
                m.w["beets_under", weather] + m.w["beets_over", weather]
                <= self.crop_yield[weather]["beets"] * m.x["beets"]
            )

        @m.Constraint(self.weathers)
        def quota(m, weather):
            return m.w["beets_under", weather] <= self.beets_quota

        @m.Objective()
        def objective(m):
            return (
                sum(self.planting_cost[crop] * m.x[crop] for crop in self.plant_crops)
                - (1 / 3)
                * sum(
                    self.selling_price[crop] * m.w[crop, weather]
                    for crop in self.sell_crops
                    for weather in self.weathers
                )
                + (1 / 3)
                * sum(
                    self.purchasing_price[crop] * m.y[crop, weather]
                    for crop in self.purchase_crops
                    for weather in self.weathers
                )
            )

        self.model = m

    def solve_model(self, solver):
        solver = SolverFactory(solver)

        self.result = solver.solve(self.model, tee=True)

    def print_detresults(self):

        print("\nLand (acres)")
        for crop in self.plant_crops:
            print(f"{crop} = {self.model.x[crop]():.2f}")

        print("\nYield (tons)")
        for crop in self.plant_crops:
            print(f"{crop} = {self.model.x[crop]()*self.crop_yield[crop]:.2f}")

        print("\nPurchase (tons)")
        for crop in self.purchase_crops:
            print(f"{crop} = {self.model.y[crop]():.2f}")

        print("\nSell (tons)")
        for crop in self.sell_crops:

            if "beet" in crop:
                print(
                    f"{crop} = {self.model.w[crop]():.2f} at ${self.selling_price[crop]}"
                )

            else:
                print(f"{crop} = {self.model.w[crop]():.2f}")

        print(f"\nProfit = ${-self.model.objective():.2f}")

    def print_extresults(self):

        print("\nLand (acres)")
        for crop in self.plant_crops:
            print(f"{crop} = {self.model.x[crop]():.2f}")

        for weather in self.weathers:

            print(f"\nWeather: {weather}")

            print("\nYield (tons)")
            for crop in self.plant_crops:
                print(
                    f"{crop} = {self.model.x[crop]()*self.crop_yield[weather][crop]:.2f}"
                )

            print("\nPurchase (tons)")
            for crop in self.purchase_crops:
                print(f"{crop} = {self.model.y[crop, weather]():.2f}")

            print("\nSell (tons)")
            for crop in self.sell_crops:

                if "beet" in crop:
                    print(
                        f"{crop} = {self.model.w[crop, weather]():.2f} at ${self.selling_price[crop]}"
                    )

                else:
                    print(f"{crop} = {self.model.w[crop, weather]():.2f}")

        print(f"\nProfit = ${-self.model.objective():.2f}")
