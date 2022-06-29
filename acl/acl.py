from dataclasses import dataclass, field
import os
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import re

URL = "https://aclanthology.org"


@dataclass
class Paper:
    id: str
    name: str
    code: str
    url: str = field(init=False)
    pdf: str = field(init=False)

    def __post_init__(self):
        self.url = f"{URL}/{self.id}"
        self.pdf = f"{self.url}.pdf"

    def download(self, path=str):
        if not os.path.exists(path):
            os.makedirs(path)
        name = re.sub(r'[/\\?%*:|\"<>\x7F\x00-\x1F]', '', self.name)
        filename = Path(f"{path}/{name}.pdf")
        file = requests.get(self.pdf).content
        filename.write_bytes(file)


@dataclass
class Anthology:
    id: str
    event: str
    name: str
    paper_count: int
    url: str = field(init=False)
    page: BeautifulSoup = field(
        init=False, default_factory=BeautifulSoup, repr=False)

    def __post_init__(self):
        self.url = f"{URL}/events/{self.event.lower()}/#{self.id}"

    def get_papers(self) -> list[Paper]:
        paper_list:list[Paper]=[]
        if len(self.page.contents) <= 0:
            self.page = BeautifulSoup(requests.get(
                self.url).content, "html.parser")
        papers = self.page.select(f"div[id='{self.id}'] > p")
        for paper in papers:
            info_tag = paper.select("span:nth-child(2) > strong > a")[0]
            id = info_tag.get("href").replace("/", "")
            name = info_tag.get_text()
            hasCode = paper.select(
                "span:nth-child(1) > a")[-1].get("title") == "Code"
            code = None
            if hasCode:
                code = paper.select("span:nth-child(1) > a")[-1].get("href")
            paper_list.append(Paper(id, name, code))
        return paper_list


@dataclass
class Event:
    venue: str
    year: int
    url: str = field(init=False)
    page: BeautifulSoup = field(
        init=False, default_factory=BeautifulSoup, repr=False)

    def __post_init__(self):
        self.url = f"{URL}/events/{self.venue.lower()}-{self.year}"

    def get_anthologies(self) -> list[Anthology]:
        anthology_list : list[Anthology] = []
        if len(self.page.contents) <= 0:
            self.page = BeautifulSoup(requests.get(
                self.url).content, "html.parser")
        anthologies = self.page.select("section ul li")
        for anthology in anthologies:
            a_tag = anthology.find("a")
            id = a_tag.get("href").replace("#", "")
            name = a_tag.get_text()
            papers_count = int(anthology.find(
                "span").get_text().strip().replace("paper", "").replace("s", ""))
            event = f"{self.venue}-{self.year}"
            anthology_list.append(Anthology(id, event, name, papers_count))
        return anthology_list

    def search_anthology(self, search_text: str) -> list[Anthology]:
        anthology_list : list[Anthology] = []
        if len(self.page.contents) <= 0:
            self.page = BeautifulSoup(requests.get(
                self.url).content, "html.parser")
        anthologies = self.page.select("section ul li")
        search_result = [anthology for anthology in anthologies if search_text in anthology.find("a").get_text()]
        for anthology in search_result:
            a_tag = anthology.find("a")
            id = a_tag.get("href").replace("#", "")
            name = a_tag.get_text()
            event = f"{self.venue}-{self.year}"
            papers_count = int(anthology.find(
                "span").get_text().strip().replace("paper", "").replace("s", ""))
            anthology = Anthology(id, event, name, papers_count)
            anthology_list.append(anthology)
        return anthology_list


@dataclass
class Venue:
    name: str
    url: str = field(init=False)
    page: BeautifulSoup = field(
        init=False, default_factory=BeautifulSoup, repr=False)

    def __post_init__(self):
        self.url = f"{URL}/venues/{self.name.lower()}"

    def get_all_events(self, start_year: int = None, end_year: int = None) -> list[Event]:
        if len(self.page.contents) <= 0:
            self.page = BeautifulSoup(requests.get(
                self.url).content, "html.parser")
        events_list = self.page.select('section  div[class="row"] h4 a')
        if start_year is not None and end_year is not None:
            return [Event(self.name, int(event.get_text())) for event in events_list if int(
                event.get_text()) >= start_year and int(event.get_text()) <= end_year]
        return [Event(self.name, int(e.get_text())) for e in events_list]

    def get_event(self, year: int) -> Event:
        if len(self.page.contents) <= 0:
            self.page = BeautifulSoup(requests.get(
                self.url).content, "html.parser")
        events_list = self.page.select('section  div[class="row"] h4 a')
        return next((Event(self.name, int(event.get_text())) for event in events_list if int(event.get_text()) == year), None)


@dataclass
class ACL:
    page: BeautifulSoup = field(
        init=False, default_factory=BeautifulSoup, repr=False)

    def get_venues(self) -> list[Venue]:
        if len(self.page.contents) <= 0:
            self.page = BeautifulSoup(requests.get(URL).content, "html.parser")
        venue_elements = self.page.select_one("table>tbody").select("tr>th>a")
        return [Venue(venue.text) for venue in venue_elements]

    def get_venue(self, venue_name: str) -> Venue:
        if len(self.page.contents) <= 0:
            self.page = BeautifulSoup(requests.get(URL).content, "html.parser")
        venue_elements = self.page.select_one("table>tbody").select("tr>th>a")
        return next(
            (Venue(venue.text) for venue in venue_elements if venue.text == venue_name), None)
