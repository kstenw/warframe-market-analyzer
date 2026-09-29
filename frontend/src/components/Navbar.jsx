export function Navbar({ activePage, onNavigate }) {
	const navItems = [
		{ id: 'analytics', label: 'Analytics' },
		{ id: 'about', label: 'About' },
	]

	return (
		<header className="navbar">
			<button
				type="button"
				className="navbar-brand nav-button"
				onClick={() => onNavigate('dashboard')}
			>
				<span>Market Analyzer</span>
			</button>

			<nav aria-label="Primary navigation">
				{navItems.map((item) => (
					<button
						key={item.id}
						type="button"
						className={`nav-button ${activePage === item.id ? 'active' : ''}`}
						onClick={() => onNavigate(item.id)}
					>
						{item.label}
					</button>
				))}
			</nav>
		</header>
	)
}
