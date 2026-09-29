import { useEffect, useState } from 'react'
import { fetchItems } from '../api/items'

export function useItems({ search, sort, order }) {
	const [items, setItems] = useState([])
	const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [lastUpdated, setLastUpdated] = useState(null)

	useEffect(() => {
		let isCurrentRequest = true
		const trimmedSearch = search.trim()

		if (trimmedSearch.length < 3) {
			setItems([])
			setError('')
			setLastUpdated(null)
			setLoading(false)
			return () => {
				isCurrentRequest = false
			}
		}

		async function loadItems() {
			setLoading(true)
			setError('')

			try {
				const data = await fetchItems({
					search: trimmedSearch,
					sort,
					order,
				})

				if (!isCurrentRequest) {
					return
				}

				setItems(data.items)
				setLastUpdated(data.lastUpdated)
			} catch (requestError) {
				if (isCurrentRequest) {
					setError(requestError.message)
				}
			} finally {
				if (isCurrentRequest) {
					setLoading(false)
				}
			}
		}

		loadItems()

		return () => {
			isCurrentRequest = false
		}
	}, [search, sort, order])

    return { items, loading, error, lastUpdated }
}
