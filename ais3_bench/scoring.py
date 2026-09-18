"""Pure flag matching for custom tasks; published scores are never rewritten."""

import re

FLAG_RE = re.compile(r"[A-Za-z0-9_]{2,}\{[^}]*\}")


def flag_tokens(submission):
    return set(FLAG_RE.findall(submission or ""))


def exact_flag_match(submission, target):
    """Compare flag-token sets without Unicode normalization or case folding.

    Prose around the token and repeated copies of one token are accepted.
    Two distinct candidates fail. This is not whole-submission equality.
    """
    return flag_tokens(submission) == {target.strip()}
