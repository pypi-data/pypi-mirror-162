from __future__ import annotations
from typing import List


class Job:
    def __init__(
        self,
        id: str = None,
        child_jobs: List[Job] = None,
        remote_job_id: str = None,
        slug: str = None,
        resource: str = None,
        status: str = None,
        is_terminal_state: str = None,
        remote_status: str = None,
        job_data_schema: str = None,
        job_data: dict = None,
    ) -> None:
        self.id = id
        self.child_jobs = child_jobs
        self.remote_job_id = remote_job_id
        self.slug = slug
        self.resource = resource
        self.status = status
        self.is_terminal_state = is_terminal_state
        self.remote_status = remote_status
        self.job_data_schema = job_data_schema
        self.job_data = job_data

    @classmethod
    def from_dict(cls, res: dict):
        j = Job()
        j.id = res["id"]
        j.remote_job_id = res["remoteJobId"]
        j.slug = res["slug"]
        j.status = res["status"]
        j.is_terminal_state = res["isTerminalState"]
        j.remote_status = res["remoteStatus"]
        j.job_data_schema = res["jobDataSchema"]
        j.job_data = res["jobData"]
        if "childJobs" in res:
            for _, cj in res["childJobs"]:
                j.child_jobs.append(Job().from_response(cj))
        return j


class File:
    def __init__(
        self,
        id: str = None,
        slug: str = None,
        label: str = None,
        file_name: str = None,
        url: str = None,
    ) -> None:
        self.id = id
        self.slug = slug
        self.label = label
        self.file_name = file_name
        self.url = url

    @classmethod
    def from_dict(cls, d: dict) -> File:
        f = File()
        f.id = d["id"]
        f.slug = d["slug"]
        f.label = d["label"]
        f.url = d["url"]
        f.file_name = d["fileName"]
        return f
