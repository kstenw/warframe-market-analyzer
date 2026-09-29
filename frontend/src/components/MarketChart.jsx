export function MarketChart({ items = [] }) {
  const chartData = items.length
    ? items.map((item) => ({
        label: item.name || 'Unknown',
        value: Number(item.average_price ?? item.platinum_per_ducat ?? 0),
      }))
    : [{ label: 'No data', value: 0 }]

  const width = 720
  const height = 260
  const padding = 28
  const values = chartData.map((point) => point.value)
  const minValue = Math.min(...values, 0)
  const maxValue = Math.max(...values, 1)
  const range = maxValue - minValue || 1

  const points = chartData.map((point, index) => {
    const x = padding + (index * (width - padding * 2)) / Math.max(chartData.length - 1, 1)
    const y = height - padding - ((point.value - minValue) / range) * (height - padding * 2)
    return { ...point, x, y }
  })

  const linePath = points
    .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
    .join(' ')

  const areaPath = `${linePath} L ${points[points.length - 1].x} ${height - padding} L ${points[0].x} ${height - padding} Z`

  return (
    <div className="chart-card">
      <div className="chart-header-row">
        <div>
          <p className="eyebrow">PRICE TREND</p>
          <h2>Recent market movement</h2>
        </div>
        <span className="chart-pill">Live data</span>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Market price trend chart" className="market-chart">
        <defs>
          <linearGradient id="areaFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="rgba(231, 184, 92, 0.55)" />
            <stop offset="100%" stopColor="rgba(231, 184, 92, 0.05)" />
          </linearGradient>
        </defs>

        {[0, 1, 2, 3].map((line) => {
          const y = padding + (line * (height - padding * 2)) / 3
          return <line key={line} x1={padding} x2={width - padding} y1={y} y2={y} className="grid-line" />
        })}

        <path d={areaPath} fill="url(#areaFill)" />
        <path d={linePath} fill="none" stroke="var(--accent)" strokeWidth="3" strokeLinecap="round" />

        {points.map((point) => (
          <g key={point.label}>
            <circle cx={point.x} cy={point.y} r="5" fill="var(--panel-bg)" stroke="var(--accent)" strokeWidth="2" />
            <text x={point.x} y={height - 8} textAnchor="middle" className="chart-label">
              {point.label.length > 8 ? `${point.label.slice(0, 8)}...` : point.label}
            </text>
          </g>
        ))}
      </svg>

      <ul className="chart-legend">
        {chartData.map((point) => (
          <li key={point.label}>
            <span className="legend-dot" aria-hidden="true" />
            {point.label}: {Number(point.value).toFixed(1)} plat
          </li>
        ))}
      </ul>
    </div>
  )
}
