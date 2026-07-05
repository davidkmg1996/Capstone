import React, { useRef, useState } from "react";
import {Pressable, useWindowDimensions, ImageBackground, StyleSheet, Button, View, Text, Image, TouchableOpacity, ScrollView, TextInput } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { MultipleSelectList, SelectList } from "react-native-dropdown-select-list";
import {Link, usePathname, Stack, useRouter} from "expo-router";
import {BlurView} from "expo-blur";
import {LinearGradient} from "expo-linear-gradient"
import {useEffect} from "react";
import kb from "./kb.json";
import Webcam from "react-webcam";
import { UserProvider } from "./UserContext";
import { requestMediaLibraryPermissionsAsync, launchImageLibraryAsync, MediaType } from 'expo-image-picker';
import { responsiveHeight, responsiveWidth, responsiveFontSize } from "react-native-responsive-dimensions";
import FontAwesome6 from '@expo/vector-icons/FontAwesome6';
import SymptomImage from "./SymptomImage";
import Header from "./Header";

// const {width, height} = Dimensions.get("window");
// const baseWidth = 375;
// const baseHeight = 812;

export default function useSymptoms({children}) {
  const [selected, setSelected] = useState("");
  const [input, setInput] = useState({ plant: "", symptoms: [], zipcode: null});
  const [showError, setShowError] = useState(false);
  const [result, setResult] = useState(null);
  const [imageResult, setImageResult] = useState(null);
  const formData = useRef(new FormData());
  const [showCamera, setShowCamera] = useState(false);
  const [images, setImages] = useState([]);
  const [hovered, setHovered] = useState(false);
  const [hoveredB, setHoveredB] = useState(false);
  const [hoveredC, setHoveredC] = useState(false);
  const router = useRouter();
  const [value, setValue] = useState("");
  const [showTooltip, setShowTooltip] = useState(false);
  const { width, height } = useWindowDimensions();
  const [symptomImagesUri, setSymptomImagesUri] = useState([]);
  const scrollViewRef = useRef(null);


  useEffect(() => {
    document.title = "Plant Diagnosis"

  }, [])

 
/*  const symptoms = kb.symptoms;
  const data = [];

  for (const [k, v] of Object.entries(symptoms)) {
    for (const plant of v) {
      if (!Object.hasOwn(plant, "plant")) continue;
      const element = data.find((e) => e["key"] === plant["plant"]);
      if (element !== undefined) {
        if (!element["value"].includes(k)) element["value"].push(k);
      } else data.push({ key: plant["plant"], value: [k] });
    }
  }
*/
const symptoms = kb.diseases; // your JSON parsed and accessed at .diseases
const data = [];

for (const [diseaseName, plantEntries] of Object.entries(diseases)) {
  for (const entry of plantEntries) {
    if (!Object.hasOwn(entry, "plant")) continue;
    const element = data.find((e) => e["key"] === entry["plant"]);
    if (element !== undefined) {
      entry.symptom.forEach((s) => {
        if (!element["value"].includes(s)) element["value"].push(s);
      });
    } else {
      data.push({ key: entry["plant"], value: [...entry.symptom] });
    }
  }
}
  data.sort((a, b) => sortKeys(a["key"], b["key"]));
  data.forEach((e) => e["value"].sort());


  async function handleDiagnose()
  {
      const plantEntry = data.find((e) => e.key === input.plant);

      if (!plantEntry || input.symptoms.some((s) => !plantEntry.value.includes(s))) {
        setShowError(true);
        return;
      }

      try {
        const response = await fetch(
          // "https://plantdisease-932821527783.europe-west1.run.app/api/diagnose",
          "http://localhost:5000/api/diagnose",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(input),
          }
        );

        const dataResp = await response.json();

        if (!response.ok) {
          setResult("Error: " + (dataResp.error || response.statusText));
        } else {
          setResult(JSON.stringify(dataResp, null, 2));
        }
      } catch (err) {
        setResult("Network error: " + err.message);
      }
  }

  async function pickImage()
  {
    await requestMediaLibraryPermissionsAsync();
    const symptomImages = await launchImageLibraryAsync({
      mediaTypes: "images",
      allowsMultipleSelection: true,
      quality: 1,
    });

    if(!symptomImages.canceled)
      setSymptomImagesUri(symptomImages.assets);
  }

  return (
    
    <>
    {/* <SafeAreaView style = {styles.safeArea}>
         <ImageBackground
  source={require("../assets/images/bgplant.jpg")}
  resizeMode="cover"
  style={{width: "100%", aspectRatio: 16/9}}
> */}
     {/* <LinearGradient
        colors={[
  "rgba(71,196,80,0.5)",
  "rgba(191,198,195,0.5)"
]}
   start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={{ flex: 1 }}
      > */}

    
  {/* <ScrollView
    contentContainerStyle={{
      paddingBottom: 0,
      alignItems: "center", #2b2b2b #535353 #dddddd
    }}
  > */}

    {/* <NavBar /> */}
    <Stack.Screen options={{headerShown: false}} />

    
    <View style={{width, height, backgroundColor: "#2b2b2b"}}>
      <Header />
        <View style={{flexDirection: "column", width: width * .28, backgroundColor: "#535353", alignSelf: "center", padding: 50, gap: 15, borderRadius: 4, marginTop: 70}}>

          {/* First Row */}
          <View style={{ flexDirection: "row", left: 50, right: 50, gap: 10, position: "absolute", zIndex: 20}}>
            <View style={{flex: 1}}>
              <SelectList
                setSelected={(val) => setInput({ ...input, plant: val })}
                data={data.map((e) => ({ key: e.key, value: e.key }))}
                save="value"
                placeholder="Plant"
                searchPlaceholder="Type to Search"
                inputStyles={{outlineStyle: "none", textAlign: "center" }}
                responsiveHeight
                boxStyles={{backgroundColor: "#dddddd", color: "white"}}
                dropdownStyles={{backgroundColor: "#dddddd"}}
              />
            </View>


            <View style={{flexDirection: "row", position: "relative"}}>
              <TextInput
                style={styles.zipcode}
                onChangeText={(text) => setInput({...input, zipcode: text})}
                value={input.zipcode}
                placeholder="ZIP Code"
              />
              <View
                style={{position: "absolute",
                    top: 0,
                    left: 170}}
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
              >
                <FontAwesome6 name="circle-question" size={18} color="#dddddd"/>
                {
                  showTooltip &&
                  <View style={{
                    position: "absolute",
                    top: 10,
                    left: 10,
                    borderRadius: 5,
                    width: 155,
                    backgroundColor: "#dddddd"
                    }}>
                      <Text>The ZIP code will be used to find weather data around the given ZIP code area.</Text>
                  </View> 
                }
              </View>
            </View>
          </View>

          <View style={{position: "absolute", left: 50, right: 50, zIndex: 10}}>
            <MultipleSelectList
                setSelected={(val) => setSelected(val)}
                data={input.plant ? getPlantSymptoms(data, input.plant) : []}
                onSelect={() => {
                  if (showError) setShowError(false);
                  setInput({ ...input, symptoms: selected });
                }}
                boxStyles={{
                  marginTop: 60,
                  backgroundColor: "#dddddd",
                  pointerEvents: input.plant === "" ? "none" : "auto",
                  opacity: input.plant === "" ? 0.4 : 1,
                }}
                dropdownStyles={{backgroundColor: "#dddddd"}}
                inputStyles={{outlineStyle: "none"}}
                save="value"
                placeholder="Symptoms"
                searchPlaceholder="Type to Search"
                label="Symptoms"
                maxHeight={200}
            />
          </View>
            
            <View style={{flexDirection: "row", alignItems: "center", gap: 10, marginTop: 160}}>
              <Text style={{fontSize: 18, fontWeight: "bold", color: "#000000"}}>Upload Images of Symptoms</Text>
              <Pressable onPress={() => pickImage()}>
                <View style={{backgroundColor: "#dddddd", padding: 4, borderRadius: 10, width: 50}}><FontAwesome6 name="image" size={24} color="black" style={{alignSelf: "center"}}/></View>
              </Pressable>
            </View>
            
              <ScrollView style={{height: 250}} ref={scrollViewRef} onContentSizeChange={() => scrollViewRef.current.scrollToEnd({ animated: true })}>
                <View style={{flexDirection: "row", width: "100%", minHeight: 250, justifyContent: "center", gap: 10, flexWrap: "wrap", borderWidth: 1, borderRadius: 4, borderColor: "#dddddd"}}>
                  <View style={{}}>
                    <FontAwesome6 name="image" size={180} color="#ffffff14"/> {/* this is just a placeholder. this image icon will be gone once the user has uploaded an image. however, I haven't coded this functionality yet. */}
                  </View>
                  {symptomImagesUri && symptomImagesUri.map(image => <SymptomImage uri={ image.uri } fileName={image.fileName} symptomImagesUri={symptomImagesUri} setSymptomImagesUri={setSymptomImagesUri} />)}
                </View>
              </ScrollView>
              <TouchableOpacity style={styles.diagnose}><Text style={{textAlign: "center", fontSize: 20}}>Diagnose</Text></TouchableOpacity>
        </View>
    </View>
    
    {/* </ScrollView> */}
    {/* </LinearGradient> */}
    {/* </ImageBackground>
   </SafeAreaView> */}
    </>
  );


}  
    
