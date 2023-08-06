from typing import Any, Dict, List, Optional, TYPE_CHECKING
from json.decoder import JSONDecodeError
from uuid import UUID

from httpx import Client, HTTPError, HTTPStatusError
from .exceptions import ResourceNotFound, check_uuid, ClientError


if TYPE_CHECKING:
    from .models import (
        Administrator, DestinationForNewUser, DestinationOfAccount, License,
        User, UserModeType,
    )

    Object = Dict[str, Any]


class Msp360:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.client = Client(
            base_url='https://api.mspbackups.com/api/',
            headers={'content-type': 'application/json', 'accept': 'application/json'},
        )
        self._login()

    def _login(self) -> None:
        creds = {'UserName': self.username, 'Password': self.password}
        resp = self.post('/Provider/Login', creds)
        self.client.headers.update({'authorization': f'Bearer {resp["access_token"]}'})

    def _request(self, method, path, *, params=None, body=None):
        resp = self.client.request(method, path, params=params, json=body)
        resp.raise_for_status()
        try:
            return resp.json()
        except JSONDecodeError:
            return resp.text

    def get(self, path, params=None):
        return self._request('GET', path, params=params)

    def _get_uuid(self, endpoint, uuid):
        resp = self.get(f'{endpoint}/{uuid}')
        if resp is None:
            check_uuid(uuid)
        return resp

    def post(self, path, body):
        return self._request('POST', path, body=body)

    def put(self, path, body):
        return self._request('PUT', path, body=body)

    def delete(self, path, params=None):
        return self._request('DELETE', path, params=params)

# region PACKAGES
    def get_packages(self):
        '''Returns a list of package structures available to users.
        '''
        return self.get('Packages')

    def get_package(self, package_id: int):
        '''Returns the package structure by package ID.
        '''
        return self.get(f'Packages/{package_id}')

    def create_package(self, **kwargs):
        raise NotImplementedError

    def update_package(self, **kwargs):
        raise NotImplementedError

    def delete_package(self, package_id) -> None:
        return self.delete(f'Packages/{package_id}')
# endregion

# region USERS
    def get_users(self) -> List['User']:
        '''Returns list of users.
        '''
        return self.get('Users')

    def get_user(self, user_id: str) -> 'User':
        '''Returns user by user ID.
        '''
        return self.get(f'Users/{user_id}')

    def get_user_by_login(self, login: str, password: str) -> 'User':
        '''Returns user by user login and password.
        '''
        body = {'Email': login, 'Password': password}
        return self.put('Users/Authenticate', body)

    def create_user(
        self,
        login:                   str,
        password:                str,
        first_name:              Optional[str] = None,
        last_name:               Optional[str] = None,
        notification_emails:     Optional[List[str]] = None,
        company:                 Optional[str] = None,
        enabled:                 bool = True,
        destination_list:        Optional[List['DestinationForNewUser']] = None,
        send_email_instruction:  bool = False,
        license_management_mode: Optional['UserModeType'] = None,
    ) -> str:
        '''Creates new user.

        Args:
            login: User login (must be unique).
            password: User password.
            send_email_instruction: Sends email with instructions to
                user.
            company: Company name (not UUID).
            license_management_mode: Mode of user license management.
        '''
        if 6 > len(password) > 100:
            raise ValueError('Password required length between 6 and 100')

        if isinstance(notification_emails, str):
            notification_emails = [notification_emails]

        body = {
            'Email':                login,
            'Password':             password,
            'FirstName':            first_name,
            'LastName':             last_name,
            'NotificationEmails':   notification_emails,
            'Company':              company,
            'Enabled':              enabled,
            'DestinationList':      destination_list,
            'SendEmailInstruction': send_email_instruction,
            'LicenseManagmentMode': license_management_mode,
        }

        resp = self.post('Users', body)

        # XXX: always returns 200, if it's not an UUID it's an error
        try:
            UUID(resp)
            return resp
        except ValueError:
            if 'Email already exist' in resp:
                # XXX: not necessarily an email address
                raise ClientError('User login already exists.') from None
            raise ClientError(resp) from None

    def update_user(self, **kwargs):
        '''Applies new values of user properties.
        '''
        raise NotImplementedError

    def delete_user(self, user_id: str, remove_data: bool = False) -> None:
        '''Deletes user account only.

        Args:
            user_id: User UUID.
            only_account: If ``False`` removes user account only. Cloud
            storage data is not deleted. Otherwise, deletes all user
            data as well (with some delay).
        '''
        path = f'Users/{user_id}' if remove_data else f'Users/{user_id}/Account'

        try:
            return self.delete(path) or None
        except HTTPStatusError as e:
            if e.response.status_code == 400:
                check_uuid(user_id)
            else:
                raise

    def get_user_computers(self, user_id: str) -> List['Object']:
        '''Returns list of user computers.
        '''
        return self.get(f'Users/{user_id}/Computers')
# endregion

# region MONITORING
    def get_monitoring(self) -> List['Object']:
        '''Returns status data for latest runs for endpoints which are
        currently online (all users).
        '''
        return self.get('Monitoring')

    def get_user_monitoring(self, user_id: str) -> List['Object']:
        '''Returns status data for latest runs for endpoints which are
        currently online filtered by specified user ID.
        '''
        return self._get_uuid('Monitoring', user_id)
# endregion

