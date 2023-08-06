"""
The aurori project

Copyright (C) 2022  Marcus Drobisch,

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__authors__ = ["Marcus Drobisch"]
__contact__ = "aurori@fabba.space"
__credits__ = []
__license__ = "AGPLv3+"

from aurori.logs import logManager
import hashlib
try:
    import ldap
except ImportError:
    logManager.info("Unable to import ldap")

from aurori.workspaces.workspaceHooks import WorkspaceHooks


class UserManager(object):
    """ The UserManager ...
    """
    def __init__(self, ):
        # preparation to instanciate
        pass

    def init_manager(self, app, db, workspaceManager, config):
        self.config = config
        self.app = app
        self.db = db
        self.workspaceManager = workspaceManager
        logManager.info("UserManager initialized")

        from aurori.users.models import User
        self.user = User

    def checkUserTokens(self, ):
        # fixme: Does this do anything useful?
        users = self.user.query.all()
        for user in users:
            print(user, user.sessionValid)

    def registerUser(self, userdata, ldap=False):
        if self.checkUserExist(userdata['email']):
            return None
        else:
            u = self.user(email=userdata['email'],
                          password=userdata['password'],
                          isAdmin=False)
            u.firstname = userdata['firstname']
            u.lastname = userdata['lastname']
            u.organization = userdata['organization']
            u.account_activated = True
            u.ldap = ldap
            if ldap is True:
                u.ldap_dn = userdata['ldap_dn']
                u.ldap_username = userdata['ldap_username']
            self.db.session.add(u)
            self.db.session.commit()
            return u

    def registerLdapUser(self, email):
        print("")

    def checkLdapUser(self, userid):
        server = self.config['LDAP'].get('server')
        bind_dn = self.config['LDAP'].get('bind_dn')
        bind_pw = self.config['LDAP'].get('bind_pw')
        search_dn = self.config['LDAP'].get('user_dn')
        default_organization = self.config['LDAP'].get('default_organization', "")

        attrs = [
            "givenName", "sn", "cn", "userPrincipalName", "mail",
            "sAMAccountName", "displayName"
        ]

        ldap_con = ldap.initialize(server)
        ldap_con.simple_bind_s(bind_dn, bind_pw)
        fil = "(| (mail=*" + str(userid) + \
            "*) (sAMAccountName=*" + str(userid) + "*))"
        dn, user = ldap_con.search_s(search_dn, ldap.SCOPE_SUBTREE, fil,
                                     attrs)[0]

        print(user)
        userdata = {
            "email": user['mail'][0].decode("utf-8"),
            "password": "ldap",
            "firstname": user['givenName'][0].decode("utf-8"),
            "lastname": user['sn'][0].decode("utf-8"),
            "organization": default_organization,
            'ldap_dn': dn,
            'ldap_username': user['sAMAccountName'][0].decode("utf-8")
        }
        u = self.registerUser(userdata, True)
        return u

    def get_user_by_api_key(self, plaintext_api_key):
        if plaintext_api_key is not None:
            api_key_hash = hashlib.sha512(
                plaintext_api_key.encode('utf8')).hexdigest()
            return self.user.query.filter_by(api_key=api_key_hash).first()
        else:
            return None

    def getUser(self, userid):
        user = self.user.query.filter_by(email=userid).first()
        if userid is not None:
            if user is None and self.config['LDAP'].get("enable", False):
                print("Search for ldap user locally")
                user = self.user.query.filter_by(ldap_username=userid).first()
                if user is None:
                    print("Search for ldap user on server")
                    try:
                        user = self.checkLdapUser(userid)
                    except Exception:
                        user = None
        return user

    def checkUserExist(self, email):
        user = self.user.query.filter_by(email=email).first()
        if user is None:
            return False
        else:
            return True

    def checkUserPassword(self, user, password):
        if user.ldap is False:
            return user.checkPassword(password)
        else:
            server = self.config['LDAP'].get('server')
            try:
                ldap_con = ldap.initialize(server)
                ldap_con.simple_bind_s(user.ldap_dn, password)
                return True
            except Exception:
                return False
