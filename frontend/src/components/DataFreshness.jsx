export function DataFreshness({ lastUpdated }) {
    if (!lastUpdated) {
        return null
    }

    const updatedAt = new Date(lastUpdated)
    const formattedDate = Number.isNaN(updatedAt.getTime())
        ? lastUpdated
        : updatedAt.toLocaleString(undefined, {
            dateStyle: 'medium',
            timeStyle: 'short',
        })

    return (
        <div>
            <p>Last updated: {formattedDate}</p>
        </div>
    )
}
