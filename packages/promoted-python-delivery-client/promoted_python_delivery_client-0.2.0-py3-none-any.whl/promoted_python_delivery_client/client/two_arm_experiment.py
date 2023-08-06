import hashlib
from typing import Optional
from promoted_python_delivery_client.model.cohort_arm import CohortArm
from promoted_python_delivery_client.model.cohort_membership import CohortMembership


class TwoArmExperiment:
    def __init__(self,
                 cohort_id: str,
                 num_active_control_buckets: int,
                 num_control_buckets: int,
                 num_active_treatment_buckets: int,
                 num_treatment_buckets: int) -> None:
        if not cohort_id.strip():
            raise ValueError("Cohort ID must be non-empty")

        if num_control_buckets < 0:
            raise ValueError("Control buckets must be positive")

        if num_treatment_buckets < 0:
            raise ValueError("Treatment buckets must be positive")

        if num_active_control_buckets < 0 or num_active_control_buckets > num_control_buckets:
            raise ValueError("Active control buckets must be between 0 and the total number of control buckets")

        if num_active_treatment_buckets < 0 or num_active_treatment_buckets > num_treatment_buckets:
            raise ValueError("Active treatment buckets must be between 0 and the total number of treatment buckets")

        self.cohort_id = cohort_id
        self.cohort_id_hash = _do_hash(cohort_id)
        self.num_active_control_buckets = num_active_control_buckets
        self.num_control_buckets = num_control_buckets
        self.num_active_treatment_buckets = num_active_treatment_buckets
        self.num_treatment_buckets = num_treatment_buckets
        self.num_total_buckets = num_treatment_buckets + num_control_buckets

    def check_membership(self, user_id: str) -> Optional[CohortMembership]:
        hash_code = _combine_hash(_do_hash(user_id), self.cohort_id_hash)
        bucket = abs(hash_code) % self.num_total_buckets
        if bucket < self.num_active_control_buckets:
            return CohortMembership(cohort_id=self.cohort_id, arm=CohortArm.CONTROL)

        if (self.num_control_buckets <= bucket) and (bucket < (self.num_control_buckets + self.num_active_treatment_buckets)):
            return CohortMembership(cohort_id=self.cohort_id, arm=CohortArm.TREATMENT)

        return None


def _do_hash(val: str) -> int:
    """Generate a stable int hash for a string.

    Currently we're using md5 but have this wrapper to allow for swapping in a faster implementation later.

    Args:
        val (str): the value to hash

    Returns:
        int: a stable int
    """
    a = hashlib.md5(val.encode())
    b = a.hexdigest()
    return int(b, 16)


def _combine_hash(first: int, second: int) -> int:
    h = 17
    h = h * 31 + first
    h = h * 31 + second
    return h


def create_50_50_two_arm_experiment_config(cohort_id: str,
                                           control_percent: int,
                                           treatment_percent: int) -> TwoArmExperiment:
    if control_percent < 0 or control_percent > 50:
        raise ValueError("Control percent must be in the range [0, 50]")
    if treatment_percent < 0 or treatment_percent > 50:
        raise ValueError("Treatment percent must be in the range [0, 50]")
    return TwoArmExperiment(cohort_id,
                            control_percent,
                            50,
                            treatment_percent,
                            50)
