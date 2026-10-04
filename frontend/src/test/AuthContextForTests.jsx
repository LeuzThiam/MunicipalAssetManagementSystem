import { AuthContext } from '../context/auth'

export function AuthContextForTests({ value, children }) {
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
