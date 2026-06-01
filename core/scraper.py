import requests
from bs4 import BeautifulSoup

def get_mostaql_jobs():
    url = "https://mostaql.com/projects"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    jobs = []
    # هنا نحدد الـ CSS Selectors الخاصة بالمشاريع في موقع مستقل
    project_cards = soup.select('.project-link') 
    for card in project_cards[:5]: # جلب أحدث 5 مشاريع
        title = card.text.strip()
        jobs.append(title)
    return jobs
