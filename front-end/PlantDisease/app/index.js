import React, { useRef, useState } from "react";
import { Button, View, Text, Image, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { MultipleSelectList, SelectList } from "react-native-dropdown-select-list";
import {Link, usePathname, Stack} from "expo-router"
import {useEffect} from "react"
import kb from "./kb.json";
import Webcam from "react-webcam";
import { UserProvider } from "./UserContext";
import * as DocumentPicker from 'expo-document-picker';
import { responsiveHeight, responsiveWidth, responsiveFontSize } from "react-native-responsive-dimensions";
import Markdown from 'react-native-markdown-display';


export default function Index() {

  const { user } = useContext(UserContext);
  const [hovered, setHovered] = useState(false);
  
  

  const [fontsLoaded] = useFonts({
    "IBM-Plex-Italic": require("../assets/fonts/ibm.ttf"),
  });



  useEffect(() => {
    if (typeof document !== "undefined") {
      document.title = "Plant Diagnosis";
    }
  }, []);

  if (!fontsLoaded) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <Text>Loading…</Text>
      </View>
    );
  }


  return (
    
    <ImageBackground
  source={require("../assets/images/glassmorphism.png")}
 // 👈 your image
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

       

    <View
      style={{
        flexDirection: "column",
        flex: 1,
        justifyContent: "space-between"
      }}

    >

    <NavBar />

    <Stack.Screen options={{ title: "Plant Disease Identification System", headerTitleAlign: "center" }} />

    <Text style={{ fontSize: 30, fontWeight: "bold", textAlign: "center", marginTop: 30 }}>
    Choose Symptoms
    </Text>

    <View style={{ flexDirection: "row", marginTop: 30, justifyContent: "center" }}>
      <View style={{ flexDirection: "row", overflow: "visible" }}>
      <SelectList
        setSelected={(val) => setInput({ ...input, plant: val })}
        data={data.map((e) => ({ key: e.key, value: e.key }))}
        save="value"
        placeholder="Choose a Plant"
        searchPlaceholder="Type to Search"
        inputStyles={{ textAlign: "center" }}
        boxStyles={{ marginRight: 20 }}
        responsiveHeight
      />

      <View style={{ marginRight: 15 }}>
        <MultipleSelectList
          setSelected={(val) => setSelected(val)}
          data={input.plant ? getPlantSymptoms(data, input.plant) : []}
          onSelect={() => {
            if (showError) setShowError(false);
            setInput({ ...input, symptoms: selected });
          }}
          boxStyles={{
            pointerEvents: input.plant === "" ? "none" : "auto",
            opacity: input.plant === "" ? 0.4 : 1
          }}
          save="value"
          placeholder="Select the symptoms"
          searchPlaceholder="Type to Search"
          inputStyles={{ textAlign: "center" }}
          dropdownStyles={{
          maxHeight: 200
        }}
        />

        {showError && (
          <Text style={{ color: "red", marginLeft: 8 }}>
            Please select a valid symptom for plant
          </Text>
        )}
      </View>

      <TouchableOpacity
  onPress={async () => {
    const plantEntry = data.find((e) => e.key === input.plant);

    if (!plantEntry || input.symptoms.some((s) => !plantEntry.value.includes(s))) {
      setShowError(true);
      return;
    }

    try {
      const response = await fetch(
        "http://localhost:5000/diagnose",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(input),
        }
      );

      const dataResp = await response.text();
      console.log(dataResp);

      if (!response.ok) {
        setResult("Error: " + (dataResp.error || response.statusText));
      } else {
        setResult(dataResp);
      }
    } catch (err) {
      setResult("Network error: " + err.message);
    }
  }}
  style={{
    width: responsiveWidth(10),
    height: responsiveHeight(5),
    backgroundColor: "#40ff00",
    borderRadius: 75,
    alignItems: "center",
    justifyContent: "center",
  }}
>
  <Text style={{ color: "#4f4f4f", fontSize: responsiveFontSize(1) }}>
    Diagnose Plant
  </Text>
</TouchableOpacity>

    </View>
    </View>

    {result && (
      <Markdown style={{body: {lineHeight: 24}}}>{result}</Markdown>
    )}

    {imageResult && ( // ⭐ NEW CODE
      <View style={{ marginTop: 20, alignItems: "center" }}>
        <Text style={{ fontSize: 18, fontWeight: "bold" }}>Image Diagnosis:</Text>
        <Text>Predicted Class Index: {imageResult.predicted_class_index}</Text>
        <Text>Confidence: {imageResult.confidence_percent?.toFixed(2)}%</Text>
      </View>
    )}

    <View style={{ flexDirection: "row", justifyContent: "center", marginBottom: 40 }}>
      {images}
    </View>

    <Text style={{ fontSize: 30, fontWeight: "bold", textAlign: "center", marginBottom: 30 }}>
      Upload Image
    </Text>



  {/* badges row (doesn't affect bubble centering as much) */}
  <View style={styles.badgeRow}>
    <Image
      source={require("../assets/images/aStore.svg")} // use PNG for RN web unless using react-native-svg
      style={styles.appBadge}
      resizeMode="contain"
      
    />
    <Image
      source={require("../assets/images/play.png")}
      style={styles.playBadge}
      resizeMode="contain"
    />
    
  </View>
  <Text style={styles.heroSubtitle2}>This website is currently under construction</Text>
</View>
    
      </LinearGradient>
      </ImageBackground>
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


const styles = StyleSheet.create({
  container: {
    position: "absolute",
    top: 0,
    left:0,
    right: 0,
    zIndex: 10,
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

  heroGlass: {
  width: "55%",
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

heroSubtitle2: {
  fontSize: "2vw",
  marginTop: 15,
  fontStyle: "italic",
},

heroContainer: {
  flex: 1,
  justifyContent: "center",   // vertical center
  alignItems: "center",       // horizontal center
  
  paddingTop: 10,
},

heroGlassHover: {
  borderColor: "rgba(76, 175, 80, 0.9)",

  shadowColor: "#4CAF50",
  shadowOffset: { width: 0, height: 0 },
  shadowOpacity: 0.8,
  shadowRadius: 30,
},

heroBlur: {
  paddingVertical: "2%",
  paddingHorizontal: "3%",
  backgroundColor: "transparent", // 👈 important
},



playBadge: {
  width: 180,     // 👈 smaller
  height: 55,     // 👈 keeps correct ratio
  marginTop: 16,
},

appBadge: {
  width: 180,     // 👈 smaller
  height: 55,     // 👈 keeps correct ratio
  marginTop: 16,

},

badgeRow: {
  flexDirection: "row",
  justifyContent: "center",
  alignItems: "center",
  marginTop: 18,
  gap: 16, // works on web + modern RN
},



});

 

    
 

