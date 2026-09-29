import { useState } from 'react'
import { useItems } from '../hooks/useItems'
import { DashboardControls } from '../components/DashboardControls'
import { StatusMessage } from '../components/StatusMessage'
import { DataFreshness } from '../components/DataFreshness'

export default function Dashboard() {
	// State variables for search, sort, and order.
	const [search, setSearch] = useState('')
	const [sort, setSort] = useState('name')
	const [order, setOrder] = useState('asc')

	// Fetch items based on the current search, sort, and order state.
	const { items, loading, error, lastUpdated } = useItems({ search, sort, order })

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
            
			<StatusMessage
				loading={loading}
				error={error}
				items={items}
				hasSearched={search.trim().length >= 3}
			/>
			
            <DataFreshness lastUpdated={lastUpdated} />
		</main>
	)
}
