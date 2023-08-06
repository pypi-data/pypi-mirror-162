import os

import pytest

from ticket_cross_check.gitlab_connector import GitlabConnector
from ticket_cross_check.gitlab_models import GitlabIssue


def need_token(func):
    @pytest.mark.skipif(os.getenv('PRIVATE_TOKEN') is None, reason="Need gitlab private token %s" % os.environ)
    def myfunc(*args, **kwargs):
        return func(*args, **kwargs)

    return myfunc


def need_tcc_as_project(func):
    """This thest would need the ticket cross-check gilab project to be accessible during test"""
    TCC_PID = 38031020

    @pytest.mark.skipif(os.getenv('PROJECT_ID') is TCC_PID or os.getenv('CI_PROJECT_ID') is TCC_PID,
                        reason="Need access to TCC project")
    def myfunc(*args, **kwargs):
        return func(*args, **kwargs)

    return myfunc


def gitlab_connector():
    try:
        return GitlabConnector.factory()
    finally:
        pass


@need_token
def test_init_from_env():
    gc = GitlabConnector(personal_api_token=os.getenv('PRIVATE_TOKEN'), project_id=os.getenv('PROJECT_ID'))
    assert isinstance(gc, GitlabConnector)


@need_token
def test_factory():
    assert isinstance(gitlab_connector(), GitlabConnector)


@need_token
def test_get_issues():
    result = gitlab_connector().get_issues()
    assert result
    assert isinstance(result, set)
    assert isinstance(result.pop(), GitlabIssue)


@need_token
@need_tcc_as_project
def test_issue_labels_exist_in_gitlab_project():
    result = gitlab_connector().get_project().labels.list()
    labelnames = [label.name for label in result]
    assert 'ignore' in labelnames
    assert 'ignore_doc' in labelnames


@need_token
@need_tcc_as_project
def test_isses_with_labels_exist():
    ignore_issue = gitlab_connector().get_project().issues.list(labels=['ignore'])
    assert 1 == len(ignore_issue)
    assert 'ignore' in ignore_issue[0].labels
    assert ['ignore'] == ignore_issue[0].labels
