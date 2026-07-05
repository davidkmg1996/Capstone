import {useState} from "react";
import { BlurView } from "expo-blur";
import {ImageBackground, Button, View, Text, TextInput, StyleSheet, Alert, ScrollView } from "react-native";
import {Link, usePathname, Stack} from "expo-router"
import {LinearGradient} from "expo-linear-gradient"
import {useEffect} from "react"



export default function SignUp() {

  useEffect(() => {
    document.title = "Plant Diagnosis"
  }, [])

   const [email, setEmail] = useState("");
   const [pass, setPass] = useState("");
   const [userName, setUserName] = useState("");

   const handleRegister = async () => {
    if (!userName || !pass) {
      Alert.alert("Error", "Username and Password Required");
      return;
    }

    try {
      const response = await fetch("https://plantdisease-932821527783.europe-west1.run.app/api/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          username: userName,
          password: pass
        })
      });

      const data = await response.json();

      if (response.status === 201) {
        Alert.alert("Success", "Registration Successful");
        setEmail("");
        setUserName("");
        setPass("");
      } else {
        Alert.alert("Registration Unsuccessful", data.error || "Try again.");
      }
    } catch(error) {
      Alert.alert("Error", "Network or server issue")
      console.error(error)
    }
   };

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
                  <NavBar />
    <ScrollView>
  
    <View
      style={{
        flexDirection: "column",
        flex: 1,
        justifyContent: "flex-start",
        alignItems: "center"
      }}
    >
    
    <Stack.Screen options = {{title: "Plant Disease Identification System", headerTitleAlign: "center"}} />
    
    <Text style = {{fontSize: 40, fontWeight: "bold", textAlign: "center", marginTop: 100}}>Register</Text>
     <View style = {[{width: 600, maxWidth: "80%"}, styles.container]}>
            <TextInput
                style = {[styles.input]}
                placeholder = "Enter Your Email"
                value = {email}
                onChangeText = {setEmail}
            />

            <TextInput
                style = {styles.input}
                placeholder = "Choose Username"
                value = {userName}
                onChangeText = {setUserName}
            />
    
             <TextInput
                style = {styles.input}
                placeholder = "Choose a Password"
                value = {pass}
                onChangeText = {setPass}
            />
            <View style = {{marginTop: 20}}>
            <Button
                title = "Register" onPress={handleRegister}
            />
            </View>
             <Text style = {{fontSize: 20, textAlign: "center"}}>Registered? Log in <Link href="/login" style = {{fontSize: 20, color: "blue"}}>Here</Link></Text>
             
        </View>    
    </View>
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
  container: {
    padding: 20,
    marginTop: 15,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 12,
    borderRadius: 8,
    fontSize: 18,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 10
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

});



