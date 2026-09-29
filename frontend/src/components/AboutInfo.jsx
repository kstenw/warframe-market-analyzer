export function AboutInfo() {
  return (
    <div className="about-layout">
      <section className="about-section">
        <div>
          <p>
            I built this project to make Warframe trading data easier to scan and compare at a glance. 
            The goal is to turn noisy market snapshots into clear signals for pricing trends and strong deals.
          </p>
        </div>
      </section>

      <section className="about-section">
        <h3>What this dashboard helps with</h3>
        <ul>
          <li>Quickly search prime parts by name</li>
          <li>Spot pricing changes over time</li>
          <li>Compare item value without digging through multiple pages</li>
          <li>Focus on high-signal trades before they disappear</li>
        </ul>
      </section>

      <section className="about-section">
        <h3>Why it exists</h3>
        <p>
          This app is meant to be a lightweight market analyzer for players who want a cleaner, more focused
          overview of the market without sorting through cluttered listings and repeated checks.
        </p>
      </section>
    </div>
  )
}
