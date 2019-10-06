import flask_restplus as fr
from flask import current_app, render_template

from app.decorators import use_args
from app.email import send_email
from app.errors.exceptions import BadRequest
from app.repositories.user import user_repo
from app.utils import to_json

ns = fr.Namespace(name="password", description="Password reset and verification")


@ns.route('/request_token')
class APIPasswordRequestToken(fr.Resource):
    @use_args(**{
        'type': 'object',
        'properties': {
            'email': {'type': 'string'},
        },
        'required': ['email']
    })
    def post(self, args):
        user = user_repo.get_by_email(args.get('email'))
        if not user:
            raise BadRequest(message='Email is not exist')
        if not user.emailVerified:
            raise BadRequest(message='Email is not verified')
        token = user_repo.generate_reset_password_token(user)
        url = "{path}?token={token}".format(path=current_app.config.get('RESET_PASSWORD_URL'), token=token)
        send_email(
            subject='[TheVault] Reset Password',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user.email],
            html_body=render_template('email/reset_password.html', user=user, url=url))
        return {'message': 'Reset password is sending to your email. Please check your inbox'}, 201


@ns.route('/verify_token/<string:token>')
class APIPasswordVerifyToken(fr.Resource):
    @use_args(**{
        'type': 'object',
        'properties': {
            'password': {'type': 'string'},
        },
        'required': ['password'],
    })
    def post(self, args, token):
        user, message = user_repo.get_user_from_token_reset_password(token=token)
        if message:
            raise BadRequest(message=message)
        user = user_repo.update_user(user, None, args)
        if user is None:
            raise BadRequest(message='Reset password failed')
        return {'item': to_json(user._data), 'message': 'Reset password is successfully'}, 200
