import abc

from hackle.commons import validator
from hackle.evaluation.match.semantic_version import SemanticVersion


class ValueMatcher(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def matches(self, operator_matcher, user_value, match_value):
        pass


class StringValueMatcher(ValueMatcher):
    def matches(self, operator_matcher, user_value, match_value):
        if isinstance(user_value, str) and isinstance(match_value, str):
            return operator_matcher.string_matches(user_value, match_value)
        else:
            return False


class NumberValueMatcher(ValueMatcher):
    def matches(self, operator_matcher, user_value, match_value):
        if validator.is_finite_number(user_value) and validator.is_finite_number(match_value):
            return operator_matcher.number_matches(user_value, match_value)
        else:
            return False


class BoolValueMatcher(ValueMatcher):
    def matches(self, operator_matcher, user_value, match_value):
        if isinstance(user_value, bool) and isinstance(match_value, bool):
            return operator_matcher.bool_matches(user_value, match_value)
        else:
            return False


class VersionValueMatcher(ValueMatcher):
    def matches(self, operator_matcher, user_value, match_value):
        user_version = SemanticVersion.parse_or_none(user_value)
        match_version = SemanticVersion.parse_or_none(match_value)
        if user_version is not None and match_version is not None:
            return operator_matcher.version_matches(user_version, match_version)
        else:
            return False
