import React, { useRef, useState } from "react";
import { Button, View, Text, TextInput, StyleSheet, Alert } from "react-native";
import { SelectList } from "react-native-dropdown-select-list";
import {Link, usePathname, Stack} from "expo-router"
import {useEffect} from "react"
import kb from "./kb.json";
import Webcam from "react-webcam";


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
    <Text style = {{fontSize: 40, fontWeight: "bold", textAlign: "center"}}>Register</Text>
     <View style = {[styles.container, {width : 500}]}>
            <TextInput
                style = {styles.input}
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
             <Text style = {{fontSize: 30, textAlign: "center"}}>Already registered? Log in <Link href="/login" style = {{fontSize: 30, color: "blue"}}>Here</Link></Text>
             
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
    marginTop: 30,
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

