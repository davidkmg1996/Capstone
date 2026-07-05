import json


def updateKB():
    with open("KB.json", "r", encoding="utf-8") as f:
        kb = json.load(f)

    with open("ScrapeOutput.json", "r", encoding="utf-8") as f:
        scrape = json.load(f)
    count=0
    for symptom_name in kb["symptoms"].keys():


        for item in scrape:

            if symptom_name.lower() in item["symptoms"].lower():
                count+=1
                entry = {"plant": item.get("plant",""),
                    "disease": item.get("disease",""),
                    "symptom": symptom_name,
                    "condition": setCategory(item.get("condition","")),
                    "type": setType(item.get("type","")),
                    "comments": item.get("comments",""),
                    "management": item.get("management","")
                }
                kb["symptoms"][symptom_name].append(entry)
    print("New Entries: ",count)
    with open("KB.json", "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2)

    
def setCategory(option):
    match option:
        case "Category : Mites":
            return "pest attack"
        case "Category : Viral":
            return "disease"
        case "Category : Fungal, Oomycete":
            return "disease"
        case "Category : Bacterial, Fungal":
            return "disease"
        case "Category : Others":
            return "disease"
        case "Category : Insects":
            return "pest attack"
        case "Category : Bacterial":
            return "disease"
        case "Category : Nematodes":
            return "pest attack"
        case "Category : Fungal":
            return  "disease"
        case "Category : Oomycete":
            return "disease"
        case "": 
            return "Unknown"
        case _:
            return "Unknown"

def setType(raw: str) -> str:
    text = raw.lower().strip()

    # BACTERIAL
    bacterial_keywords = [
        "bacteria", "bacterium", "bacterial", "mycoplasma",
        "mycoplasma-like", "phytoplasma"
    ]

    # FUNGAL
    fungal_keywords = [
        "fungus", "fungi", "fungal", "fugnus", "oomycete",
        "alga", "algae", "viroid", "virus", "viruses"
    ]

    # ENVIRONMENTAL / PHYSIOLOGICAL / ANIMALS / NOT PATHOGENS
    environmental_keywords = [
        "physiological", "stress", "nutritional", "disorder",
        "insect", "insects", "mite", "mites", "arachnid",
        "rodents", "mollusc", "weed", "thrips",
        "nematode", "nematodes",
        "low calcium", "excess nitrogen", "unknown"
    ]

    # Normalize categories using substring matching
    if any(k in text for k in bacterial_keywords):
        return "bacterial"
    elif any(k in text for k in fungal_keywords):
        return "fungal"
    elif any(k in text for k in environmental_keywords):
        return "environmental"

    return "unkown"  # fallback

if __name__=="__main__":
   updateKB()