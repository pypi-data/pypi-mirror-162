"""Kameleoon exceptions"""


class KameleoonException(Exception):
    """Base Kameleoon exception"""

    def __init__(self, message=None) -> None:
        self.message = f"Kameleoon error: {message}"
        super().__init__(self.message)


class ConfigurationNotFoundException(KameleoonException):
    """Configuration Not Found"""


class CredentialsNotFoundException(KameleoonException):
    """Credentials Not Found"""


class NotFoundError(Exception):
    """Base not found error"""

    def __init__(self, message=None) -> None:
        self.message = str(message) + ' not found.'
        super().__init__(self.message)


class ExperimentConfigurationNotFound(NotFoundError):
    """Exception indicating that the requested experiment ID has not been found in the
    internal configuration of the SDK. This is usually normal and means that the experiment
    has not yet been started on Kameleoon's side (but code triggering / implementing variations
    is already deployed on the web-application's side)."""

    def __init__(self, message=None) -> None:
        self.message = 'Experiment ' + str(message)
        super().__init__(self.message)


class VariationConfigurationNotFound(NotFoundError):
    """Variation configuration not found"""

    def __init__(self, message=None) -> None:
        self.message = 'Variation ' + str(message)
        super().__init__(self.message)


class FeatureConfigurationNotFound(NotFoundError):
    """Exception indicating that the requested feature ID
    has not been found in the internal configuration of the SDK.
    This is usually normal and means that the feature flag
    has not yet been activated on Kameleoon's side."""

    def __init__(self, message=None) -> None:
        self.message = 'Feature flag ' + str(message)
        super().__init__(self.message)


class FeatureVariableNotFound(NotFoundError):
    """Exception indicating that the requested variable has not been found.
    Check that the variable's ID (or key) matches the one in your code."""

    def __init__(self, message=None) -> None:
        self.message = 'Feature variable ' + str(message)
        super().__init__(self.message)


class NotTargeted(KameleoonException):
    """Exception indicating that the current visitor / user
    did not trigger the required targeting conditions for this experiment.
    The targeting conditions are defined via Kameleoon's segment builder."""

    def __init__(self, message=None) -> None:
        self.message = "Visitor " + str(message) + " is not targeted."
        super().__init__(self.message)


class NotActivated(KameleoonException):
    """Exception indicating that the current visitor / user t
    riggered the experiment (met the targeting conditions),
    but did not activate it. The most common reason for that
    is that part of the traffic has been excluded from the
    experiment and should not be tracked."""

    def __init__(self, message=None) -> None:
        self.message = "Visitor " + str(message) + " is not activated."
        super().__init__(self.message)


class VisitorCodeNotValid(KameleoonException):
    """Exception indicating that visitorCode is empty or too long."""
    def __init__(self, message=None) -> None:
        self.message = "Visitor code not valid: " + str(message)
        super().__init__(self.message)


class SiteCodeDisabled(KameleoonException):
    """Exception indicating that site is disabled. To make it working need to enable in an account"""
    def __init__(self, message=None) -> None:
        self.message = "Site with siteCode '" + str(message) + "' is disabled"
        super().__init__(self.message)
