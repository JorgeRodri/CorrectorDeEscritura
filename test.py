import requests

request_template = 'http://www.ivoox.com/{0}_sb.html'
search_terms = 'wololo'

r = requests.get(request_template.format(search_terms))
