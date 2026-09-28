export function ItemTable({ items }) {
    const formatDate = (value) => {
        if (!value) {
            return 'Unknown'
        }

        return new Date(value).toLocaleString()
    }

    return (
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Lowest Price</th>
                    <th>Average Price</th>
                    <th>Ducats</th>
                </tr>
            </thead>
            <tbody>
                {items.map((item) => (
                    <tr key={item.slug}>
                        <td>{item.name}</td>
                        <td>
                            {item.lowest_price === null
                                ? 'No price'
                                : `${item.lowest_price} platinum`}
                        </td>
                        <td>
                            {item.average_price === null
                                ? 'No price'
                                : `${item.average_price} platinum`}
                        </td>
                        <td>{item.ducats}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    )
}
