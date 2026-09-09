import { ThemeProvider } from './theme/ThemeProvider'
import ThemeDemo from './pages/ThemeDemo'

export default function App() {
  return (
    <ThemeProvider>
      <ThemeDemo />
    </ThemeProvider>
  )
}
