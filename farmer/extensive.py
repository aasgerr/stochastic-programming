from base import farmer

if __name__ == "__main__":
    farmer = farmer(["good", "fair", "bad"])
    farmer.build_extmodel()
    farmer.solve_model("gurobi")
    farmer.print_extresults()
