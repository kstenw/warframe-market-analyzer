export function DataFreshness({ lastUpdated }) {
    if (!lastUpdated) {
        return null
    }

    return (
        <div>
            <p>Last updated: {lastUpdated}</p>
        </div>
    )
}
