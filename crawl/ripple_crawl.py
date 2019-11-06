import urllib.request
import urllib.parse
import ssl
import json

context = ssl._create_unverified_context()

start = '2019-07-01T06:00:00Z'
end = '2019-08-02T06:00:00Z'
limit = '1000'
marker = '20190701145301'
base_url = 'https://data.ripple.com/v2/payments/?'

file_dir = 'file/'

count = 1

while True:
    print("file ", count, " ... ")
    url = base_url + "start=" + start + "&end=" + end + '&limit=' + limit if marker == '' else \
        base_url + "start=" + start + "&end=" + end + '&limit=' + limit + '&marker=' + marker

    filename = file_dir + '0.html' if marker == '' else file_dir + marker + '.html'
    f = open(filename, 'x')

    print("url = ", url)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=context) as response:
        html = response.read()
    json_str = html.decode('utf-8')
    data = json.loads(json_str)
    marker_str = data['marker']
    markers = str.split(marker_str, '|')
    marker = markers[0]
    print("marker = ", data['marker'])
    f.write(json_str)
    f.close()
    count += 1
