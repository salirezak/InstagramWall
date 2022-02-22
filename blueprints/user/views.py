from flask import render_template, redirect, url_for, abort, request, session, flash
from sqlalchemy.exc import IntegrityError
from flask_mail import Message

from app import db, mail
from . import user
from .forms import StoryTextForm
from .models import Story

from blueprints.admin.models import InstagramCookie, InstagramError

from instagram import Checker, StoryUploader
from picture import generate_pic, generate_text, bg_color


@user.route('/test/')
def test():
    return render_template('user/up.html', link='', error='some thing', status_code=None, bg_color=bg_color())

@user.route('/', methods=['GET', 'POST'])
def index():
    form = StoryTextForm(request.form)

    if request.method == 'GET' and not session.get('storyID'):
        session['bgCOLOR'] = bg_color()

    if request.method == 'POST' and not session.get('storyID'):
        if not form.validate_on_submit(): abort(400)

        text = generate_text(form.text.data)

        if not text:
            flash('Make it shorter.', 'secondary')
        else:
            new_story = Story()
            new_story.text = text

            db.session.add(new_story)
            db.session.commit()

            session['storyID'] = new_story.id

    if session.get('storyID'):
        story = Story.query.get(session.get('storyID'))

        if story.stage_name() == 'received':
            story.stage = 'uploading'
            db.session.commit()

            return render_template('user/uploading.html', bg_color=session.get('bgCOLOR'))

        if story.stage_name() == 'uploading':

            instagram_cookie = InstagramCookie.query.order_by(InstagramCookie.id.desc()).first()
            cookie = instagram_cookie.get_cookie() if instagram_cookie else None

            try:
                instagram_response, instagram_status = Checker(cookie)
            except Exception as e:
                instagram_status = {'username':None}
                instagram_response = FakeInstagramResponse('Checker()', None, str(e))

            if not instagram_status['username']:
                error_id = update_instagram_errors(instagram_response, story)
                story.stage = 'failed'
                story.error_id = error_id
                db.session.commit()
                del session['storyID']
                return render_template('user/result.html', link=None, error='Not logged in', status_code=instagram_response.status_code if instagram_response.status_code != 200 else 401, bg_color=session.get('bgCOLOR'))

            try:
                instagram_response, instagram_link = StoryUploader(cookie, pic=generate_pic(story.text, bg_color=session.get('bgCOLOR')))
            except Exception as e:
                instagram_response, instagram_link = FakeInstagramResponse('StoryUploader()', None, str(e)), None

            if not instagram_link:
                error_id = update_instagram_errors(instagram_response, story)
                story.stage = 'failed'
                story.error_id = error_id
                db.session.commit()
                del session['storyID']
                return render_template('user/result.html', link=None, error='Couldn\'t upload', status_code=instagram_response.status_code if instagram_response.status_code else 400, bg_color=session.get('bgCOLOR'))

            story.stage = 'uploaded'
            db.session.commit()
            del session['storyID']
            body = f'Story:\n  Id: {story.id}\n  Timestamp: {story.timestamp}\n  Text: {story.text}'
            msg = Message(subject="IW - New story", recipients=['salirezakarami@gmail.com'], body=body)
            mail.send(msg)

            return render_template('user/result.html', link=instagram_link, error=None, status_code=None, bg_color=session.get('bgCOLOR'))

        if story.stage_name() in ['failed', 'uploaded']:
            del session['storyID']
            session['bgCOLOR'] = bg_color()

    return render_template('user/index.html', form=form, bg_color=session.get('bgCOLOR'))


def update_instagram_errors(response, story):
    instagram_error = InstagramError()
    instagram_error.url = response.url
    instagram_error.status_code = response.status_code
    instagram_error.text = response.text
    instagram_error.story_id = story.id

    db.session.add(instagram_error)
    db.session.commit()
    instagram_error

    body = f'Story:\n  Id: {story.id}\n  Timestamp: {story.timestamp}\n  Text: {story.text}\n\n'
    body += f'Error:\n  Id: {instagram_error.id}\n  Timestamp: {instagram_error.timestamp}\n  Url: {instagram_error.url}\n  Status Code: {instagram_error.status_code}\n  Text:\n    {instagram_error.text}'
    msg = Message(subject="IW - Error", recipients=['salirezakarami@gmail.com'], body=body)
    mail.send(msg)
    return instagram_error.id

class FakeInstagramResponse:
    def __init__(self, url, status_code, text):
        self.url = url
        self.status_code =status_code
        self.text = text