import json

from hackle.entities import *


class Workspace(object):
    def __init__(self, data):
        json_data = json.loads(data)

        self.bucket_id_map = self._bucket_id_map(json_data.get('buckets', []))
        self.experiment_key_map = self._experiment_key_map('AB_TEST', json_data.get('experiments', []))
        self.feature_flag_key_map = self._experiment_key_map('FEATURE_FLAG', json_data.get('featureFlags', []))
        self.event_type_key_map = self._event_type_key_map(json_data.get('events', []))
        self.segment_key_map = self._segment_key_map(json_data.get('segments', []))

    def get_experiment_or_none(self, experiment_key):
        return self.experiment_key_map.get(experiment_key)

    def get_feature_flag_or_none(self, feature_key):
        return self.feature_flag_key_map.get(feature_key)

    def get_bucket_or_none(self, bucket_id):
        return self.bucket_id_map.get(bucket_id)

    def get_event_type_or_none(self, event_key):
        return self.event_type_key_map.get(event_key)

    def get_segment_or_none(self, segment_key):
        return self.segment_key_map.get(segment_key)

    @staticmethod
    def _bucket_id_map(buckets_data):
        bucket_id_map = {}
        for bucket_data in buckets_data:
            slots = []

            for slot_data in bucket_data['slots']:
                slots.append(
                    Slot(
                        start_inclusive=slot_data['startInclusive'],
                        end_exclusive=slot_data['endExclusive'],
                        variation_id=slot_data['variationId']
                    )
                )

            bucket_id_map[bucket_data['id']] = Bucket(
                seed=bucket_data['seed'],
                slot_size=bucket_data['slotSize'],
                slots=slots
            )
        return bucket_id_map

    @staticmethod
    def _experiment_key_map(experiment_type, experiments_data):
        experiment_key_map = {}
        for experiment_data in experiments_data:
            experiment = Workspace._experiment(experiment_type, experiment_data)
            if experiment:
                experiment_key_map[experiment_data['key']] = experiment
        return experiment_key_map

    @staticmethod
    def _experiment(type, experiment_data):

        execution_data = experiment_data['execution']
        status = Workspace._experiment_status_or_none(execution_data['status'])
        if not status:
            return None

        variations = []
        for variation_data in experiment_data['variations']:
            variation = Variation(
                id=variation_data['id'],
                key=variation_data['key'],
                is_dropped=variation_data['status'] == 'DROPPED'
            )
            variations.append(variation)

        user_overrides = {}
        for override_data in execution_data['userOverrides']:
            user_overrides[override_data['userId']] = override_data['variationId']

        return Experiment(
            id=experiment_data['id'],
            key=experiment_data['key'],
            type=type,
            status=status,
            version=experiment_data['version'],
            variations=variations,
            user_overrides=user_overrides,
            segment_overrides=Workspace._target_rules(execution_data.get('segmentOverrides', []),
                                                      TargetingTypes.IDENTIFIER),
            target_audiences=Workspace._targets(execution_data.get('targetAudiences', []), TargetingTypes.PROPERTY),
            target_rules=Workspace._target_rules(execution_data.get('targetRules', []), TargetingTypes.PROPERTY),
            default_rule=Workspace._target_action(execution_data['defaultRule']),
            winner_variation_id=experiment_data.get('winnerVariationId')
        )

    @staticmethod
    def _experiment_status_or_none(execution_status):
        if execution_status == 'READY':
            return 'DRAFT'
        elif execution_status == 'RUNNING':
            return 'RUNNING'
        elif execution_status == 'PAUSED':
            return 'PAUSED'
        elif execution_status == 'STOPPED':
            return 'COMPLETED'
        else:
            return None

    @staticmethod
    def _target_or_none(target_data, targeting_type):
        conditions = []

        for condition_data in target_data['conditions']:
            condition = Workspace._condition_or_none(condition_data, targeting_type)
            if condition:
                conditions.append(condition)

        if not conditions:
            return None

        return Target(conditions)

    @staticmethod
    def _condition_or_none(condition_data, targeting_type):

        target_key = Workspace._target_key(condition_data['key'])

        if not targeting_type.supports(target_key.type):
            return None

        target_match = Workspace._target_match(condition_data['match'])

        return TargetCondition(
            key=target_key,
            match=target_match
        )

    @staticmethod
    def _target_key(target_key_data):
        return TargetKey(
            type=target_key_data['type'],
            name=target_key_data['name']
        )

    @staticmethod
    def _target_match(target_match_data):
        return TargetMatch(
            type=target_match_data['type'],
            operator=target_match_data['operator'],
            value_type=target_match_data['valueType'],
            values=target_match_data['values']
        )

    @staticmethod
    def _target_action(target_action_data):
        return TargetAction(
            type=target_action_data['type'],
            variation_id=target_action_data.get('variationId'),
            bucket_id=target_action_data.get('bucketId')
        )

    @staticmethod
    def _target_rule_or_none(target_rule_data, targeting_type):
        target = Workspace._target_or_none(target_rule_data['target'], targeting_type)
        if not target:
            return None

        action = Workspace._target_action(target_rule_data['action'])

        return TargetRule(
            target=target,
            action=action
        )

    @staticmethod
    def _targets(targets_data, targeting_type):
        targets = []
        for target_data in targets_data:
            target = Workspace._target_or_none(target_data, targeting_type)
            if not target:
                continue
            targets.append(target)
        return targets

    @staticmethod
    def _target_rules(target_rules_data, targeting_type):
        target_rules = []
        for target_rule_data in target_rules_data:
            target_rule = Workspace._target_rule_or_none(target_rule_data, targeting_type)
            if not target_rule:
                continue
            target_rules.append(target_rule)
        return target_rules

    @staticmethod
    def _event_type_key_map(event_types_data):
        event_type_key_map = {}
        for event_type_data in event_types_data:
            event_type_key_map[str(event_type_data['key'])] = EventType(event_type_data['id'],
                                                                        event_type_data['key'])
        return event_type_key_map

    @staticmethod
    def _segment_key_map(segments_data):
        _segment_key_map = {}
        for segment_data in segments_data:
            segment = Workspace._segment(segment_data)
            _segment_key_map[segment.key] = segment
        return _segment_key_map

    @staticmethod
    def _segment(segment_data):
        return Segment(
            id=segment_data['id'],
            key=segment_data['key'],
            type=segment_data['type'],
            targets=Workspace._targets(segment_data['targets'], TargetingTypes.SEGMENT)
        )
