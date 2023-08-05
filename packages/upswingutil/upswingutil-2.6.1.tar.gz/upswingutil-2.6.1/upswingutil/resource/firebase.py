import logging

from firebase_admin import auth, get_app
from firebase_admin.auth import UserNotFoundError, EmailAlreadyExistsError


class FirebaseHelper:

    def __init__(self, appName=None):
        self.appName = appName
        # modifiedBy:Vikash Anand updated because of issues to initilize with default firebase app
        self.app = get_app(self.appName) if appName else get_app()

    def find_user_by_email(self, email):
        try:
            return auth.get_user_by_email(email, app=self.app)
        except UserNotFoundError as userNotFound:
            logging.error(f'User not found in {self.appName} for given email id')
        except Exception as e:
            logging.error(e)

    def create_user_by_email(self, email, name=None):
        user = None
        try:
            user = auth.create_user(email=email, display_name=name, app=self.app)
            logging.info('creating new user in alvie')
        except EmailAlreadyExistsError as err:
            logging.info('returning existing user in alvie')
            user = self.find_user_by_email(email)
        except Exception as e:
            logging.error(e)
        finally:
            return user
