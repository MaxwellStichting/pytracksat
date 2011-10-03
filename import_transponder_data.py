from BeautifulSoup import BeautifulSoup
import urllib2
import sys

page = 'http://www.amsat.org/amsat-new/satellites/frequencies.php'
html = urllib2.urlopen(urllib2.Request(page)).read()
soup = BeautifulSoup(html)
table = soup.findAll('table', {'align': 'center'})[0]
for tr in table.findAll('tr'):
    tds = tr.findAll('td')
    if (len(tds) < 5):
        continue
    if (len(tds) == 6):
        freq = tds[1].contents[0]
        name = tds[2].findAll('a')[0].contents[0]
        desc = tds[3].contents[0]
        modu = tds[4].contents[0]
        state = tds[5].contents[0]
    if (len(tds) == 5):
        freq = tds[0].contents[0]
        name = tds[1].findAll('a')[0].contents[0]
        desc = tds[2].contents[0]
        modu = tds[3].contents[0]
        state = tds[4].contents[0]
#    if (sys.argv[1] != name):
#        continue
    print "Name: %s"%(name)
    print "Freq: %s"%(freq)
    print "Modulation: %s"%(modu)
    print "Desc.: %s"%(desc)
    print "State: %s"%(state)

