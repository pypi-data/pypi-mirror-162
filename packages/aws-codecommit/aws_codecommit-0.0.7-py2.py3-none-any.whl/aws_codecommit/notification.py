# -*- coding: utf-8 -*-

"""
The core of CI/CD on AWS CodeCommit / CodeBuild.

You can create an AWS CodeCommit notification event rule, and send those events
to AWS SNS topic, then use an AWS Lambda function to subscript the SNS topic,
use this library to parse the data, and use if else condition to decide when
to trigger CI build job.

This solution requires >= Python3.8 because of the ``cached_property``
Since it is only used in the AWS Lambda Function, there's no need to use
this inside of your application code.
"""

from typing import List, Tuple
import dataclasses

from .compat import need_cached_property

if need_cached_property:  # pragma: no cover
    from cached_property import cached_property
else:  # pragma: no cover
    from functools import cached_property

try:
    from .cc_client import get_commit_message_and_committer
except ImportError:  # pragma: no cover
    pass
except:  # pragma: no cover
    raise

# ------------------------------------------------------------------------------
# Act 1. Semantic Branch
# ------------------------------------------------------------------------------
_ACT_1_SEMANTIC_BRANCH = None

MAIN_BRANCH = ["master", "main"]


def is_main_branch(name: str) -> bool:
    return name in MAIN_BRANCH


def is_certain_semantic_branch(name: str, words: List[str]) -> bool:
    flag = False
    for word in words:
        flag = flag or name.startswith(f"{word}/")
        flag = flag or (name == word)
    return flag


def is_develop_branch(name: str) -> bool:
    return is_certain_semantic_branch(name, ["dev", "develop"])


def is_feature_branch(name: str) -> bool:
    return is_certain_semantic_branch(name, ["feat", "feature"])


def is_release_branch(name: str) -> bool:
    return is_certain_semantic_branch(name, ["rls", "release"])


def is_hotfix_branch(name: str) -> bool:
    return is_certain_semantic_branch(name, ["fix", "hotfix"])


# ------------------------------------------------------------------------------
# Act 2. Semantic Commit
# ------------------------------------------------------------------------------
_ACT_2_SEMANTIC_COMMIT = None


class SemanticCommitEnum:
    """
    Semantic commit message can help CI to determine what you want to do.
    It is a good way to allow developer controls the CI behavior with small
    effort.
    """

    chore = "chore"  # house cleaning, do nothing
    feat = "feat"  # feature, message can be automatically picked up in description
    build = "build"  # build artifacts
    pub = "pub"  # publish artifacts
    test = "test"  # run all test
    utest = "utest"  # run unit test
    itest = "itest"  # run integration test
    ltest = "ltest"  # run load test
    rls = "rls"  # release
    fix = "fix"  # fix something


valid_commit_action_list = [
    v for k, v in SemanticCommitEnum.__dict__.items() if not k.startswith("_")
]
valid_commit_action_set = set(valid_commit_action_list)


def _parse_commit_message(msg: str) -> List[str]:
    if msg.strip().lower() in valid_commit_action_set:
        return [
            msg.strip().lower(),
        ]

    words = [
        word.strip().lower() for word in msg.split(":")[0].split(",") if word.strip()
    ]
    return [word for word in words if word in valid_commit_action_set]


def parse_commit_message(msg: str) -> List[str]:
    try:
        return _parse_commit_message(msg)
    except:  # pragma: no cover
        return []


# ------------------------------------------------------------------------------
# Act 3. Declare CodeCommit Event Data Model
# ------------------------------------------------------------------------------
_ACT_3_DECLARE_CODECOMMIT_EVENT_DATA_MODEL = None


class CodeCommitEventTypeEnum:
    """
    Enumerate common CodeCommit notification event type.

    It is the value of the :meth:`CodeCommitEvent.event_type` method.
    """

    commit_to_branch = "commit_to_branch"
    commit_to_branch_from_merge = "commit_to_branch_from_merge"
    create_branch = "create_branch"
    delete_branch = "delete_branch"
    pr_created = "pr_created"
    pr_closed = "pr_closed"
    pr_updated = "pr_updated"
    pr_merged = "pr_merged"
    comment_on_pr_created = "comment_on_pr_created"
    comment_on_pr_updated = "comment_on_pr_updated"
    reply_to_comment = "reply_to_comment"
    approve_pr = "approve_pr"
    approve_rule_override = "approve_rule_override"
    unknown = "unknown"


