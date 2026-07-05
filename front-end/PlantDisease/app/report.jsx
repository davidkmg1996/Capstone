import { useState, useRef, useEffect } from "react";
import {Animated, StyleSheet, View, Text, TouchableOpacity, Linking, Pressable, Dimensions, ScrollView} from "react-native";
import { Stack } from 'expo-router';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import FontAwesome6 from '@expo/vector-icons/FontAwesome6';
import FontAwesome5 from '@expo/vector-icons/FontAwesome5';
import Feather from '@expo/vector-icons/Feather';
import Header from "./Header";
import Markdown from "react-native-markdown-display";


function CandidateDiseaseReport({textOpacity, header, paragraph, screenHeight})
{
    return(
        <View style={{width: screenHeight * 0.71}}>
            <Animated.Text style={{opacity: textOpacity, fontSize: 30}}>
                {header}
            </Animated.Text>

            {/* Loop through each section's paragraphs and generate the Animated.Text for each paragraph. */}
            <View style={{marginTop: 8, gap: 10}}>
                <Animated.Text style={{opacity: textOpacity, fontSize: 18, lineHeight: 27}}>
                    {paragraph}
                </Animated.Text>
            </View>
        </View>
    )
}


export default function Report()
{
    const [diseaseCandidates, setDiseaseCandidates] = useState({"diseases":[
        {name: "Apple Scab", showReport: false},
        {name: "Cedar-Apple Rust", showReport: false},
        {name: "gemini", showReport: false}
        ]});
    
    const [reportShowing, setReportShowing] = useState(false);
    const [paragraph, setParagraph] = useState("");

    useEffect(() => {
        if(reportShowing && !diseaseCandidates["diseases"].some((item) => item.showReport))
        {
            collapse();
        }
    }, [diseaseCandidates]);
    


    const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
    
    const width = useRef(new Animated.Value(0)).current;
    const scaleY = useRef(new Animated.Value(0.001)).current;
    const textOpacity = useRef(new Animated.Value(0)).current

    function expand()
    {
        Animated.sequence([
                Animated.timing(width, {toValue: screenWidth * 0.40, duration: 400, useNativeDriver: false}),
                Animated.parallel([
                Animated.timing(textOpacity, {toValue: 1, duration: 3000, useNativeDriver: true}),
                Animated.timing(scaleY, {toValue: 1, useNativeDriver: false, duration: 500})
                ])
            
        ]).start();
    }

    function collapse()
    {
        Animated.sequence([
                Animated.timing(width, {toValue: 0, duration: 600, useNativeDriver: false})
            ]).start(() => {
                width.setValue(0);
                scaleY.setValue(0.001);
                textOpacity.setValue(0);
                setReportShowing(false);
            });
    }

    function showPressedDiseaseReport(candidate)
    {
        setDiseaseCandidates(prev => ({...prev, "diseases": prev["diseases"].map(
            (disease) =>
            {
                if(disease.name === candidate)
                {
                    if(!disease["showReport"] && !reportShowing)
                    {
                        setReportShowing(true);
                        expand();
                    }
                    return {...disease, showReport: !disease["showReport"]};
                }
                else if(disease["showReport"])
                    return {...disease, showReport: false}
                return disease
        
            })}))
    }

    async function getGeminiOpinion()
    {
        if(!paragraph)
        {
            const response = await fetch("http://localhost:5000/geminiOpinion",
                {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({plant: "Alfalfa", symptoms: ["Black", "Brown"]})
                }
            );
            const data = await response.text();
            setParagraph(data);
        }
    }

    return (
        <>
            <Stack.Screen options={{headerShown: false}}/>        


            <View style={{backgroundColor: "#2b2b2b"}}>
                <Header />
            </View>
            <View style={{flexDirection: "row", height: "100%", justifyContent: "center", backgroundColor: "#2b2b2b", overflow: "visible"}}>
                <View style={{backgroundColor: "#ffffffa2", height: "90%", width: "30%", gap: 20, padding: 40, borderRadius: 8, marginTop: 20, boxShadow: '0px 5px 20px rgb(0, 0, 0)'}}>
                        
                        {/* top part of the report*/}
                        <View style={styles.container}>
                            <View style={{gap: 20}}>
                                <View style={{flexDirection: "row", justifyContent: "space-between", marginBottom: 20}}>
                                    <Text style={{fontSize: 16}}>Plant: Apple</Text>
                                    <View style={{flexDirection: "row"}}>
                                        <FontAwesome name="calendar" size={18} color="black" />
                                        <Text style={{fontSize: 16, marginLeft: 2}}>Date of Report: 2/20/26</Text>
                                    </View>
                                </View>
                                <View style={{flexDirection: "row", alignItems: "center"}}>
                                    <Text style={{fontSize: 16}}>Symptoms: </Text>
                                    <View style={{width: 14, height: 14, backgroundColor: "yellow", borderWidth: 1, marginRight: 2}}></View>
                                    <Text style={{fontSize: 16, marginRight: 10, }}>User Provided</Text>
                                    <View style={{width: 14, height: 14, backgroundColor: "orange", borderWidth: 1, marginRight: 2}}></View>
                                    <Text style={{fontSize: 16}}>AI Recognized</Text>
                                </View>
                                <View style={{flexDirection: "row", marginBottom: 10, gap: 5, flexWrap: "wrap", width: "70%"}}>
                                    <Text style={{fontSize: 16, backgroundColor: "yellow", padding: 8, borderRadius: 16}}>Yellow Leaves</Text>
                                    <Text style={{fontSize: 16, backgroundColor: "yellow", padding: 8, borderRadius: 16}}>Canker</Text>
                                    <Text style={{fontSize: 16, backgroundColor: "yellow", padding: 8, borderRadius: 16}}>Yellow Leaves</Text>
                                    <Text style={{fontSize: 16, backgroundColor: "orange", padding: 8, borderRadius: 16}}>Canker</Text>
                                    <Text style={{fontSize: 16, backgroundColor: "orange", padding: 8, borderRadius: 16}}>Cracks</Text>
                                </View>
                            </View>
                        </View>

                        {/* Possible Diseases Header */}
                        <Text style={{fontSize: 40, textAlign: "center", marginTop: 15}}>Possible Diseases</Text>


                        {/* disease candidates */}
                        <TouchableOpacity onPress={() => showPressedDiseaseReport("Apple Scab")}>
                            <View style={{flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 10, borderRadius: 4}}>
                                <View style={{flexDirection: "row", justifyContent: "space-between", flex: 1}}>
                                    <View style={{backgroundColor: "yellow", padding: 10, width: 50, height: 50, borderRadius: 25, justifyContent: "center", alignItems: "center", borderWidth: 3, borderColor: "#ffffff"}}>
                                        <Text style={{fontSize: 18}}>30%</Text>
                                    </View>
                                    <Text style={{fontSize: 30, textAlign: "center"}}>Apple Scab</Text>
                                </View>
                                {
                                    diseaseCandidates["diseases"][0]["showReport"] ? <Feather name="minus" size={40} color="black" /> : <Feather name="plus" size={40} color="black" />
                                }
                            </View>
                        </TouchableOpacity>

                        <TouchableOpacity onPress={() => showPressedDiseaseReport("Cedar-Apple Rust")}>
                            <View style={{flexDirection: "row", backgroundColor: "red", justifyContent: "space-between", alignItems: "center", padding: 10, borderRadius: 4}}>
                                <View style={{flexDirection: "row", alignItems: "center"}}>
                                    <View style={{backgroundColor: "yellow", padding: 10, width: 50, height: 50, borderRadius: 25, justifyContent: "center", alignItems: "center", borderWidth: 3, borderColor: "#ffffff"}}>
                                        <Text style={{fontSize: 18}}>20%</Text>
                                    </View>
                                    <Text style={{fontSize: 30, marginLeft: 5}}>Cedar-Apple Rust</Text>
                                </View>
                                {
                                    diseaseCandidates["diseases"][1]["showReport"] ? <FontAwesome5 name="minus-circle" size={40} color="black" /> : <FontAwesome6 name="circle-plus" size={40} color="black" />
                                }
                            </View>
                        </TouchableOpacity>

                        <TouchableOpacity onPress={() => {getGeminiOpinion(); showPressedDiseaseReport("gemini")}}>
                            <View style={{flexDirection: "row", backgroundColor: "red", justifyContent: "space-between", alignItems: "center", padding: 10, borderRadius: 4}}>
                                <View style={{flexDirection: "row", alignItems: "center"}}>
                                    <View style={{backgroundColor: "yellow", padding: 10, width: 50, height: 50, borderRadius: 25, justifyContent: "center", alignItems: "center", borderWidth: 3, borderColor: "#ffffff"}}>
                                        <Text style={{fontSize: 18}}>20%</Text>
                                    </View>
                                    <Text style={{fontSize: 30, marginLeft: 5}}>Get Gemini Second Opinion</Text>
                                </View>
                                {
                                    diseaseCandidates["diseases"][1]["showReport"] ? <FontAwesome5 name="minus-circle" size={40} color="black" /> : <FontAwesome6 name="circle-plus" size={40} color="black" />
                                }
                            </View>
                        </TouchableOpacity>
                </View>
                {
                    reportShowing &&
                            <Animated.View style={{backgroundColor: "#ffffffa2", gap: 30, height: screenHeight * 0.9, width, borderRadius: 8, marginTop: 20, marginLeft: 50, boxShadow: '0px 10px 30px #000000', transform: [{scaleY}]}}>
                                    <ScrollView>
                                        <View style={{margin: 40}}>
                                            <Markdown>{paragraph}</Markdown>
                                        </View>
                                    </ScrollView>
                            </Animated.View>
                }
                
                
            </View>
            
        </>
    )
}


const styles = StyleSheet.create({
    container: {
        flexDirection: "column",
        gap: 250,
        borderBottomWidth: 1,
        borderBottomColor: "black"
    }
});
