from datetime import datetime, UTC
from typing import Any

class AppException(Exception):
    status_code = 500
    error_type = "application_error"
    error_code = "APPLICATION_ERROR"

    def __init__(self, message: str, details: Any = None):
        self.message = message
        self.details = details
        timestamp = datetime.now(UTC).isoformat()
        super().__init__(message)

class BusinessRuleException(AppException):
    status_code = 409
    error_type = "business_rule"
    error_code = "BUSINESS_RULE_VIOLATION"

class ServiceRequestValidationException(AppException):
    status_code = 422
    error_type = "service_request_validation"
    error_code = "SERVICE_REQUEST_INVALID"

class UpstreamServiceHttpException(AppException):
    status_code = 502
    error_type = "upstream_http_error"
    error_code = "UPSTREAM_HTTP_ERROR"

class UpstreamServiceInvalidResponseException(AppException):
    status = 502
    error_type = "upstream_service_exception"
    error_code = "UPSTREAM_SERVICE_INVALID_RESPONSE"

class InternalSchemaConfigurationException(AppException):
    status_code = 500
    error_type = "internal_schema_configuration"
    error_code = "INVALID_SCHEMA_CONFIGURATION"

class UnsupportedLLMProviderException(AppException):
    status_code = 500
    error_type = "internal_provider_configuration"
    error_code = "MISSING_PROVIDER_CONFIGURATION"