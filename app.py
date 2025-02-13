import os
from flask import Flask, jsonify
from scrapper import NoticeScraper  # Import the scraper class from scrapper.py

app = Flask(__name__)

# Initialize the scraper instance
scraper = NoticeScraper()

@app.route('/api/notices', methods=['GET'])
def get_notices():
    """
    Endpoint to get all the scraped notices
    """
    notices = scraper.scrape_notices()  # Scrape the notices
    return jsonify(notices), 200  # Return notices as JSON response

if __name__ == '__main__':
    # Use the port from the environment variable, or default to 5000 for local development
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)  # Use dynamic port binding