# region COMPANIES
    def get_companies(self) -> List['Object']:
        return self.get('Companies')

    def get_company(self, company_id: str) -> 'Object':
        return self._get_uuid('Companies', company_id)

    def create_company(
        self,
        name:             str,
        *, storage_limit: int = -1,
        license_settings: int = 1,
    ) -> str:
        '''
        Creates new company and returns its ID.

        Args:
            name: Company Name.
            storage_limit: Company backup limit. A negative value
                indicates the resource is unconstrained by a quota
                integer.
            license_settings: Company license settings:
                0 - Custom (Users have custom license settings).
                1 - Global Pool (Users activate paid licenses from the
                    global pool automatically).
                2 - Company Pool (Users can activate only limited number
                    of paid licenses from the company pool).
        '''
        body = {'Name': name, 'StorageLimit': storage_limit, 'LicenseSettings': license_settings}
        return self.post('Companies', body)

    def delete_company(self, company_id) -> None:
        try:
            return self.delete(f'Companies/{company_id}')
        except HTTPError as e:
            err = e.response.json().get('Message', '')

            if e.response.status_code == 400:
                not_found = 'not found' in err
                check_uuid(company_id, not_found, err)
            raise
# endregion

# region LICENSES
    def get_licenses(self, is_available: bool = False) -> List['License']:
        '''Returns a list of license structures.

        Args:
            is_available: Returns only available licenses.
        '''
        params = {'isAvailable': is_available}
        return self.get('Licenses', params)

    def get_license(self, license_id: str) -> 'License':
        return self._get_uuid('Licenses', license_id)

    def grant_license(self, user_id: str, license_id: str):
        '''Grants an available license for existing user.

        Args:
            license_id: Old license UUID.
            user_id: Existing user UUID.
        '''
        body = {'LicenseID': license_id, 'UserID': user_id}
        return self.client.post('Licenses/Grant', body)

    def release_license(self, user_id: str, license_id: str):
        '''Releases license from a user.

        Args:
            license_id: Old license UUID.
            user_id: Existing user UUID.
        '''
        body = {'LicenseID': license_id, 'UserID': user_id}
        return self.client.post('Licenses/Release', body)

    def revoke_license(self, user_id: str, license_id: str):
        '''Revokes license (release info about computer).

        Args:
            license_id: Current license UUID.
            user_id: Existing user UUID.
        '''
        body = {'LicenseID': license_id, 'UserID': user_id}
        return self.client.post('Licenses/Revoke', body)

# endregion

# region DESTINATIONS
    def get_destinations(self, user_login: Optional[str] = None) -> List['DestinationOfAccount']:
        try:
            path = f'Destinations/{user_login}' if user_login else 'Destinations'
            return self.get(path)
        except HTTPError as e:
            # XXX: wrongly returns 406 when `user_login` is invalid
            if e.response.status_code == 406 and user_login:
                raise ResourceNotFound(user_login) from None
            raise

    def add_user_destination(self, user_id: str, destination: 'DestinationForNewUser'):
        body = {'UserID': user_id, **destination}
        return self.post('Destinations', body)

    def delete_user_destination(self, user_id: str, destination_id: str):
        params = {'UserID': user_id}
        return self.delete(f'Destinations/{destination_id}', params=params)

# endregion

# region ACCOUNTS
    def get_accounts(self) -> List['Object']:
        '''Returns account list.
        '''
        return self.get('Accounts')

    def get_account(self, account_id) -> 'Object':
        '''Returns account properties by account ID.
        '''
        return self._get_uuid('Accounts', account_id)

    def create_account(self, **kwargs):
        '''Adds new account.
        '''
        raise NotImplementedError

    def update_account(self, **kwargs):
        '''Edits account.
        '''
        raise NotImplementedError

    def add_account_destination(
        self,
        account_id:               str,
        destination:              str,
        destination_display_name: Optional[str] = None,
    ):
        '''Adds destinations to existing storage accounts. You can add
        multiple destinations (buckets) to each storage account.

        Args:
            destination: Name of an existent bucket.

        ..note:
        '''
        raise NotImplementedError

    def update_account_destination(self, destination: 'DestinationOfAccount'):
        '''Edits storage account destinations.
        '''
        return self.put('Accounts/EditDestination', destination)

    def delete_account_destination(self, destination: 'DestinationOfAccount'):
        '''Removes storage destination from an account.
        '''
        return self.put('Accounts/RemoveDestination', destination)
# endregion

# region BILLING
    def get_billing(self) -> 'Object':
        '''Returns billing information for reporting month.
        '''
        return self.get('Billing')
# endregion

# region BUILDS
    def get_builds(self) -> List['Object']:
        '''Returns a list of build structures that are available to
        users.
        '''
        return self.get('Builds')

    def get_builds_versions(self) -> List['Object']:
        '''Returns latest available build versions.
        '''
        return self.get('Builds/AvailableVersions')

    def request_custom_builds(self, **kwargs):
        '''Requests custom builds of specified editions.
        '''
        raise NotImplementedError
# endregion

# region ADMINISTRATORS
    def get_admins(self) -> List['Administrator']:
        '''Returns the list of administrators.
        '''
        return self.get('Administrators')

    def get_admin(self, admin_id: str) -> 'Administrator':
        '''Returns administrator properties by administrator ID.
        '''
        return self._get_uuid('Administrators', admin_id)

    def create_admin(self, **kwargs):
        '''Creates new administrator.
        '''
        raise NotImplementedError

    def update_admin(self, **kwargs):
        '''5Updates administrator properties to new values.
        '''
        raise NotImplementedError

    def delete_admin(self, admin_id: str):
        '''Deletes specified administrator.
        '''
        return self.delete(f'Administrators/{admin_id}')
# endregion