function NavBar() {
  const pathN = usePathname()
 
  return (
      <BlurView intensity={50} tint="light" style={styles.navBar}>
        <Link href="/" style = {[styles.link, pathN === "/" && styles.activeLink]}>Home</Link>
        <Link href="/home" style = {[styles.link, pathN === "/home" && styles.activeLink]}>Diagnose</Link>
        <Link href="/about" style = {[styles.link, pathN === "/about" && styles.activeLink]}>About</Link>
        <Link href="/login" style = {[styles.link, pathN === "/login" && styles.activeLink]}>Login</Link>
      </BlurView>
      
      
  
  );
}


function CameraCapture({ showCamera, setShowCamera }) {
  const webcamRef = React.useRef(null);

  const capturePhoto = () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      console.log(imageSrc);
    }
  };

  return (
    <div style={{ alignItems: "center", marginTop: 20 }}>
      {showCamera && (
        <div style={{ marginTop: 20 }}>
          <Webcam
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            width={400}
            height={300}
            videoConstraints={{
              width: 400,
              height: 300,
              facingMode: "environment",
              alignSelf: "center"
            }}
          />
        </div>
      )}
    </div>
  );
} 



function sortKeys(a, b) {
  if (a < b) return -1;
  else if (a > b) return 1;
  return 0;
}

