import os

import gitlab
from gitlab.v4.objects import ProjectIssue, Project

from ticket_cross_check.gitlab_models import GitlabIssue


class GitlabConnector:
    def __init__(self, personal_api_token: str, project_id: str):
        """
        Create Gitlab instance with token and project
        :param personal_api_token:
        :param project_id:
        """
        assert personal_api_token
        assert project_id
        self.project_id = project_id
        self.__gitlab = gitlab.Gitlab(private_token=personal_api_token)

    @staticmethod
    def factory() -> "GitlabConnector":
        personal_api_token = os.environ['PRIVATE_TOKEN']
        project_id = os.getenv('PROJECT_ID')
        if not project_id:
            # if project is not defined, assume current project
            project_id = os.environ['CI_PROJECT_ID']
        return GitlabConnector(personal_api_token, project_id)

    def get_issues(self) -> set[GitlabIssue]:
        issues = self.__gitlab.projects.get(self.project_id).issues.list(get_all=True)
        return self._convert_issues(issues)

    @staticmethod
    def _convert_issues(issue_json: list[ProjectIssue]) -> set[GitlabIssue]:
        result = set()
        for raw_req in issue_json:
            result.add(GitlabIssue.from_project_issue(raw_req))
        return result

    @staticmethod
    def _convert_issues_from_dict(issue_json: list[dict]) -> set[GitlabIssue]:
        result = set()
        for raw_req in issue_json:
            result.add(GitlabIssue(**raw_req))
        return result

    def get_project(self) -> Project:
        """Get GitlabProject info from API"""
        rpi = self.__gitlab.projects.get(self.project_id)
        return rpi
