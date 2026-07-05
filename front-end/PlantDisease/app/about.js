import {ImageBackground, View, Text, Pressable, ScrollView, StyleSheet, Animated } from "react-native";
import {Link, usePathname, Stack} from "expo-router"
import {useState, useEffect, useRef} from "react"
import {LinearGradient} from "expo-linear-gradient"
import { BlurView } from "expo-blur";

function Accordion({ title, children, style }) {
  const [open, setOpen] = useState(false);
  const animation = useRef(new Animated.Value(0)).current;
  const [hovered, setHovered] = useState(false);

  useEffect(() => {
    Animated.timing(animation, {
      toValue: open ? 1 : 0,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [open]);

  const animatedStyle = {
    maxHeight: animation.interpolate({
      inputRange: [0, 1],
      outputRange: [0, 500], // adjust if content is taller
    }),
    opacity: animation.interpolate({
      inputRange: [0, 1],
      outputRange: [0, 1],
    }),
  };

  return (
    <View style={[{ width: "85%", marginTop: 20 }, style]}>
     <Pressable
   onPress={() => setOpen(!open)}
  style={({ hovered, focused }) => [
    styles.accordionHeader,
    hovered && styles.heroGlassHover,
    (focused) && { outlineStyle: "none" }, // web
  ]}
>


        <Text style={{ fontSize: 22, fontWeight: "bold", textAlign: "center" }}>
          {title}
        </Text>
      </Pressable>

      <Animated.View style={[animatedStyle]}>
        <View
          style={{
            padding: 16,
            marginTop: 15,
            marginBottom: 15,
            // backgroundColor: "rgba(255,255,255,0.6)",
            // borderRadius: 10,
          }}
        >
          {children}
        </View>
      </Animated.View>
    </View>
  );
}


   

export default function Index() {

  useEffect(() => {
    document.title = "Plant Diagnosis"
  }, [])


  return (

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
      // paddingTop: 70,
      paddingBottom: 100,
      alignItems: "center",
    }}
  >
     <NavBar />
    <View
      style={{
        flexDirection: "column",
        flex: 1,
        justifyContent: "flex-start"
      }}
    >
   <View style = {styles.pageHeader}>
    <Text style = {styles.pageTitle}>Plant Disease Identification</Text>
    <Text style = {styles.pageSubtitle}><strong>This application is a prototype.</strong></Text>
    </View>
    <View style= {{alignItems: "center"}}>
   <Accordion title="What is this?" style = {styles.heroGlass}>
  <Text style={{ fontSize: 15, textAlign: "left" }}>
    This is a 2025–2026 Computer Science Capstone Project prototype written by
    Josh Hanson, Mason Lewis, Matthew Murphy, David Markowski, and Eh Doh Kue Kyi
    for faculty advisor Dr. Mohammadreza Hajiarbabi at Purdue University Fort Wayne.
    Our goal is to utilize machine learning models, expert system rules, and image
    preprocessing libraries to create diagnostic reports for plants suffering
    from disease or infestation.
  </Text>
</Accordion>
   <Accordion title="How do the diagnostics work?" style = {styles.heroGlass}>
    <Text style = {{fontSize: 15, textAlign: "left"}}>We are using trained machine learning models, expert system libraries, and image
    preprocessing techniques to create generative diagnostic reports. Our text based system uses
    Bayesian statistics alongside data scraped from current and reputable sources to return
    diagnoses and diagnostic reports from user-given information. Our image-based system uses Machine Learning models trained using TensorFlow/Keras to return a diagnosis with an accuracy.
    of ≥ 85-90%.
    </Text>
    </Accordion>
    <Accordion title="Where does your data come from?" style = {styles.heroGlass}>
    <Text style = {{fontSize: 15, textAlign: "left"}}>For the prototpe, we are using a PlantVillage dataset of ". . . around 54,303 images"
    to train our Machine Learning models. We have also received help and guidance from
    faculty at Purdue West Lafayette. Our symptom and diagnosis registry has been scraped
    from PlantVillage as well.</Text>
    </Accordion>
    <Accordion title="More Information" style = {styles.heroGlass}>
    <Text style = {{fontSize: 15, textAlign: "left"}}><a href = "https://plantvillage.psu.edu/plants">https://plantvillage.psu.edu/plants</a></Text>
    <Text style = {{fontSize: 15, textAlign: "left"}}><a href = "https://www.kaggle.com/datasets/mohitsingh1804/plantvillage">https://www.kaggle.com/datasets/mohitsingh1804/plantvillage</a></Text>
    <Text style = {{fontSize: 15, textAlign: "left"}}><a href = "https://www.apsnet.org/edcenter/resources/commonnames/Pages/default.aspx">https://www.apsnet.org/edcenter/resources/commonnames/Pages/default.aspx</a></Text>
    <Text style = {{fontSize: 15, textAlign: "left"}}><a href = "https://www.extension.purdue.edu/extmedia/BP/BP-164-W.pdf">https://www.extension.purdue.edu/extmedia/BP/BP-164-W.pdf</a></Text>
    </Accordion>
    </View>
    <Stack.Screen options = {{title: "Plant Disease Identification System", headerTitleAlign: "center"}} />
    
    </View>
  <Text style={styles.heroSubtitle2}>This website is currently under construction</Text>
  </ScrollView>
  
  </LinearGradient>
  
  </ImageBackground>
  
  );
}

function NavBar() {
  const pathN = usePathname()

  const linkBar = (path) => ({
    fontSize: 18,
    paddingHorizontal: 12,
    paddingVertical: 6,
    color: pathN === path ? "#4CAF50" : "black",
    fontWeight: pathN === path ? "bold" : "normal",
  });
 
  return (
    <BlurView intensity={50} tint="light" style={styles.navBar}>
      <Link href="/" style={linkBar("/")}>Home</Link>
      <Link href="/home" style={linkBar("/home")}>Diagnose</Link>
      <Link href="/about" style={linkBar("/about")}>About</Link>
      <Link href="/login" style = {linkBar("/login")}>Login</Link>
  </BlurView>
  );

}

 const styles = StyleSheet.create({

  heroGlass: {
  width: "55%",
  borderRadius: 10,
  // overflow: "hidden",

  borderWidth: 1,
  borderColor: "rgba(255,255,255,0.35)",
  backgroundColor: "rgba(255,255,255,0.10)",

  shadowColor: "#000",
  shadowOffset: { width: 0, height: 12 },
  shadowOpacity: 0.18,
  shadowRadius: 25,
  },

  heroGlassHover: {
  // borderWidth: 1,
  borderColor: "rgba(76, 175, 80, 0.8)",

  // Native shadow
  shadowColor: "#4CAF50",
  shadowOffset: { width: 0, height: 0 },
  shadowOpacity: 0.6,
  shadowRadius: 25,

  // ✅ Web glow (React Native Web)
  boxShadow: "0 0 25px rgba(76, 175, 80, 0.6)",
},

accordionHeader: {
  paddingVertical: 12,
  paddingHorizontal: 16,
  borderRadius: 10,

  // IMPORTANT: keep border width 0 normally
  borderWidth: 0,
},

heroSubtitle2: {
  fontSize: "2vw",
  marginTop: 15,
  fontStyle: "italic",
},

 navBar: {
    position: "sticky",
    width: "100%",
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

  pageText: {
 width: "100%",
    maxWidth: 900,
    alignSelf: "stretch",
    paddingHorizontal: 16,
},

pageHeader: {
    width: "100%",
    maxWidth: 1000,
    paddingHorizontal: 16,
    alignItems: "center",
    alignSelf: "center",
    marginTop: 20,
  },

  pageTitle: {
    fontWeight: "bold",
    textAlign: "center",

    // ✅ web responsive
    fontSize: "clamp(24px, 5vw, 44px)",

    // keeps it from “cutting off”
    flexShrink: 1,
    width: "100%",
  },

  pageSubtitle: {
    textAlign: "center",
    marginTop: 8,
    fontSize: "clamp(12px, 1.6vw, 16px)",
    width: "100%",
    flexShrink: 1,
  },


});