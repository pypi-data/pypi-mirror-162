
## BASIC EXCEPTION CLASSES 

from rest_framework.exceptions import APIException

class ModelNotFound(APIException):
    status_code = 204
    default_detail = 'Matching action and type not found , try with some other type '
    default_code = 'model_not_found'



class TransitionNotAllowed(APIException):
    status_code = 204
    default_detail = 'Transition Not Allowed .'
    default_code = 'transition_unavailable'



class SignaturesNotMatching(APIException):
    status_code = 204
    default_detail = 'Signatures not matching , only positive index accepted'
    default_code = 'signatures_index_not_matching'



class SignLengthError(APIException):
    status_code = 204
    default_detail = 'Signatures not matching , only positive index accepted'
    default_code = 'signatures_index_not_matching'