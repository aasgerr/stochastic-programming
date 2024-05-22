from base import farmer as base

if __name__ == "__main__":
    weathers = ["good", "fair", "bad"]
    for weather in weathers:
        farmer = base(weather)
        farmer.build_detmodel()
        farmer.solve_model("gurobi")
        print(f"\nWeather: {weather}")
        farmer.print_detresults()
