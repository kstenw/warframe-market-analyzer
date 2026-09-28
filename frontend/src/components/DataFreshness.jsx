export function DataFreshness({ lastUpdated }) {
    return (
        <div>
            {lastUpdated && <p>Last updated: {lastUpdated}</p>}
        </div>
    )
}
