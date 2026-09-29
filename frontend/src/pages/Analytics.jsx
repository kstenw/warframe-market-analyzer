import { useEffect, useState } from 'react'
import {
  fetchAnalyticsBestBuys,
  fetchMarketHours,
} from '../api/items'
import { BestItemsList } from '../components/BestItemsList'
import { HourlyMarketChart } from '../components/HourlyMarketChart'

export default function AnalyticsPage() {
  const [bestBuys, setBestBuys] = useState([])
  const [hours, setHours] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadAnalytics() {
      setLoading(true)
      setError('')

      try {
        const [bestBuysResult, marketHoursResult] = await Promise.allSettled([
          fetchAnalyticsBestBuys(30, 5),
          fetchMarketHours(30, 10),
        ])

        if (!active) return

        if (bestBuysResult.status === 'fulfilled') {
          setBestBuys(bestBuysResult.value.items || [])
        } else {
          setBestBuys([])
        }

        if (marketHoursResult.status === 'fulfilled') {
          setHours(marketHoursResult.value.hours || [])
        } else {
          setHours([])
        }

        const failedRequests = [bestBuysResult, marketHoursResult].filter(
          (result) => result.status === 'rejected',
        )

        if (failedRequests.length > 0 && !bestBuysResult.value && !marketHoursResult.value) {
          setError(failedRequests[0].reason?.message || 'Market analytics are temporarily unavailable.')
        }
      } catch (requestError) {
        if (!active) return
        setError(requestError.message || 'Market analytics are temporarily unavailable.')
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    loadAnalytics()

    return () => {
      active = false
    }
  }, [])

  return (
    <main className="page page-analytics">
      <div className="page-header">
        <h1>Market overview</h1>
        <p className="page-subtitle">
          Price spread and trading windows for the current market cycle.
        </p>
      </div>

      {loading ? (
        <p>Loading analytics…</p>
      ) : (
        <>
          {error && <p role="alert">{error}</p>}

          <section className="analytics-grid">
            <HourlyMarketChart hours={hours} />
            <BestItemsList items={bestBuys} />
          </section>
        </>
      )}
    </main>
  )
}
