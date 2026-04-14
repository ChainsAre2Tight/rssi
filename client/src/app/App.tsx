import { useEffect } from "react"
import AppLayout from "../components/Layout/AppLayout"
import { useAppStore } from "../store/useAppStore"
import ThemeToggle from "../components/ThemeToggle/ThemeToggle"
import { fetchMeasurements } from "../services/measurements"
import { adaptMeasurements } from "../features/measurements/adapter"

export default function App() {
  const setMeasurements = useAppStore(s => s.setMeasurements)
  const setLoading = useAppStore(s => s.setMeasurementsLoading)

  useEffect(() => {
    let mounted = true

    async function load() {
      try {
        setLoading(true)

        const res = await fetchMeasurements()
        const adapted = adaptMeasurements(res.measurements)

        if (!mounted) return
        setMeasurements(adapted)

      } catch (err) {
        console.error("Failed to load measurements", err)
      } finally {
        if (mounted) setLoading(false)
      }
    }

    load()

    return () => {
      mounted = false
    }
  }, [])

  return (
    <>
      <AppLayout />
      <ThemeToggle />
    </>
  )
}