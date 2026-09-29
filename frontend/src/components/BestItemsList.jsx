export function BestItemsList({ items = [] }) {
  const rankedItems = [...items]
    .map((item) => {
      const averagePrice = Number(item.average_price ?? item.lowest_price)
      const ducats = Number(item.ducats ?? 0)
      const apiRatio = Number(item.ducats_per_platinum)
      const ducatsPerPlatinum = apiRatio > 0
        ? apiRatio
        : averagePrice > 0
          ? ducats / averagePrice
          : 0

      return {
        ...item,
        average_price: averagePrice,
        ducats_per_platinum: ducatsPerPlatinum,
      }
    })
    .filter((item) => item.ducats_per_platinum > 0)
    .sort((a, b) => b.ducats_per_platinum - a.ducats_per_platinum)
    .slice(0, 5)

  return (
    <div className="chart-card">
      <div className="chart-header-row">
        <div>
          <h2>Best buys by ducat value</h2>
        </div>
      </div>

      <ul className="best-items-list">
        {rankedItems.map((item, index) => (
          <li key={item.slug || index}>
            <div className="best-item-name-block">
              <span className="best-item-rank">{index + 1}.</span>
              <strong>{item.name || 'Unknown item'}</strong>
            </div>

            <div className="best-item-meta">
              <span>{item.ducats ?? 0} ducats</span>
              <span>{Number(item.average_price ?? 0).toFixed(1)} plat</span>
              <span>{Number(item.ducats_per_platinum ?? 0).toFixed(2)} ducat/plat</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
