import React, { useRef, useState } from "react";
import { Button, View, Text, Image, TouchableOpacity, ScrollView } from "react-native";
import { MultipleSelectList, SelectList } from "react-native-dropdown-select-list";
import {Link, usePathname, Stack} from "expo-router"
import {useEffect} from "react"
import kb from "./kb.json";
import Webcam from "react-webcam";
import { UserProvider } from "./UserContext";
import * as DocumentPicker from 'expo-document-picker';
import { responsiveHeight, responsiveWidth, responsiveFontSize } from "react-native-responsive-dimensions";


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
  <ScrollView
    contentContainerStyle={{
      paddingBottom: 100,
      alignItems: "center",
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
        "https://plantdisease-932821527783.europe-west1.run.app/api/diagnose",
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
        setResult(dataResp.diagnosis);   // 👈 THIS IS THE KEY
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
      <View style={{ marginTop: 20, alignItems: "center" }}>
        <Text style={{ fontSize: 16, color: "black", whiteSpace: "pre-line" }}>
          {result}
        </Text>
      </View>
    )}

   {imageResult?.predicted_symptoms && (
  <View style={{ marginTop: 20 }}>
    <Text style={{ fontSize: 20, fontWeight: "bold" }}>
      Image Diagnosis (Detected Symptoms)
    </Text>

    {imageResult.predicted_symptoms.length > 0 ? (
      imageResult.predicted_symptoms.map((s, idx) => (
        <Text key={idx}>
          Symptom #{s.symptom_index} — {s.probability_percent}%
        </Text>
      ))
    ) : (
      <Text>No symptoms detected above threshold.</Text>
    )}
  </View>
)}



    <View style={{ flexDirection: "row", justifyContent: "center", marginBottom: 40 }}>
      {images}
    </View>

    <Text style={{ fontSize: 30, fontWeight: "bold", textAlign: "center", marginBottom: 30 }}>
      Upload Image
    </Text>

    <View style={{ flexDirection: "row", gap: 15, marginBottom: 20 }}>
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

    

  </ScrollView>
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
      <Link href="/login" style={linkBar("/login")}>Login</Link>
  </View>
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
