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
          <li>Quickly search prime parts by name for organized info</li>
          <li>Provides recommendations for selling items based on ducat-plat value</li>
          <li>Compare item value without digging through multiple pages</li>
          <li>Determine the best time to sell items based on market trends</li>
        </ul>
      </section>

      <section className="about-section">
        <h3>Calculations</h3>
        <p>
          This app is meant to be a lightweight market analyzer for players who want a current, more focused
          overview of the market without sorting through cluttered listings. Rather than using the Weighted 
          Average like the Warframe Market API, I calculated the average price of the top 4 cheapest current 
          orders for each item. This is meant to give a more accurate representation of the current market 
          value of an item without being skewed by outliers or old listings.
        </p>
        <p>
          The ducats per platinum ratio is calculated by dividing the ducat value by its average (top 4) price. 
          This ratio is used to determine a recommendation to users on whether to sell an item for ducats or for 
          platinum. The current thresholds for this recommendation are 8 ducats per platinum for items with less 
          than 100 ducats, and 10 ducats per platinum for items with 100 or more ducats. These thresholds are 
          based on the current market trends and may be adjusted in the future as the market evolves.
        </p>
      </section>
      <section className="about-section">
        <h3>Next Steps</h3>
        <ul>
          <li>Implement a dropdown menu for selecting different time periods (ex. last 7 days, 30 days)</li>
          <li>Add support for custom user-defined thresholds for recommendations</li>
          <li>Include historical data visualization</li>
          <li>Add inventory snapshot feature to easily determine current inventory status</li>
        </ul>
      </section>
    </div>
  )
}
