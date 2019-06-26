from flask import Blueprint, render_template, abort, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from ..users.models import User
from forms import TokenGrant
from app import db

moderator = Blueprint("moderator", __name__, url_prefix="/moderator")

@login_required
@moderator.route('/token/<int:user_id>/', methods=['GET', 'POST'])
def token(user_id=None):
    user = None
    token_form = None
    if not current_user.is_moderator():
        return abort(403)
    if user_id:
        user = User.query.get_or_404(user_id)
        token_form = TokenGrant()

        if token_form.validate_on_submit():
            user.user_class = 1 if token_form.is_moderator.data else 0
            user.upload_credits = token_form.token_number.data
            db.session.add(user)
            db.session.commit()
            flash("Save successful.", "success")
            return redirect(url_for("users.user_page", user_id=user.account_id))

        token_form.is_moderator.data = user.is_moderator()
        token_form.token_number.data = user.upload_credits
    return render_template('moderator/token.html', title="Grant tokens", user=user, token_form=token_form)
