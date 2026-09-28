import { ItemTable } from './ItemTable'

export function StatusMessage({ loading, error, items }) {
	if (loading) {
		return <p>Loading market data...</p>
	}

	if (error) {
		return <p role="alert">{error}</p>
	}

	if (items.length === 0) {
		return <p>No Prime parts match your search.</p>
	}

	return <ItemTable items={items} />
}
