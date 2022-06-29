
OOP based system for scraping https://aclanthology.org/

# Usage example:
```python
from acl.acl import ACL

acl = ACL();
acl_venue = acl.get_venue("ACL")
events = acl_venue.get_all_events(2016, 2021)
long_papers_2021 = events[0].search_anthology("Long")[0].get_papers()
```