from flask import Flask, jsonify, render_template
import os
from automatic_df_news_fetching import scrape_keyword, setup_driver, KEYWORDS_WITH_PAGES
from datetime import datetime, timedelta
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='news_scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def index():
    """Render a simple homepage."""
    return render_template('index.html')

@app.route('/scrape', methods=['GET'])
def scrape_news():
    """Run the scraper and return results as JSON."""
    try:
        # Date range
        end_date = datetime.today().strftime("%m/%d/%Y")
        start_date = (datetime.today() - timedelta(days=1)).strftime("%m/%d/%Y")
        logging.info(f"Starting scrape: {start_date} to {end_date}")

        # Initialize driver and results
        driver = setup_driver()
        all_data = []
        seen_links = set()

        # Scrape one page per keyword for demo (adjust for production)
        for keyword, num_pages in KEYWORDS_WITH_PAGES.items():
            data = scrape_keyword(driver, keyword, num_pages=1, start_date=start_date,
                                 end_date=end_date, seen_links=seen_links)
            all_data.extend(data)

        driver.quit()
        logging.info(f"Scrape completed: {len(all_data)} articles")
        return jsonify(all_data)

    except Exception as e:
        logging.error(f"Scrape failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)