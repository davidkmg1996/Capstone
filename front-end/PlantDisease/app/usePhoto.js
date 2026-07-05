import React, { useRef, useState } from "react";
import {Pressable, ImageBackground, StyleSheet, Button, View, Text, Image, TouchableOpacity, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { MultipleSelectList, SelectList } from "react-native-dropdown-select-list";
import {Link, usePathname, Stack, router} from "expo-router";
import {BlurView} from "expo-blur";
import {LinearGradient} from "expo-linear-gradient"
import {useEffect} from "react";
import kb from "./kb.json";
import Webcam from "react-webcam";
import { UserProvider } from "./UserContext";
import * as DocumentPicker from 'expo-document-picker';
import { responsiveHeight, responsiveWidth, responsiveFontSize } from "react-native-responsive-dimensions";

// const {width, height} = Dimensions.get("window");
// const baseWidth = 375;
// const baseHeight = 812;
export default function Index({children}) {
  return (
    <UserProvider>
    <IndexContent />
    </UserProvider>
    
  );
};

function IndexContent(){
  const [selected, setSelected] = useState("");
  const [input, setInput] = useState({ plant: "", symptoms: []});
  const [showError, setShowError] = useState(false);
  const [result, setResult] = useState(null);
  const [imageResult, setImageResult] = useState(null); // ⭐ NEW CODE
  const formData = useRef(new FormData());
  const [showCamera, setShowCamera] = useState(false);
  const [images, setImages] = useState([]);
  const [hovered, setHovered] = useState(false);
  const [hoveredB, setHoveredB] = useState(false);
  const [hoveredC, setHoveredC] = useState(false);


  useEffect(() => {
    document.title = "Plant Diagnosis"

  }, [])

 
  const symptoms = kb.symptoms;
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

  data.sort((a, b) => sortKeys(a["key"], b["key"]));
  data.forEach((e) => e["value"].sort());


  return (
    <SafeAreaView style = {styles.safeArea}>
         <ImageBackground
  source={require("../assets/images/glassmorphism.png")}
  resizeMode="cover"
  style={{ flex: 1 }}
>
     <LinearGradient
        colors={[
  "rgba(71,196,80,0.5)",
  "rgba(191,198,195,0.5)"
]}
   start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={{ flex: 1 }}
      >

    
  <ScrollView
    contentContainerStyle={{
      paddingBottom: 0,
      alignItems: "center",
    }}
  >

    <NavBar />

    <Stack.Screen options={{ title: "Plant Disease Identification System", headerTitleAlign: "center" }} />

   {imageResult?.image_symptoms?.length > 0 && (
  <>
   
  </>
)}


    <Text style={{ fontSize: 30, fontWeight: "bold", textAlign: "center", marginTop: "5%", marginBottom: "3%"}}>
      Upload Image
    </Text>

    <View style={{ flexDirection: "row", justifyContent: "center" }}>
      {images}
    </View>

    {imageResult?.image_symptoms?.length > 0 && (
  <>
    <Text style={{ fontWeight: "bold", marginTop: 10 }}>
      Detected Symptoms:
    </Text>

    {imageResult.image_symptoms.map((s, i) => (
      <Text key={i}>
        {s.symptom_name} — {s.probability_percent}%
      </Text>
    ))}
  </>
)}


   {imageResult?.expert_probabilities?.length > 0 && (
  <>
    <Text style={{ marginTop: "1%", fontWeight: "bold" }}>
      Most Likely Disease:
    </Text>
    <Text>
      {imageResult.expert_probabilities[0][0]} (
      {imageResult.expert_probabilities[0][1]}%)
    </Text>
  </>
)}

    
    <View style={{ flexDirection: "row", gap: 15, marginBottom: 20 }}>
        <View style = {{flexDirection: "row", gap: 15,marginTop: 30}}>
      <Button
        onPress={async () => {
          try {
            const result = await DocumentPicker.getDocumentAsync({
              type: ["image/jpeg", "image/png"],
              copyToCacheDirectory: true,
            });

            if (result.canceled) return;

            const asset = result.assets[0];

            // push preview
            setImages([
              <View key={asset.file.name} style={{ marginRight: 10 }}>
                <Image
                  source={{ uri: asset.uri }}
                  style={{
                    width: responsiveFontSize(10),
                    height: responsiveFontSize(10)
                  }}
                />
                <Text style={{
                  width: responsiveFontSize(10),
                  fontSize: responsiveFontSize(1)
                }}>{asset.file.name}</Text>
              </View>
            ]);

            const fd = new FormData();
            fd.append("image", asset.file);

            const resp = await fetch(
              "https://plantdisease-932821527783.europe-west1.run.app/api/diagnoseImage",
              { method: "POST", body: fd }
            );

            const prediction = await resp.json();
            setImageResult(prediction); // ⭐ NEW CODE

          } catch (error) {
            setImageResult({ error: error.message });
          }
        }}
        title="Upload"
      />

      <Button title="Capture Image" onPress= {() => setShowCamera(true)}/>

      <CameraCapture showCamera={showCamera} setShowCamera={setShowCamera} />
      </View>

    </View>
    
      <Button title="Return" onPress= {() => router.replace('/home')}>
      </Button>
    </ScrollView>
    </LinearGradient>
    </ImageBackground>
   </SafeAreaView>
  )
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

}); 
