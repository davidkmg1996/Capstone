import { useState } from "react";
import { Image, View, Text, Pressable } from "react-native";
import MaterialIcons from '@expo/vector-icons/MaterialIcons';

export default function SymptomImage({ uri, fileName, symptomImagesUri, setSymptomImagesUri })
{
    const [remove, setRemove] = useState(false);

    function del()
    {
        return setSymptomImagesUri(symptomImagesUri.filter(imageUri => imageUri.uri != uri));
    }
    return (
        <>
            {
                <View style={{position: "relative", paddingLeft: 10, paddingTop: 10}} onMouseEnter={() => setRemove(true)} onMouseLeave={() => setRemove(false)}>
                    {
                        remove &&
                            <Pressable style={{ position: "absolute", top: 2, left: 2, zIndex: 10 }} onPress={() => del()}>
                                <MaterialIcons name="cancel" size={22} color="black" />
                            </Pressable>
                    }
                    <Image source={{ uri: uri }} style={{ width: 160, height: 160, borderRadius: 2 }} />
                    <Text>{fileName}</Text>
                </View>
            }
        </>
    )
}