from fnmatch import fnmatch
from irc import User

def init():
    add_hook('privmsg', privmsg)
    
def privmsg(irc, origin, args):
    irc_helpers = m('irc_helpers')
    target, command, args = irc_helpers.parse(args)
    if command == 'access':
        canon = get_canonical_nick(origin.nick)
        access = get_user_access(origin)
        m('irc_helpers').message(irc, target, "Access for %s (%s) is level %s" % (canon, origin, access))
        

def get_canonical_nick(nick):
    results = m('datastore').query("SELECT canon FROM aliases WHERE alias = ?", nick)
    if not results:
        return nick
    return results[0][0]

def get_user_access(user):
    nick = get_canonical_nick(user.nick)
    results = m('datastore').query("SELECT id, level FROM users WHERE nick = ?", nick)
    if not results:
        return 1
    
    level = results[0][1]
    uid = results[0][0]
    hosts = m('datastore').query("SELECT host FROM hosts WHERE uid = ? AND (expires < DATETIME() OR expires IS NULL)", uid)
    for host in hosts:
        if fnmatch(user.hostname, host[0]):
            return level
    
    return 1
    
def get_command_access(command):
    results = m('datastore').query("SELECT level FROM command_access WHERE command = ?", command)
    if not results:
        return 1
    return results[0][0]
    
def check_action_permissible(user, command):
    return get_user_access(user) >= get_command_access(command)