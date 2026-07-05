import React, { useRef, useState, useContext} from "react";
import { Button, View, Text } from "react-native";
import { SelectList } from "react-native-dropdown-select-list";
import {Link, usePathname, Stack, useRouter} from "expo-router"
import {useEffect} from "react"
import kb from "./kb.json";
import Webcam from "react-webcam";
import { UserContext } from "./UserContext";


export default function Index() {

  const {user} = useContext(UserContext)

  useEffect(() => {
    document.title = "Plant Diagnosis"
  }, [])

  return (

    <View
      style={{
        flexDirection: "column",
        flex: 1,
        justifyContent: "space-between"
      }}
    >
    <NavBar />

    
        <Stack.Screen
        options={{
        title: user ? `Plant Disease Identification System for ${user}` : "Plant Disease Identification System",
        headerTitleAlign: "center",
      }}
    />
    
    
      </View>
  );
}

function NavBar() {
  const pathN = usePathname()
  const { user, setUser } = useContext(UserContext)
  const router = useRouter()

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

