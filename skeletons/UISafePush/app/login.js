import React, { useRef, useState, useContext } from "react";
import { Button, View, Text, TextInput, StyleSheet, Alert} from "react-native";
import { SelectList } from "react-native-dropdown-select-list";
import {Link, usePathname, Stack, useRouter} from "expo-router"
import {useEffect} from "react"
import kb from "./kb.json";
import Webcam from "react-webcam";
import { UserContext } from "./UserContext";


export default function Login() {

  const router = useRouter()
  const {setUser} = useContext(UserContext)

  useEffect(() => {
    document.title = "Plant Diagnosis"
  }, [])
  
  const [email, getEmail] = useState("");
  const [userName, getUsername] = useState("")
  const [pass, getPass] = useState("");

  const handleLogin = async () => {
    if (!userName || !pass) {
      Alert.alert("Error", "Username and Password required");
      return;
    }

 try {
      const response = await fetch("https://plantdisease-932821527783.europe-west1.run.app/api/login", {
        method: "POST",
        headers: {
      "Content-Type": "application/json"
      },
        body: JSON.stringify({
        username: userName,
        password: pass
        })
      });

      const data = await response.json();

      if (response.status === 200) {
        Alert.alert("Success", "Login Successful");
        getEmail("");
        getUsername("");
        getPass("");
        setUser(userName);
        router.replace("/indexLogin");
      } else {
        Alert.alert("Login Unsuccessful", data.error || "Try again.");
      }
    } catch(error) {
      Alert.alert("Error", "Network or server issue")
      console.error(error)
    }
   };

  return (

    <View
      style={{
        flexDirection: "column",
        flex: 1,
        justifyContent: "flex-start",
        alignItems: "center"
      }}
    >
      
    <NavBar />
    <Stack.Screen options = {{title: "Plant Disease Identification System", headerTitleAlign: "center"}} />
    <Text style = {{fontSize: 40, fontWeight: "bold", textAlign: "center"}}>Log In</Text>
    
    <View style = {[styles.container, {width : 500}]}>
        <TextInput
            style = {styles.input}
            placeholder = "Enter Username"
            value = {userName}
            onChangeText = {getUsername}
            
        />

         <TextInput
            style = {styles.input}
            placeholder = "Enter Password"
            value = {pass}
            onChangeText = {getPass}
            secureTextEntry
        />

       <View style={{ marginTop: 20, }}>
      <Button title="Log in" onPress={handleLogin} />
      </View>

         <Text style = {{fontSize: 30, textAlign: "center", marginTop: 15}}>Not signed up? Register <Link href="/signup" style = {{fontSize: 30, color: "blue"}}>Here</Link></Text>
         
    </View>
    
    </View>

    
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
    <View style = {{
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
      <Link href="/home" style={linkBar("/home")}>Home</Link>
      <Link href="/" style={linkBar("/")}>Diagnose</Link>
      <Link href="/about" style={linkBar("/about")}>About</Link>
      <Link href="/login" style = {linkBar("/login")}>Login</Link>
  </View>
  

  
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    marginTop: 30
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

});

