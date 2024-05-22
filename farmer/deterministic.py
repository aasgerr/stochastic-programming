from base import farmer as base

if __name__ == "__main__":
    farmer = base()
    farmer.build_detmodel()
    farmer.solve_model("gurobi")
    farmer.print_detresults()
