import requests
from pydantic import BaseModel


class GithubSink(BaseModel):
    repo: str  # "owner/name"
    token: str
    api_url: str = "https://api.github.com"
    timeout: int = 30

    def write(self, title: str, body: str, labels: list[str]) -> str:
        resp = requests.post(
            f"{self.api_url}/repos/{self.repo}/issues",
            json={"title": title, "body": body, "labels": labels},
            headers=self._headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return str(resp.json()["number"])

    def comment(self, issue_id: str, content: str) -> None:
        resp = requests.post(
            f"{self.api_url}/repos/{self.repo}/issues/{issue_id}/comments",
            json={"body": content},
            headers=self._headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
