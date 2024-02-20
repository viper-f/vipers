from bs4 import BeautifulSoup

from intellect.Intellect import Intellect
from intellect.models import Page


class Trainer:
    def __init__(self):
        self.intellect = Intellect()

    def form_dataset(self, crawl_session_id):
        pages = Page.objects.filter(control_session_id=crawl_session_id)
        dataset = []
        labels = []
        for page in pages:
            f = open(page.file_path, "r", encoding="windows-1251")
            content = f.read()
            data = self.intellect.analize(content, True)

            if page.corrected_topic_id is not None:
                id = page.corrected_topic_id
            else:
                id = page.automatic_topic_id
            y = self.find_label(content, id, page.domain)
            if y:
                dataset.append(data)
                labels.append(y)
        #todo

    def find_label(self, html_text, id, domain):
        url = domain + '/viewtopic.php?id='+str(id)
        soup = BeautifulSoup(html_text, 'html.parser')
        label_vector = []
        found = False
        n = 0
        for line in soup.css.select('tbody tr'):
            if n >= 20:
                break
            topic = line.css.select('.tcl>a')[0]
            if topic['href'] == url:
                found = True
                label_vector.append(1)
            else:
                label_vector.append(0)
            n += 1
        return found, label_vector