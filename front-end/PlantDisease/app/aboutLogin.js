import React, { useContext, useEffect } from "react";
import { Button, View, Text, ScrollView } from "react-native";
import { Link, usePathname, Stack, useRouter } from "expo-router";
import { UserContext } from "./UserContext";

export default function Index() {
  const { user } = useContext(UserContext);

  useEffect(() => {
    document.title = "Plant Diagnosis";
  }, []);

  return (
    <>
      <Stack.Screen
        options={{
          title: user
            ? `Plant Disease Identification System for ${user}`
            : "Plant Disease Identification System",
          headerTitleAlign: "center",
        }}
      />
      <AboutContent />
    </>
  );
}

function AboutContent() {
  return (
    <ScrollView
      contentContainerStyle={{
        paddingBottom: 100,
        alignItems: "center",
      }}
    >
      <NavBar />

      <View
        style={{
          flexDirection: "column",
          justifyContent: "flex-start",
        }}
      >
       <Text style = {{fontSize: 40, fontWeight: "bold", textAlign: "center"}}>Plant Disease Identification</Text>
           <Text style = {{fontSize: 15, textAlign: "center"}}><br></br><strong>This application is a prototype and is currently under construction, so features<br></br>
           may not work exactly as described, may not work at all, or might be a little wonky.</strong></Text>
           <Text style = {{fontSize: 30, textAlign: "center"}}><br></br>What is this?</Text>
           <Text style = {{fontSize: 15, textAlign: "justify", marginLeft: 50}}>This is a 2025-2026 Computer Science Capstone Project prototype written by Josh<br></br>Hanson, Mason Lewis, Matthew Murphy, 
           David Markowski, and Eh Doh Kue Kyi for<br></br>faculty advisor Dr. Mohammadreza Hajiarbabi at Purdue University Fort Wayne. Our<br></br>goal is to utilize
           machine learning models, expert system rules, and image preprocessing<br></br>libraries to create diagnostic reports
           for plants suffering from disease or infestation.</Text>
           <Text style = {{fontSize: 30, textAlign: "center", marginTop: 30}}>How do the diagnostics work?</Text>
           <Text style = {{fontSize: 15, textAlign: "justify", marginLeft: 50}}>We are using trained machine learning models, expert system libraries, and image<br></br>
           preprocessing techniques to create generative diagnostic reports. Our text based system<br></br>uses
           Bayesian statistics alongside data scraped from current and reputable sources to retun<br></br>
           diagnoses and diagnostic reports from user-given information. Our image-based system uses<br></br>Machine Learning models trained using TensorFlow/Keras to return a diagnosis with an accuracy.<br></br>
           of ≥ 85-90%.
           </Text>
           <Text style = {{fontSize: 30, textAlign: "center", marginTop: 30}}>Where does your data come from?</Text>
           <Text style = {{fontSize: 15, textAlign: "justify", marginLeft: 50}}>For the prototpe, we are using a PlantVillage dataset of ". . . around 54,303 images"<br></br>
           to train our Machine Learning models. We have also received help and guidance from<br></br>
           faculty at Purdue West Lafayette. Our symptom and diagnosis registry has been scraped<br></br>
           from PlantVillage as well.</Text>
           <Text style = {{fontSize: 30, textAlign: "center", marginTop: 30}}>Sources</Text>
           <Text style = {{fontSize: 15, textAlign: "center"}}><a href = "https://plantvillage.psu.edu/plants">https://plantvillage.psu.edu/plants</a></Text>
           <Text style = {{fontSize: 15, textAlign: "center"}}><a href = "https://www.kaggle.com/datasets/mohitsingh1804/plantvillage">https://www.kaggle.com/datasets/mohitsingh1804/plantvillage</a></Text>
           <Text style = {{fontSize: 15, textAlign: "center"}}><a href = "https://www.apsnet.org/edcenter/resources/commonnames/Pages/default.aspx">https://www.apsnet.org/edcenter/resources/commonnames/Pages/default.aspx</a></Text>
           <Text style = {{fontSize: 15, textAlign: "center"}}><a href = "https://www.extension.purdue.edu/extmedia/BP/BP-164-W.pdf">https://www.extension.purdue.edu/extmedia/BP/BP-164-W.pdf</a></Text>
      </View>
    </ScrollView>
  );
}


function NavBar() {
  const pathN = usePathname();
  const { user, setUser } = useContext(UserContext);
  const router = useRouter();

  const linkBar = (path) => ({
    fontSize: 18,
    paddingHorizontal: 12,
    paddingVertical: 6,
    color: pathN === path ? "#4CAF50" : "black",
    fontWeight: pathN === path ? "bold" : "normal",
  });

  return (
    <View
      style={{
        width: "100%",
        flexDirection: "row",
        justifyContent: "center",
        alignItems: "center",
        paddingVertical: 15,
        backgroundColor: "#e8f5e9",
        borderBottomWidth: 1,
        borderBottomColor: "#c8e6c9",
      }}
    >
      <Link href="/homeLogin" style={linkBar("/homeLogin")}>Home</Link>
      <Link href="/indexLogin" style={linkBar("/indexLogin")}>Diagnose</Link>
      <Link href="/aboutLogin" style={linkBar("/aboutLogin")}>About</Link>

      {user && (
        <Button
          title="Logout"
          color="red"
          onPress={() => {
            setUser(null);
            router.replace("/");
          }}
        />
      )}
    </View>
  );
}
