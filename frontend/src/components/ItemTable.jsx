export function ItemTable({ items }) {
    const getPlatinumTrigger = (ducats) => {
        return ducats >= 100 ? 10 : 8
    }

    const getSellRecommendation = (item) => {
        const lowestPrice = Number(item.lowest_price ?? item.average_price)
        const ducats = Number(item.ducats)

        if (!Number.isFinite(lowestPrice) || lowestPrice <= 0 || !Number.isFinite(ducats)) {
            return 'Unknown'
        }

        const platinumTrigger = getPlatinumTrigger(ducats)

        if (lowestPrice < platinumTrigger) {
            return 'Ducats'
        }

        return 'Plat'
    }

    return (
        <div className="results-panel">
            <table className="results-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Lowest Price</th>
                        <th>Average Price</th>
                        <th>Ducats</th>
                        <th>Sell for</th>
                    </tr>
                </thead>
                <tbody>
                    {items.map((item) => (
                        (() => {
                            const displayPrice = item.lowest_price ?? item.average_price
                            const sellRecommendation = getSellRecommendation(item)

                            return (
                        <tr key={item.slug}>
                            <td>{item.name}</td>
                            <td>
                                {displayPrice == null
                                    ? 'No price'
                                    : `${displayPrice} platinum`}
                            </td>
                            <td>
                                {item.average_price === null
                                    ? 'No price'
                                    : `${item.average_price} platinum`}
                            </td>
                            <td>{item.ducats}</td>
                            <td className={`sell-recommendation sell-${sellRecommendation.toLowerCase()}`}>
                                {sellRecommendation}
                            </td>
                        </tr>
                            )
                        })()
                    ))}
                </tbody>
            </table>
        </div>
    )
}
