import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

class NoticeScraper:
    def __init__(self):
        self.url = "https://daffodilvarsity.edu.bd/noticeboard"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def parse_date(self, date_text):
        """Convert date text to ISO format"""
        try:
            date_obj = datetime.strptime(date_text, "%dth %B %Y")
            return date_obj.isoformat()
        except:
            try:
                date_obj = datetime.strptime(date_text.replace('rd ', 'th '), "%dth %B %Y")
                return date_obj.isoformat()
            except:
                try:
                    date_obj = datetime.strptime(date_text.replace('st ', 'th '), "%dth %B %Y")
                    return date_obj.isoformat()
                except:
                    try:
                        date_obj = datetime.strptime(date_text.replace('nd ', 'th '), "%dth %B %Y")
                        return date_obj.isoformat()
                    except:
                        return None

    def scrape_notices(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            notices = []

            notice_items = soup.find_all('div', class_='row full-notice mb-2')

            for item in notice_items:
                try:
                    link_element = item.find('a', class_='noticeFile')
                    title = link_element.text.strip() if link_element else "No Title"
                    link = link_element.get('onclick', '') if link_element else ""

                    if 'myFunction' in link:
                        notice_id = link.split('(')[1].split(',')[0]
                        link = f"https://daffodilvarsity.edu.bd/notice/{notice_id}"
                    else:
                        link = "#"

                    department_div = item.find('div', class_='col-md-5')
                    department = department_div.text.strip() if department_div else "General"

                    date_div = item.find('div', class_='col-md-3')
                    date_text = date_div.text.strip() if date_div else "No Date"
                    if 'calendar-alt' in date_text:
                        date_text = date_text.split('calendar-alt')[-1].strip()

                    iso_date = self.parse_date(date_text)

                    notice = {
                        'title': title,
                        'link': link,
                        'department': department,
                        'date': date_text,
                        'timestamp': iso_date
                    }
                    notices.append(notice)
                    logging.debug(f"Successfully parsed notice: {notice}")

                except Exception as e:
                    logging.error(f"Error parsing notice item: {str(e)}")
                    continue

            return notices

        except requests.RequestException as e:
            logging.error(f"Error fetching notices: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return []

# Flask API file (app.py)
from flask import Flask, jsonify
from scrapper import NoticeScraper

app = Flask(__name__)

scraper = NoticeScraper()

@app.route('/notices', methods=['GET'])
def get_notices():
    notices = scraper.scrape_notices()
    return jsonify(notices)

if __name__ == '__main__':
    app.run(debug=True)
