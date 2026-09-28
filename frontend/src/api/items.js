const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

async function request(path) {
	const controller = new AbortController()
	const timeoutId = setTimeout(() => controller.abort(), 8000)

	let response
	try {
		response = await fetch(`${API_URL}${path}`, {
			signal: controller.signal,
		})
	} catch (error) {
		if (error.name === 'AbortError') {
			throw new Error('The market API timed out. Check that PostgreSQL is running.')
		}

		throw error
	} finally {
		clearTimeout(timeoutId)
	}

	if (!response.ok) {
		let message = `Request failed with status ${response.status}`

		try {
			const error = await response.json()
			message = error.detail || message
		} catch {
			// Keep the HTTP error when the server does not return JSON.
		}

		throw new Error(message)
	}

	return response.json()
}

export async function fetchItems({
	search = '',
	sort = 'name',
	order = 'asc',
	limit = 50,
	offset = 0,
} = {}) {
	const params = new URLSearchParams({
		search,
		sort,
		order,
		limit: String(limit),
		offset: String(offset),
	})

	return request(`/api/items?${params.toString()}`)
}

export function fetchItem(slug) {
	return request(`/api/items/${encodeURIComponent(slug)}`)
}

export function fetchItemHistory(slug, days = 30) {
	const params = new URLSearchParams({ days: String(days) })
	return request(
		`/api/items/${encodeURIComponent(slug)}/history?${params.toString()}`,
	)
}

export function fetchApiStatus() {
	return request('/api/status')
}
