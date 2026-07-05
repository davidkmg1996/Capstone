from ESTest import PlantDiagnosis, MultiSymptom, load_json, Observation, symptomatic



def main():
    kb = load_json("KB.json")
    # engine = PlantDiagnosis(kb)
    engine2 = MultiSymptom(kb)

    engine2.reset()
    engine2.declare(symptomatic(name="Tomato", symptoms = ["deformed", "discolored"]))
    engine2.run()
if __name__ == "__main__":
    main()