# keeping this a seperate file because i hate you
from sah_const import *
import types
def generate_settings():
    # i couldnt just delete it
    # f = open('sah_const.py', 'r').readlines();
    # varnames = [a.replace(' ', '').split('=')[0] for a in f if not a.startswith('#') and a != '\n']

    # this isnt much better
    settings = { k: v for k, v in globals().iteritems() if '__' not in k and type(v) is str or type(v) is int}
    settings_str = 'var settings = ' + repr(settings).replace('\'', '"') + ";"

    open('web/static/settings.js', 'w').write(settings_str);
    return settings_str
