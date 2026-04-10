import { useEffect } from "react"
import AppLayout from "../components/Layout/AppLayout"
import { loadMockMeasurements } from "../features/measurements/mockMeasurements"
import { useAppStore } from "../store/useAppStore"

export default function App() {

  const setMeasurements = useAppStore((s) => s.setMeasurements)

  useEffect(() => {
      const data = loadMockMeasurements()
      setMeasurements(data)
  }, [])

  return <AppLayout />
}