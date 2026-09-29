export function HourlyMarketChart({ hours = [] }) {
  const width = 760
  const height = 240
  const padding = 28

  const normalizedHours = hours
    .map((hour) => ({
      ...hour,
      hour_of_day: Number(hour.hour_of_day ?? 0),
      average_price: Number(hour.average_price ?? 0),
    }))
    .sort((a, b) => a.hour_of_day - b.hour_of_day)

  const prices = normalizedHours
    .map((entry) => entry.average_price)
    .filter((value) => Number.isFinite(value) && value >= 0)
  const rawMinValue = prices.length ? Math.min(...prices) : 0
  const rawMaxValue = prices.length ? Math.max(...prices) : 1
  const valueRange = Math.max(rawMaxValue - rawMinValue, 1)
  const chartMinValue = Math.max(0, rawMinValue - valueRange * 0.12)
  const chartMaxValue = rawMaxValue + valueRange * 0.12
  const chartRange = chartMaxValue - chartMinValue
  const bestHour = normalizedHours.reduce((best, current) => {
    if (!best || current.average_price < best.average_price) return current
    return best
  }, null)

  const points = normalizedHours.map((hour) => {
    const x = padding + ((hour.hour_of_day ?? 0) / 23) * (width - padding * 2)
    const y = height - padding - ((hour.average_price - chartMinValue) / chartRange) * (height - padding * 2)
    return { ...hour, x, y }
  })

  const linePath = points
    .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
    .join(' ')

  const yAxisTicks = [0, 1, 2, 3, 4].map((tick) => ({
    value: chartMaxValue - (tick / 4) * chartRange,
    y: padding + (tick / 4) * (height - padding * 2),
  }))

  return (
    <div className="chart-card">
      <div className="chart-header-row">
        <div>
          <h2>Best buy window</h2>
          <p className="chart-insight">
            Cheapest market hour: {bestHour ? `${bestHour.hour_of_day}:00` : 'No data'}
          </p>
        </div>
      </div>

      <div className="chart-with-axis">
        <div className="y-axis-labels numeric" aria-hidden="true">
          {yAxisTicks.map((tick) => (
            <span key={tick.value}>{tick.value.toFixed(1)}</span>
          ))}
        </div>

        <svg viewBox={`0 0 ${width} ${height}`} className="market-chart" role="img" aria-label="Hourly market price chart">
          {yAxisTicks.map((tick, index) => (
            <line key={index} x1={padding} x2={width - padding} y1={tick.y} y2={tick.y} className="grid-line" />
          ))}

          <path d={linePath} fill="none" stroke="var(--accent)" strokeWidth="3" strokeLinecap="round" />

          {points.map((point) => (
            <g key={point.hour_of_day}>
              <circle
                cx={point.x}
                cy={point.y}
                r={bestHour && point.hour_of_day === bestHour.hour_of_day ? 6 : 4}
                fill={bestHour && point.hour_of_day === bestHour.hour_of_day ? '#f4cf7c' : 'var(--accent)'}
              />
              {point.hour_of_day % 4 === 0 && (
                <text x={point.x} y={height - 8} textAnchor="middle" className="chart-label">
                  {point.hour_of_day}:00
                </text>
              )}
            </g>
          ))}
        </svg>
      </div>
    </div>
  )
}
