// app/_layout.tsx
import { Stack } from "expo-router";
import React, { ReactNode } from "react";
import { UserProvider } from "./UserContext";

interface RootLayoutProps {
  children: ReactNode; // ✅ explicitly type children
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <UserProvider>
      <Stack>
        {children}
      </Stack>
    </UserProvider>
  );
}
