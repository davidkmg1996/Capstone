module.exports = function (api) {
  api.cache(true);
  return {
    presets: ["babel-preset-expo"],
    plugins: [
      "expo-router/babel",
      // If you use Reanimated, keep this LAST:
      // "react-native-reanimated/plugin",
    ],
  };
};
