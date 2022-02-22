from flask import render_template, request, session, abort, flash, redirect, url_for
import ast
from sqlalchemy.exc import IntegrityError

from app import db
from . import admin
from .forms import InstagramLoginForm, InstagramLogoutForm, InstagramVerifyFrom, InstagramCookieSet
from .models import Admin, InstagramCookie, InstagramError
from .utils import root_view, admin_view, viewer_view, banned_view, get_browser, get_screen_browser, del_browser, update_instagram_cookie, get_instagram_cookie, get_instagram_status, get_instagram_stage, FakeInstagramResponse

from blueprints.user.models import Story


@admin.route('/dashboard/')
@viewer_view
def dashboard():
    admin = Admin.query.get(session.get('adminID'))

    cookie = get_instagram_cookie()
    instagram_status = get_instagram_status(cookie)

    tables = zip(
        InstagramError.query.filter(InstagramError.story_id).order_by(InstagramError.id.desc()).limit(10).all(),
        Story.query.filter(Story.stage.ilike('failed')).order_by(Story.id.desc()).limit(10).all()
    )

    return render_template('admin/dashboard.html', admin=(admin.username, admin.role_name()),  instagram_status=instagram_status, tables=tables)


@admin.route('/errors-log/')
@admin_view
def errors_log():
    admin = Admin.query.get(session.get('adminID'))

    page = request.args.get('page', 1, type=int)
    errors_table = InstagramError.query.order_by(InstagramError.id.desc()).paginate(page=page, per_page=9)

    return render_template('admin/errors_log.html', errors_table=errors_table, admin=(admin.username, admin.role_name()))


@admin.route('/stories-log/')
@admin_view
def stories_log():
    admin = Admin.query.get(session.get('adminID'))

    page = request.args.get('page', 1, type=int)
    stories_table = Story.query.order_by(Story.id.desc()).paginate(page=page, per_page=11)

    return render_template('admin/stories_log.html', stories_table=stories_table, admin=(admin.username, admin.role_name()))


@admin.route('/insta-setting/', methods=['GET', 'POST'])
@admin_view
def insta_setting():
    global insta

    screen = get_screen_browser()

    admin = Admin.query.get(session.get('adminID'))
    forms = (InstagramLoginForm(request.form), InstagramVerifyFrom(request.form), InstagramLogoutForm(request.form))

    cookie = get_instagram_cookie()
    instagram_status = get_instagram_status(cookie)
    session['istage'] = get_instagram_stage(instagram_status, session.get('istage'))
    if session['istage'] == 'in':
        del_browser()



    if request.method == 'POST':
        if session.get('istage') == 'out':
            if not forms[0].validate_on_submit(): abort(400)

            try:
                if not 'insta' in globals():
                    insta = get_browser(cookie)
                result = insta.login(forms[0].username.data, forms[0].password.data)
                screen = get_screen_browser()

            except Exception as e:
                screen = get_screen_browser()
                del_browser()
                result = [str(e)]

                instagram_error = InstagramError()
                instagram_error.url = 'InstagramLoginouter.login()'
                instagram_error.status_code = None
                instagram_error.text = str(e)

                db.session.add(instagram_error)
                db.session.commit()

            if result == 'verify':
                session['istage'] = 'verify'
            elif type(result) == list:
                for err in result:
                    flash(err, 'secondary')
            elif type(result) == bool and result:
                cookie = update_instagram_cookie(insta.cookie())
                instagram_status = get_instagram_status(cookie)
                session['istage'] = get_instagram_stage(instagram_status, session.get('istage'))
                if session['istage'] == 'in':
                    del_browser()

        elif session.get('istage') == 'verify':
            if not forms[1].validate_on_submit(): abort(400)

            try:
                result = insta.verify(forms[1].verification_code.data)
                screen = get_screen_browser()

            except Exception as e:
                screen = get_screen_browser()
                del_browser()
                result = [str(e)]

                instagram_error = InstagramError()
                instagram_error.url = 'InstagramLoginouter.verify()'
                instagram_error.status_code = None
                instagram_error.text = str(e)

                db.session.add(instagram_error)
                db.session.commit()
                print('after del_browser')


            if type(result) == list:
                for err in result:
                    flash(err, 'secondary')
                    session['istage'] = 'out'
            elif type(result) == bool and result:
                cookie = update_instagram_cookie(insta.cookie())
                instagram_status = get_instagram_status(cookie)
                session['istage'] = get_instagram_stage(instagram_status, session.get('istage'))
                if session['istage'] == 'in':
                    del_browser()

        elif session.get('istage') == 'in':
            if not forms[2].validate_on_submit(): abort(400)

            try:
                if not 'insta' in globals():
                    insta = get_browser(cookie)
                result = insta.logout(instagram_status['username'])
                screen = get_screen_browser()

            except Exception as e:
                screen = get_screen_browser()
                del_browser()
                result = [str(e)]

                instagram_error = InstagramError()
                instagram_error.url = 'InstagramLoginouter.logout()'
                instagram_error.status_code = None
                instagram_error.text = str(e)

                db.session.add(instagram_error)
                db.session.commit()

            if type(result) == list:
                for err in result:
                    flash(err, 'secondary')
            elif type(result) == bool and result:
                cookie = update_instagram_cookie(insta.cookie())
                instagram_status = get_instagram_status(cookie)
                session['istage'] = get_instagram_stage(instagram_status, session.get('istage'))

            del_browser()

    if session.get('istage') == 'out':
        return render_template('admin/insta_setting/login.html', forms=forms, screen=screen, admin=(admin.username, admin.role_name()),  instagram_status=instagram_status)
    elif session.get('istage') == 'verify':
        return render_template('admin/insta_setting/verify.html', forms=forms, screen=screen, admin=(admin.username, admin.role_name()),  instagram_status=instagram_status)
    elif session.get('istage') == 'in':
        return render_template('admin/insta_setting/logout.html', forms=forms, screen=screen, admin=(admin.username, admin.role_name()),  instagram_status=instagram_status)
    elif session.get('istage') == 'error':
        return render_template('admin/insta_setting/error.html', forms=forms, screen=screen, admin=(admin.username, admin.role_name()),  instagram_status=instagram_status)

    return render_template('admin/insta_setting-ori.html', forms=forms, screen=screen, admin=(admin.username, admin.role_name()),  instagram_status=instagram_status, istage=session.get('istage'))


@admin.route('/del-insta/', methods=['GET'])
@admin_view
def del_insta():
    flag = del_browser()
    if flag: flash(f'Browser closed.', 'tertiary')
    else:  flash(f'There isn\'t any browser.', 'secondary')

    if session.get('istage'):
        del session['istage']

    return redirect(url_for('admin.insta_setting'))


@admin.route('insta-cookies/', methods=['GET', 'POST'])
@admin_view
def insta_cookie():
    admin = Admin.query.get(session.get('adminID'))

    cookie = get_instagram_cookie()
    instagram_status = get_instagram_status(cookie)

    form = InstagramCookieSet(request.form)

    if request.method == 'POST':
        if not form.validate_on_submit(): abort(400)

        cookie = ast.literal_eval(form.cookie.data)
        update_instagram_cookie(cookie)
        instagram_status = get_instagram_status(cookie)
        if session.get('istage'):
            del session['istage']


    return render_template('admin/insta_setting/cookie.html', form=form, admin=(admin.username, admin.role_name()),  instagram_status=instagram_status, cookie=cookie)