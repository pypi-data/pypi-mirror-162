class OverrideResolver(object):
    def __init__(self, target_matcher, action_resolver):
        self.target_matcher = target_matcher
        self.action_resolver = action_resolver

    def resolve_or_none(self, workspace, experiment, user):
        overridden_variation_id = experiment.user_overrides.get(user.id)
        if overridden_variation_id:
            return experiment.get_variation_by_id_or_none(overridden_variation_id)

        for overridden_rule in experiment.segment_overrides:
            if self.target_matcher.matches(overridden_rule.target, workspace, user):
                return self.action_resolver.resolve_or_none(overridden_rule.action, workspace, experiment, user)

        return None
