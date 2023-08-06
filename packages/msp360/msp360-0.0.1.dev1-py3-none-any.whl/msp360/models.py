from typing import TypedDict, NewType, Optional, Dict, List, Union
from enum import IntEnum

Uuid = NewType('Uuid', str)
Date = NewType('Date', str)


class UserModeType(IntEnum):
    '''Mode of user license management.
    '''
    #: User can activate only a limited number of paid licenses.
    Manual          = 0
    #: User can activate paid licenses from the global pool.
    Automatic       = 1
    #: Company settings for licensing are applied. Direct changes are restricted.
    CompanySettings = 2


class AccountType(IntEnum):
    AmazonS3            = 0
    AmazonS3China       = 1
    Azure               = 2
    S3Compatible        = 5
    BackblazeB2         = 9
    Connectria          = 11
    Constant            = 12
    Dunkel              = 14
    GreenQloud          = 15
    HostEurope          = 16
    Seeweb              = 17
    Walrus              = 20
    FS                  = 21 # File System
    GoogleCloudPlatform = 22
    Wasabi              = 23
    Minio               = 24


class DestinationOfAccount(TypedDict):
    '''
    Args:
        DestinationID: Storage destination ID.
        AccountID: Storage account ID.
        Destination: Storage destination name.
        DestinationDisplayName: Displayed destination name.
    '''
    DestinationID:          Uuid
    AccountID:              Uuid
    Destination:            str
    DestinationDisplayName: str


class DestinationForNewUser(TypedDict):
    AccountID:   Uuid
    Destination: str
    PackageID:   int


class License(TypedDict):
    '''
    Args:
        ID: License UUID.
        Number: License number.
        ComputerName:
        OperatingSystem:
        IsTrial: ``True`` is trial, ``False`` is paid license.
        IsTaken: The status of license: in use or not in use.
        LicenseType: The type of license.
        DateExpired: The license expiration date.
        Transaction: Transaction of license.
        User: User attached to a license.
        UserID: User UUID.
    '''
    ID:              Uuid
    Number:          int
    ComputerName:    Optional[str]
    OperatingSystem: Optional[str]
    IsTrial:         bool
    IsTaken:         bool
    LicenseType:     str
    DateExpired:     Date
    Transaction:     Uuid
    User:            Optional[str]
    UserID:          Optional[Uuid]


class Administrator(TypedDict):
    AdminID:          Uuid
    Email:            str
    FirstName:        str
    LastName:         str
    Enabled:          bool
    PermisionsModels: Dict[str, int]
    LastLogin:        Date
    DateCreated:      Date
    Companies:        str


class User(TypedDict):
    ID:                    Uuid
    Email:                 str
    FirstName:             str
    LastName:              str
    NotificationEmails:    List[str]
    Company:               str
    Enabled:               bool
    LicenseManagementMode: UserModeType
    DestinationList:       List[Dict[str, Union[str, int]]]  # TODO
    SpaceUsed:             int
