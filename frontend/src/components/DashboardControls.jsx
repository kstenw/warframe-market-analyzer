export function DashboardControls({search, setSearch, sort, setSort, order, setOrder}) {
	return (
		<div>
            {/* Input field for searching items */}
			<input
				type="search"
				value={search}
				onChange={(event) => setSearch(event.target.value)}
				placeholder="Search Prime parts"
			/>

            {/* Dropdown for sorting items */}
			<select value={sort} onChange={(event) => setSort(event.target.value)}>
				<option value="name">Name</option>
				<option value="ducats">Ducats</option>
				<option value="price">Average price</option>
			</select>

            {/* Button for toggling the order of sorting (asc/desc) */}
			<button
				type="button"
				onClick={() => setOrder(order === 'asc' ? 'desc' : 'asc')}
			>
				{order === 'asc' ? 'Ascending' : 'Descending'}
			</button>
		</div>
	)
}
