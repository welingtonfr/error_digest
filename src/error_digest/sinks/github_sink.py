from pydantic.main import BaseModel


class GithubSink(BaseModel):
    def write(self, title: str, body: str, labels: list[str]):
        pass
    def comment(self, issue_id: str, content: str):
        pass