function getPlantSymptoms(data, name) {
  const symptoms = data.find((e) => e["key"] === name);
  if (symptoms !== undefined) {
    return symptoms["value"].map((e) => ({ key: e, value: e }));
  }
  return []
}

const styles = StyleSheet.create({

  safeArea: { 
    flex: 1,
    backgroundColor: '#f0f0f0',
  },

  container: {
    position: "absolute",
    top: 0,
    left:0,
    right: 0,
    zIndex: 10,
  },

  glass: {

  },

  navBar: {
    position: "absolute",
  top: 0,
  left: 0,
  right: 0,
  zIndex: 100,

  flexDirection: "row",
  justifyContent: "center",
  alignItems: "center",
  paddingVertical: 15,

  backgroundColor: "rgba(255,255,255,0.25)",
  borderBottomWidth: 1,
  borderBottomColor: "rgba(255,255,255,0.3)",

  shadowColor: "#000",
  shadowOffset: { width: 0, height: 10 },
  shadowOpacity: 0.2,
  shadowRadius: 20,
  // elevation: 10,
  },

  link: {
    fontSize: 18,
    paddingHorizontal: 12,
    paddingVertical: 6,
    fontWeight: "normal",
  },

  activeLink: {
    color: "#4CAF50",
    fontWeight: "bold",
  },

  heroRow: {
  flexDirection: "row",
  justifyContent: "center",
  alignItems: "center",
  gap: 50,
  marginTop: 85,
  flexWrap: "wrap"
},


heroBlur: {
  paddingVertical: "2%",
  paddingHorizontal: "3%",
  backgroundColor: "transparent", // 👈 important
},

heroGlassHoverA: {
  borderColor: "rgba(251, 138, 0, 0.9)",

  shadowColor: "rgba(112, 66, 10, 0.9)",
  shadowOffset: { width: 0, height: 0 },
  shadowOpacity: 0.8,
  shadowRadius: 30,
},

heroGlassHoverB: {
  borderColor: "rgba(76, 175, 80, 0.9)",

  shadowColor: "#0d6510ff",
  shadowOffset: { width: 0, height: 0 },
  shadowOpacity: 0.8,
  shadowRadius: 30,
},

heroGlassHoverC: {
  borderColor: "rgba(51, 0, 255, 0.9)",

  shadowColor: "#180372ff",
  shadowOffset: { width: 0, height: 0 },
  shadowOpacity: 0.8,
  shadowRadius: 30,
},

heroGlass: {
  width: 260,
  height: 400,
  borderRadius: 20,
  overflow: "hidden",

  borderWidth: 1,
  borderColor: "rgba(255,255,255,0.35)",
  backgroundColor: "rgba(255,255,255,0.10)",

  shadowColor: "#000",
  shadowOffset: { width: 0, height: 12 },
  shadowOpacity: 0.18,
  shadowRadius: 25,
},

heroTitle: {
  fontSize: '6vw',
  textAlign: "left",
  // fontFamily: "YourTitleFont",
},

heroSubtitle: {
  fontSize: "3vw",
  fontStyle: "italic",
},

zipcode: {backgroundColor: "#dddddd", padding: 5, borderWidth: 1, borderRadius: 10, height: 45, borderColor: "gray", outlineStyle: "none", flex: 1, marginRight: 5},

diagnose:
  {
    backgroundColor: "#8083ff",
    marginBottom: -10,
    padding: 15,
    borderRadius: 10,
    width: "50%",
    alignSelf: "center"
  }
}); 
