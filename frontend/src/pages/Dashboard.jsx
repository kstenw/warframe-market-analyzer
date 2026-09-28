import { useEffect, useState } from 'react'
import { fetchItems } from '../api/items'
import { DashboardControls } from '../components/DashboardControls'
import { StatusMessage } from '../components/StatusMessage'
import { DataFreshness } from '../components/DataFreshness'

export default function Dashboard() {
	const [items, setItems] = useState([])
	const [search, setSearch] = useState('')
	const [sort, setSort] = useState('name')
	const [order, setOrder] = useState('asc')
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState('')
	const [lastUpdated, setLastUpdated] = useState(null)

	useEffect(() => {
		let isCurrentRequest = true

		async function loadItems() {
			setLoading(true)
			setError('')

			try {
				const data = await fetchItems({ search, sort, order })

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

	return (
		<main>
			<h1>Prime Part Market</h1>

			<DashboardControls
				search={search}
				setSearch={setSearch}
				sort={sort}
				setSort={setSort}
				order={order}
				setOrder={setOrder}
			/>
            
			<StatusMessage loading={loading} error={error} items={items} />
			
            <DataFreshness lastUpdated={lastUpdated} />
		</main>
	)
}
