'use client'

import React from 'react'
import { GoogleOAuthProvider } from '@react-oauth/google'

export interface GoogleAuthProviderProps {
  children: React.ReactNode
}

export function GoogleAuthProvider({ children }: GoogleAuthProviderProps) {
  const clientId =
    process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ||
    '1092837465-wealify-demo-google-oauth-client-id.apps.googleusercontent.com'

  return <GoogleOAuthProvider clientId={clientId}>{children}</GoogleOAuthProvider>
}
