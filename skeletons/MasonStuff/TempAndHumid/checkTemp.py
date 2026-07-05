import json
#improve confidence if disease matches temp, lower if it doesnt
#potentially get percentage confidence from percentage close to range disease needs
#Input is a daily average of temperatures, can be expanded to day/night for more accuracy


#Input is plant and disease predicted from symptoms, and user enter average temperature of the last 24 hours
def checkTemp(plant, disease, userTemp):
    if userTemp is None:
        print("user did not enter temp")
        return

    with open("kb.json", "r", encoding="utf-8") as f:
        kb = json.load(f)
    

    diseases = kb["diseases"]

    if disease not in diseases:
        print("not in kb")
        print("Available diseases:", diseases.keys())
        return

    for entry in diseases[disease]:
        if entry["disease"] != disease:
            continue
        optimal_temps=kb["crop_profiles"][plant]["optimal_temperature"]
        compare_high=classify_temperature(userTemp-optimal_temps[1])
        compare_low=classify_temperature(userTemp-optimal_temps[0])
       
        tempRange = [compare_low,compare_high]

        kbTemp=entry.get("temperature","")

        if "None" in kbTemp:
            print("disease not affected by temperature")
            #no change in confidence
            return

        if any(t in kbTemp for t in tempRange):
            print("improve confidence")
            # improve confidence
        else:
            print("decrease confidence")
            # lower confidence

#Input is plant and disease predicted from symptoms, and average relative humidity from the last 24 hours
def checkHumid(plant, disease, userHumidity):
    if userHumidity is None:
        print("User did not enter humidity")
        return

    with open("kb.json", "r", encoding="utf-8") as f:
        kb = json.load(f)
    

    diseases = kb["diseases"]

    if disease not in diseases:
        print("not in kb")
        print("Available diseases:", diseases.keys())
        return

    for entry in diseases[disease]:
        if entry["disease"] != disease:
            continue
            
        humidRating=classify_humidity(userHumidity)
        diseaseHumidity=entry.get("humidity","")
        if "None" in diseaseHumidity:
            print("disease not affected by humidity")
            #no change confidence
            return
        
        if humidRating==diseaseHumidity:
            print("improve confidence")
            # improve confidence
        else:
            print("decrease confidence")
            # lower confidence

#Input is plant and disease predicted from symptoms, and user estimated length of plant wetness from fog, dew, rain, etc in hours
def checkLengthOfWetness(plant, disease, userLength):
    if userLength is None:
        print("User did not enter length of wetness")
        return

    with open("kb.json", "r", encoding="utf-8") as f:
        kb = json.load(f)
    

    diseases = kb["diseases"]

    if disease not in diseases:
        print("not in kb")
        print("Available diseases:", diseases.keys())
        return

    for entry in diseases[disease]:
        if entry["disease"] != disease:
            continue
        
        kbLength=entry.get("lengthOfWetness","")
        if kbLength=="None":
            print("Disease is not affected by length of wetness")
            return

        kbLength=int(kbLength)
        
        if userLength>=kbLength:
            print("improve confidence")
        else: 
            print("lower confidence")

        




def classify_temperature(temp_diff_f: float) -> str:
    match temp_diff_f:
        case x if -4 <= x <= 4:
            return "within"

        case x if -10 <= x <= -5:
            return "slightly_below"
        case x if -22 <= x <= -11:
            return "moderately_below"
        case x if x <= -23:
            return "extreme_below"

        case x if 5 <= x <= 10:
            return "slightly_above"
        case x if 11 <= x <= 22:
            return "moderately_above"
        case x if x >= 23:
            return "extreme_above"

        case _:
            raise ValueError("Unhandled temperature range")

def classify_humidity(relative_humidity: float )-> str:
    # High
    if relative_humidity >= 81:
        return "high"

    # Moderate
    if 61 <= relative_humidity <= 80:
        return "moderate"

    # Low
    if relative_humidity <= 60:
        return "low"

    # Fallback (should never hit)
    return "unknown"



if __name__=="__main__":
   checkTemp( "Maize (corn)", "Common rust",77)
   checkHumid( "Maize (corn)","Common rust", 85)
   checkLengthOfWetness("Maize (corn)","Common rust", 4)

   checkTemp( "Maize (corn)", "Common rust", None)
   checkHumid( "Maize (corn)","Common rust", None)
   checkLengthOfWetness("Maize (corn)","Common rust", None)

   checkTemp("Maize (corn)", "Northern Leaf Blight", 68)
   checkHumid( "Maize (corn)","Northern Leaf Blight", 85)
   checkLengthOfWetness("Maize (corn)","Northern Leaf Blight", 6)
