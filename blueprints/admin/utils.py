from functools import wraps
from flask  import session, abort, url_for, request, redirect

from app import db
from .models import Admin, InstagramCookie, InstagramError

from instagram import InstagramLoginouter, Checker

def root_view(func):
        @wraps(func)
        def decorator(*args, **kwargs):
                if not session.get('adminID'):
                        return redirect(url_for('admin.login'))
                admin = Admin.query.filter(Admin.id == session['adminID']).first()
                if admin.role_name() not in ['root']:
                        return redirect(url_for('admin.dashboard'))
                return func(*args, **kwargs)
        return decorator

def admin_view(func):
        @wraps(func)
        def decorator(*args, **kwargs):
                if not session.get('adminID'):
                        return redirect(url_for('admin.login'))
                admin = Admin.query.filter(Admin.id == session['adminID']).first()
                if admin.role_name() not in ['root', 'admin']:
                        return redirect(url_for('admin.dashboard'))
                return func(*args, **kwargs)
        return decorator

def viewer_view(func):
        @wraps(func)
        def decorator(*args, **kwargs):
                if not session.get('adminID'):
                        return redirect(url_for('admin.login'))
                admin = Admin.query.filter(Admin.id == session['adminID']).first()
                if admin.role_name() not in ['root', 'admin', 'viewer']:
                        return redirect(url_for('admin.dashboard'))
                return func(*args, **kwargs)
        return decorator

def banned_view(func):
        @wraps(func)
        def decorator(*args, **kwargs):
                if not session.get('adminID'):
                        return redirect(url_for('admin.login'))
                admin = Admin.query.filter(Admin.id == session['adminID']).first()
                if admin.role_name() not in ['root', 'admin', 'viewer', 'banned']:
                        return redirect(url_for('admin.dashboard'))
                return func(*args, **kwargs)
        return decorator



def get_browser(cookie):
    return InstagramLoginouter(cookie=cookie)

def get_screen_browser():
    global insta
    if 'insta' in globals():
        try: return 'data:image/png;base64, '+ insta.screen()
        except: pass
    return None

def del_browser():
    global insta
    if 'insta' in globals():
        del insta
        return True
    return False

def update_instagram_cookie(cookie):
    instagram_cookie = InstagramCookie()
    instagram_cookie.set_cookie(cookie)
    db.session.add(instagram_cookie)
    db.session.commit()

    return cookie

def get_instagram_cookie():
    instagram_cookie = InstagramCookie.query.order_by(InstagramCookie.id.desc()).first()
    return instagram_cookie.get_cookie() if instagram_cookie else None

def get_instagram_status(cookie):
    try:
        response, instagram_status = Checker(cookie)
    except Exception as e:
        instagram_status = {'country':None, 'userid':None}
        response = FakeInstagramResponse('Checker()', None, str(e))

    if response.status_code != 200 or not instagram_status['country']:
        instagram_status['color'] = 'error'

        instagram_error = InstagramError()
        instagram_error.url = response.url
        instagram_error.status_code = response.status_code
        instagram_error.text = response.text

        db.session.add(instagram_error)
        db.session.commit()
    elif not instagram_status['userid']:
        instagram_status['color'] = 'warning'
    else:
        instagram_status['color'] = ''

    return instagram_status

def get_instagram_stage(instagram_status, istage):
    if instagram_status['color'] == 'error':
        istage = 'error'
    elif instagram_status['color'] == 'warning':
        if istage != 'verify': istage = 'out'
    elif instagram_status['color'] == '':
        istage = 'in'

    return istage

class FakeInstagramResponse:
    def __init__(self, url, status_code, text):
        self.url = url
        self.status_code =status_code
        self.text = text
