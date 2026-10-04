import { createContext, useContext } from 'react'

export const AuthContext = createContext(null)

export function useAuth() {
  const contexte = useContext(AuthContext)
  if (!contexte) throw new Error('useAuth doit être utilisé dans AuthProvider.')
  return contexte
}