@dataclasses.dataclass
class CodeCommitEvent:
    """
    Data container class to represent a CodeCommit notification event.
    """

    afterCommitId: str = ""
    approvalStatus: str = ""
    author: str = ""
    beforeCommitId: str = ""
    callerUserArn: str = ""
    commentId: str = ""
    commitId: str = ""
    creationDate: str = ""
    destinationCommit: str = ""
    destinationCommitId: str = ""
    destinationReference: str = ""
    event: str = ""
    isMerged: str = ""
    inReplyTo: str = ""
    lastModifiedDate: str = ""
    mergeOption: str = ""
    notificationBody: str = ""
    oldCommitId: str = ""
    overrideStatus: str = ""
    pullRequestId: str = ""
    pullRequestStatus: str = ""
    referenceFullName: str = ""
    referenceName: str = ""
    referenceType: str = ""
    repositoryId: str = ""
    repositoryName: str = ""
    revisionId: str = ""
    sourceCommit: str = ""
    sourceCommitId: str = ""
    sourceReference: str = ""
    title: str = ""
    aws_account_id: str = ""
    aws_region: str = ""

    @classmethod
    def from_event(cls, event: dict) -> "CodeCommitEvent":
        kwargs = event["detail"].copy()
        if "repositoryNames" in kwargs:
            kwargs["repositoryName"] = kwargs.pop("repositoryNames")[0]
        repo_arn = event["resources"][0]
        parts = repo_arn.split(":")
        kwargs["aws_account_id"] = parts[4]
        kwargs["aws_region"] = parts[3]
        return cls(**kwargs)

    def to_env_var(self, prefix="") -> dict:
        return {(prefix + k).upper(): v for k, v in dataclasses.asdict(self).items()}

    @classmethod
    def from_env_var(cls, env_var: dict, prefix="") -> "CodeCommitEvent":
        field_set = {field.name for field in dataclasses.fields(cls)}
        kwargs = dict()
        for field_name in field_set:
            key = (prefix + field_name).upper()
            if key in env_var:
                kwargs[field_name] = env_var[key]
        return cls(**kwargs)

    @cached_property
    def event_type(self) -> str:
        if self.event == "referenceUpdated":
            if self.mergeOption:
                return CodeCommitEventTypeEnum.commit_to_branch_from_merge
            else:
                return CodeCommitEventTypeEnum.commit_to_branch
        elif self.event == "referenceCreated":
            return CodeCommitEventTypeEnum.create_branch
        elif self.event == "referenceDeleted":
            return CodeCommitEventTypeEnum.delete_branch
        elif self.event == "pullRequestCreated":
            if self.isMerged == "False" and self.pullRequestStatus == "Open":
                return CodeCommitEventTypeEnum.pr_created
            else:  # pragma: no cover
                return CodeCommitEventTypeEnum.unknown
        elif (
            self.event == "pullRequestStatusChanged"
            and self.pullRequestStatus == "Closed"
        ):
            return CodeCommitEventTypeEnum.pr_closed
        elif self.event == "pullRequestSourceBranchUpdated":
            return CodeCommitEventTypeEnum.pr_updated
        elif (
            self.event == "pullRequestMergeStatusUpdated"
            and self.isMerged == "True"
            and self.pullRequestStatus == "Closed"
        ):
            return CodeCommitEventTypeEnum.pr_merged
        elif self.event == "commentOnPullRequestCreated":
            if self.inReplyTo:
                return CodeCommitEventTypeEnum.reply_to_comment
            else:
                return CodeCommitEventTypeEnum.comment_on_pr_created
        elif self.event == "commentOnPullRequestUpdated":
            if self.inReplyTo:
                return CodeCommitEventTypeEnum.reply_to_comment
            else:
                return CodeCommitEventTypeEnum.comment_on_pr_updated
        elif (
            self.event == "pullRequestApprovalStateChanged"
            and self.approvalStatus == "APPROVE"
        ):
            return CodeCommitEventTypeEnum.approve_pr
        elif self.event == "pullRequestApprovalRuleOverridden":
            return CodeCommitEventTypeEnum.approve_rule_override
        else:  # pragma: no cover
            return CodeCommitEventTypeEnum.unknown

    @cached_property
    def event_description(self) -> str:  # pragma: no cover
        if self.is_commit:
            return (
                f"commit to {self.source_branch!r} branch, "
                f"commit id is {self.source_commit}, "
                f"commit message is {self.commit_message}."
            )
        elif self.is_pr:
            return (
                f"{self.event_type} "
                f"from {self.source_branch!r} branch to "
                f"{self.target_branch!r} branch, "
                f"commit id is {self.source_commit}, "
                f"commit message is {self.commit_message}."
            )
        elif self.is_comment:
            return (
                f"comment on pull request {self.pullRequestId!r} "
                f"comment id is {self.commentId!r}"
            )
        else:
            return ""

    # test Event Type
    @cached_property
    def is_commit_to_branch(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.commit_to_branch

    @cached_property
    def is_commit_to_branch_from_merge(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.commit_to_branch_from_merge

    @cached_property
    def is_commit(self) -> bool:
        return self.is_commit_to_branch or self.is_commit_to_branch_from_merge

    @cached_property
    def is_create_branch(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.create_branch

    @cached_property
    def is_delete_branch(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.delete_branch

    @cached_property
    def is_pr_created(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.pr_created

    @cached_property
    def is_pr_closed(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.pr_closed

    @cached_property
    def is_pr_update(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.pr_updated

    @cached_property
    def is_pr_merged(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.pr_merged

    @cached_property
    def is_comment_on_pr_created(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.comment_on_pr_created

    @cached_property
    def is_comment_on_pr_updated(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.comment_on_pr_updated

    @cached_property
    def is_reply_to_comment(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.reply_to_comment

    @cached_property
    def is_comment(self) -> bool:
        return self.is_comment_on_pr_created or self.is_reply_to_comment

    @cached_property
    def is_approve_pr(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.approve_pr

    @cached_property
    def is_approve_rule_override(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.approve_rule_override

    @cached_property
    def is_pr(self) -> bool:
        return (
            self.is_pr_created
            or self.is_pr_update
            or self.is_pr_merged
            or self.is_pr_closed
        )

    @cached_property
    def is_pr_created_or_updated(self) -> bool:
        return self.is_pr_created or self.is_pr_update

    # additional property
    @cached_property
    def repo_name(self) -> str:
        return self.repositoryName

    @cached_property
    def source_branch(self) -> str:
        if self.is_pr:
            return self.sourceReference.replace("refs/heads/", "", 1)
        elif self.is_commit:
            return self.referenceName
        elif self.is_comment:  # pragma: no cover
            return ""
        elif self.is_approve_pr or self.is_approve_rule_override:
            return self.sourceReference.replace("refs/heads/", "", 1)
        else:  # pragma: no cover
            return ""

    @cached_property
    def source_commit(self) -> str:
        if self.is_pr:
            return self.sourceCommit
        elif self.is_commit:
            return self.commitId
        elif self.is_comment:
            return self.afterCommitId
        elif self.is_approve_pr or self.is_approve_rule_override:
            return self.sourceCommit
        else:  # pragma: no cover
            return ""

    @cached_property
    def target_branch(self) -> str:
        if self.is_pr:
            return self.destinationReference.replace("refs/heads/", "", 1)
        elif self.is_approve_pr or self.is_approve_rule_override:
            return self.destinationReference.replace("refs/heads/", "", 1)
        else:  # pragma: no cover
            return ""

    @cached_property
    def target_commit(self) -> str:
        if self.is_pr:
            return self.destinationCommit
        elif self.is_commit:
            return self.oldCommitId
        elif self.is_comment:
            return self.beforeCommitId
        elif self.is_approve_pr or self.is_approve_rule_override:
            return self.destinationCommit
        else:  # pragma: no cover
            return ""

    @cached_property
    def _source_commit_message_and_committer(self) -> Tuple[str, str]:  # pragma: no cover
        return get_commit_message_and_committer(
            repo_name=self.repo_name,
            commit_id=self.source_commit,
        )

    @cached_property
    def source_commit_message(self) -> str:  # pragma: no cover
        return self._source_commit_message_and_committer[0]

    @cached_property
    def commit_message(self) -> str:  # pragma: no cover
        return self.source_commit_message

    @cached_property
    def source_committer_name(self) -> str:  # pragma: no cover
        return self._source_commit_message_and_committer[1]

    @cached_property
    def committer_name(self) -> str:  # pragma: no cover
        return self.source_committer_name

    @cached_property
    def pr_id(self) -> str:
        return self.pullRequestId

    @cached_property
    def pr_status(self) -> str:
        return self.pullRequestStatus

    @cached_property
    def pr_is_open(self) -> bool:
        return self.pr_status == "Open"

    @cached_property
    def pr_is_merged(self) -> bool:
        return self.isMerged == "True"

    # test branch name
    @cached_property
    def source_is_main_branch(self) -> bool:
        return is_main_branch(self.source_branch)

    @cached_property
    def source_is_develop_branch(self) -> bool:
        return is_develop_branch(self.source_branch)

    @cached_property
    def source_is_feature_branch(self) -> bool:
        return is_feature_branch(self.source_branch)

    @cached_property
    def source_is_release_branch(self) -> bool:
        return is_release_branch(self.source_branch)

    @cached_property
    def source_is_hotfix_branch(self) -> bool:
        return is_hotfix_branch(self.source_branch)

    @cached_property
    def is_main_branch(self) -> bool:
        return self.source_is_main_branch

    @cached_property
    def is_develop_branch(self) -> bool:
        return self.source_is_develop_branch

    @cached_property
    def is_feature_branch(self) -> bool:
        return self.source_is_feature_branch

    @cached_property
    def is_release_branch(self) -> bool:
        return self.source_is_release_branch

    @cached_property
    def is_hotfix_branch(self) -> bool:
        return self.source_is_hotfix_branch

    @cached_property
    def target_is_main_branch(self) -> bool:
        return is_main_branch(self.target_branch)

    @cached_property
    def target_is_develop_branch(self) -> bool:
        return is_develop_branch(self.target_branch)

    @cached_property
    def target_is_feature_branch(self) -> bool:
        return is_feature_branch(self.target_branch)

    @cached_property
    def target_is_release_branch(self) -> bool:
        return is_release_branch(self.target_branch)

    @cached_property
    def target_is_hotfix_branch(self) -> bool:
        return is_hotfix_branch(self.target_branch)

    @cached_property
    def is_pr_from_develop_to_main(self) -> bool:
        return (
            self.is_pr
            and self.source_is_develop_branch
            and self.target_is_main_branch
        )

    @cached_property
    def is_pr_from_feature_to_main(self) -> bool:
        return (
            self.is_pr
            and self.source_is_feature_branch
            and self.target_is_main_branch
        )

    @cached_property
    def is_pr_from_hotfix_to_main(self) -> bool:
        return (
            self.is_pr
            and self.source_is_hotfix_branch
            and self.target_is_main_branch
        )

    # test commit message
    @cached_property
    def is_feat_commit(self) -> bool:
        return SemanticCommitEnum.feat in parse_commit_message(self.commit_message)

    @cached_property
    def is_utest_commit(self) -> bool:
        return SemanticCommitEnum.utest in parse_commit_message(self.commit_message)

    @cached_property
    def is_itest_commit(self) -> bool:
        return SemanticCommitEnum.itest in parse_commit_message(self.commit_message)

    @cached_property
    def is_ltest_commit(self) -> bool:
        return SemanticCommitEnum.ltest in parse_commit_message(self.commit_message)

    @cached_property
    def is_test_commit(self) -> bool:
        acts = parse_commit_message(self.commit_message)
        return (
            SemanticCommitEnum.utest in acts
            or SemanticCommitEnum.itest in acts
            or SemanticCommitEnum.ltest in acts
        )

    @cached_property
    def is_build_commit(self) -> bool:
        return SemanticCommitEnum.build in parse_commit_message(self.commit_message)

    @cached_property
    def is_pub_commit(self) -> bool:
        return SemanticCommitEnum.pub in parse_commit_message(self.commit_message)

    @cached_property
    def is_rls_commit(self) -> bool:
        return SemanticCommitEnum.rls in parse_commit_message(self.commit_message)

    @cached_property
    def is_fix_commit(self) -> bool:
        return SemanticCommitEnum.fix in parse_commit_message(self.commit_message)
