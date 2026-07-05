import{useState, useContext, useEffect } from "react";
import {
  Button,
  View,
  Text,
  Image,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import { MultipleSelectList, SelectList } from "react-native-dropdown-select-list";
import { Link, usePathname, Stack, useRouter } from "expo-router";
import kb from "./kb.json";
import { UserContext } from "./UserContext";
import * as DocumentPicker from "expo-document-picker";
import {
  responsiveHeight,
  responsiveWidth,
  responsiveFontSize,
} from "react-native-responsive-dimensions";


export default function Index() {
  const { user } = useContext(UserContext);

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
      <IndexContent />
    </>
  );
}


function IndexContent() {
  const [selected, setSelected] = useState([]);
  const [input, setInput] = useState({ plant: "", symptoms: [] });
  const [showError, setShowError] = useState(false);
  const [result, setResult] = useState(null);
  const [imageResult, setImageResult] = useState(null);
  const [images, setImages] = useState([]);

  useEffect(() => {
    document.title = "Plant Diagnosis";
  }, []);


  const symptoms = kb.symptoms;
  const plantData = [];

  for (const [symptomKey, arr] of Object.entries(symptoms)) {
    for (const obj of arr) {
      if (!obj?.plant) continue;
      const found = plantData.find((d) => d.key === obj.plant);
      if (found) {
        if (!found.value.includes(symptomKey)) found.value.push(symptomKey);
      } else {
        plantData.push({ key: obj.plant, value: [symptomKey] });
      }
    }
  }

  plantData.sort((a, b) => (a.key < b.key ? -1 : 1));
  plantData.forEach((e) => e.value.sort());

  return (
    <ScrollView
      contentContainerStyle={{ paddingBottom: 150, alignItems: "center" }}
    >
      <NavBar />

      <Text style={{ fontSize: 32, fontWeight: "bold", marginTop: 30 }}>
        Choose Symptoms
      </Text>

      <View style={{ flexDirection: "row", marginTop: 30 }}>
        <SelectList
          setSelected={(val) =>
            setInput((prev) => ({ ...prev, plant: val }))
          }
          data={plantData.map((e) => ({ key: e.key, value: e.key }))}
          save="value"
          placeholder="Choose a Plant"
        />

        <MultipleSelectList
          setSelected={setSelected}
          data={
            input.plant
              ? getPlantSymptoms(plantData, input.plant)
              : []
          }
          onSelect={() => {
            setShowError(false);
            setInput((prev) => ({ ...prev, symptoms: selected }));
          }}
          save="value"
          placeholder="Choose Symptoms"
        />
      </View>

      <TouchableOpacity
        onPress={async () => {
          const plantEntry = plantData.find(
            (e) => e.key === input.plant
          );

          if (
            !plantEntry ||
            input.symptoms.some(
              (s) => !plantEntry.value.includes(s)
            )
          ) {
            setShowError(true);
            return;
          }

          try {
            const resp = await fetch(
              "https://plantdisease-932821527783.europe-west1.run.app/api/diagnose",
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(input),
              }
            );

            const text = await resp.text();
            setResult(text);
          } catch (err) {
            setResult("Error: " + err.message);
          }
        }}
        style={{
          width: responsiveWidth(20),
          height: responsiveHeight(6),
          backgroundColor: "#40ff00",
          borderRadius: 50,
          justifyContent: "center",
          alignItems: "center",
          marginTop: 30,
        }}
      >
        <Text
          style={{
            fontSize: responsiveFontSize(1.6),
            fontWeight: "bold",
          }}
        >
          Diagnose
        </Text>
      </TouchableOpacity>

      {showError && (
        <Text style={{ color: "red", marginTop: 10 }}>
          Invalid symptoms
        </Text>
      )}

      {result && (
        <View style={{ marginTop: 20, padding: 10 }}>
          <Text style={{ whiteSpace: "pre-line", fontSize: 16 }}>
            {result}
          </Text>
        </View>
      )}

      <Text style={{ fontSize: 30, fontWeight: "bold", marginTop: 40 }}>
        Upload Image
      </Text>

      <Button
        title="Choose Image"
        onPress={async () => {
          try {
            const file = await DocumentPicker.getDocumentAsync({
              type: ["image/jpeg", "image/png"],
            });

            if (file?.assets?.length > 0) {
              const asset = file.assets[0];
              const fd = new FormData();
              fd.append("image", asset.file);

              const resp = await fetch(
                "https://plantdisease-932821527783.europe-west1.run.app/api/diagnoseImage",
                { method: "POST", body: fd }
              );

              const json = await resp.json();
              setImageResult(json);

              setImages([
                <Image
                  key={asset.uri}
                  source={{ uri: asset.uri }}
                  style={{
                    width: responsiveFontSize(12),
                    height: responsiveFontSize(12),
                    marginTop: 10,
                  }}
                />,
              ]);
            }
          } catch (err) {
            setImageResult({ error: err.message });
          }
        }}
      />

      {imageResult && !imageResult.error && (
        <View style={{ marginTop: 25 }}>
          <Text style={{ fontSize: 20, fontWeight: "bold" }}>
            Image Diagnosis
          </Text>
          <Text>Class Index: {imageResult.predicted_class_index}</Text>
          <Text>
            Confidence: {imageResult.confidence_percent?.toFixed(2)}%
          </Text>
        </View>
      )}

      {imageResult?.error && (
        <Text style={{ color: "red", marginTop: 10 }}>
          Image Error: {imageResult.error}
        </Text>
      )}

      {images.length > 0 && <View>{images}</View>}
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


function getPlantSymptoms(data, name) {
  const obj = data.find((e) => e.key === name);
  return obj ? obj.value.map((s) => ({ key: s, value: s })) : [];
}
