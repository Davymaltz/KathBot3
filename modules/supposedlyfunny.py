import xml.dom.minidom as dom
import urllib2
from locale import format as format_number
from datetime import datetime
from xml.sax.saxutils import unescape
import re
import random

COMMANDS = frozenset(('fml', 'bash', 'foon'))

def init():
    add_hook('privmsg', privmsg)

def privmsg(irc, origin, args):
    irch = m('irc_helpers')
    target, command, args = irch.parse(args)
    if command not in COMMANDS:
        return
    if command == 'fml':
        url = 'http://api.betacie.com/view/random/nocomment?key=readonly&language=en'
        if len(args) == 1:
            try:
                fmlid = int(args[0])
                url = 'http://api.betacie.com/view/%s/nocomment?key=readonly&language=en' % fmlid
            except:
                pass
        try:
            f = urllib2.urlopen(url)
            xml = f.read()
            f.close()
            xml = dom.parseString(xml)
            item = xml.getElementsByTagName('item')[0]
            author = item.getElementsByTagName('author')[0].firstChild.data
            content = item.getElementsByTagName('text')[0].firstChild.data
            fmlid = item.getAttribute('id')
            agree = int(item.getElementsByTagName('agree')[0].firstChild.data)
            deserved = int(item.getElementsByTagName('deserved')[0].firstChild.data)
            #published = datetime.strptime(item.getElementsByTagName('date')[0].firstChild.data[:-6], '%Y-%m-%dT%H:%M:%S')
        except:
            irch.message(irc, target, "Couldn't load item.")
            return
        
        irch.message(irc, target, "~B[FML]~B ~UFML ~B#%s~B from ~B%s~B~U" % (fmlid, author))
        irch.message(irc, target, "~B[FML]~B %s" % content)
        irch.message(irc, target, "~B[FML]~B Agree: ~B%s~B | Disagree: ~B%s~B" % (format_number('%i', agree, True), format_number('%i', deserved, True)))
    elif command == 'bash':
        # With thanks to Davy. <3
        try:
            f = urllib2.urlopen('http://www.bash.org/?random1')
            data = f.read()
            f.close()
            quotes = re.findall('<p class="quote"><a href="(.+?)".*?</p><p class="qt">(.+?)</p>', data, re.S)
            quote = random.choice(quotes)
            lines = unescape(quote[1].replace('<br />','')).split('\n')
        except urllib2.HTTPError:
            irch.message(irc, target, "~B[bash]~B Couldn't find a quote. D:")
            return
        irch.message(irc,target,'~B[bash]~B ~UFrom: http://www.bash.org/%s~U' % quote[0])
        for line in lines:
            irch.message(irc,target,'~B[bash]~B %s' % line)
    elif command == 'foon':
        # Davy here! O: 7-21-09
        try:
            handle = urllib2.urlopen('http://www.foon.co.uk/')
            data = handle.read()
            phrase = re.findall("<div id='subtitle'>(.+?)</div>", data, re.S)
            phrase = phrase[0]
            irch.message(irc,target,'~B[foon]~B ~U%s~U' % phrase)
        except urllib2.HTTPError:
            irch.message(irc,target,'~B[foon]~B There was an error fetching a title message from foon.co.uk!')
