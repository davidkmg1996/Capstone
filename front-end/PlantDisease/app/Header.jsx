import { Pressable, View, Text, StyleSheet } from "react-native";

export default function Header()
{
    return (
        <View style={styles.wrapper}>
            <Pressable>
                <Text style={{marginLeft: 20, fontSize: 16, color: "#dddddd"}}>Home</Text>
            </Pressable>

            <View style={{flexDirection: "row", padding: 20, gap: 20}}>
                <Pressable>
                    <View style={{}}>
                        <Text style={styles.link}>Sign Up</Text>
                    </View>    
                </Pressable>

                <Pressable>
                    <View style={{}}>
                        <Text style={styles.link}>Login</Text>
                    </View>    
                </Pressable>
            </View>
        </View> 
    );
}

const styles = StyleSheet.create({
    wrapper:
    {
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "center"
    },

    link:
    {
        fontSize: 16,
        color: "white"
    }
});