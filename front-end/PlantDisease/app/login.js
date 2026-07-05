import {useState, useContext, useEffect} from "react";
import {ImageBackground, Button, View, Text, TextInput, StyleSheet, Alert, TouchableOpacity} from "react-native";
import {LinearGradient} from "expo-linear-gradient"
import {Link, usePathname, Stack, useRouter} from "expo-router"
import { BlurView } from "expo-blur";
import { UserContext } from "./UserContext";
import Header from "./Header";
import Feather from '@expo/vector-icons/Feather';
import Fontisto from '@expo/vector-icons/Fontisto';


export default function Login() {

  const router = useRouter()
  const {setUser} = useContext(UserContext)
   const [hovered, setHovered] = useState(false);

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
    <>
    {/* <Header /> */}
    <Stack.Screen options={{headerShown: false}} />
    {/* <View style={{backgroundColor: "#2b2b2b", height: "100%"}}> */}
    <ImageBackground
      source={require("../assets/images/background.jpg")}
      resizeMode="cover"
      style={{width: '100%', height: '100%'}}
    >
      <View style={{height: "100%", backgroundColor: "#00000091"}}>
      {/* <View style = {styles.container}> */}

        <BlurView intensity={60} tint="light" style={styles.container}>
        {/* Username */}
        <View style={styles.input}>
          <Feather name="user" size={30} color="black" style={styles.inputIcon}/>
          <TextInput
              style = {styles.inputText}
              placeholder = "Username"
              value = {userName}
              onChangeText = {getUsername}
              
          />
        </View>

        {/* Password */}
        <View style={[styles.input, {marginTop: 40}]}>
          <Fontisto name="locked" size={25} color="black" style={styles.inputIcon}/>
          <TextInput
              style = {styles.inputText}
              placeholder = "Password"
              value = {pass}
              onChangeText = {getPass}
              secureTextEntry
          />
        </View>

        <View style={styles.logInWrapper}>
          <TouchableOpacity onPress={handleLogin} style={styles.logIn}>
            <Text style={styles.logInText}>Log In</Text>
          </TouchableOpacity>
        </View>

          <Text style = {{fontSize: 16, textAlign: "center", marginTop: 15}}>Not yet registered? <Link href="/signup" style = {{fontSize: 16, color: "blue"}}>Create an account</Link></Text>
          
      {/* </View> */}
      </BlurView>
      </View>
    </ImageBackground>
    </>
    
    
    

    
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
    width: "20%",
    height: "50%",
    marginTop: 200,
    paddingTop: 70,
    borderRadius: 4,
    backgroundColor: "#dad9d9",
    alignSelf: "center",
  },
  input: {
    // backgroundColor: "green",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center"
  },
  inputIcon: {
    marginRight: 10
  },
  inputText: {
    // backgroundColor: "blue",
    borderBottomWidth: 1,
    fontSize: 18,
    outlineStyle: "none",
  },
  logInWrapper: {
    flexDirection: "row",
    justifyContent: "center",
    marginBottom: 30
  },
  logIn: {
    backgroundColor: "blue",
    padding: 10,
    marginTop: 40,
    borderRadius: 10,
    width: "60%"
  },
  logInText: {
    fontSize: 20,
    textAlign: "center"
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

