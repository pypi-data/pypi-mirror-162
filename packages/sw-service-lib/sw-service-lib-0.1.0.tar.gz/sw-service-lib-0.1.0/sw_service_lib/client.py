import io
import os
from typing import Any
import aiofiles
import aiohttp
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from sw_service_lib.billing import BillingTransaction

from sw_service_lib.job import File, Job
from sw_service_lib.resource import (
    Resource,
    ResourceConfiguration,
    ResourceConfigurationValueType,
)

# Default url and define setter
__root = "/services"
__url = "https://api.strangeworks.com"
__headers = {}


def set_url(url: str):
    """ """
    global __url
    __url = url


def set_custom_headers(header: dict):
    global __headers
    __headers = header


def add_header(key: str, value: Any):
    global __headers
    __headers[key] = value


# Create a new endpoint for each request, enforces narrow scope for auth
def __new_client(auth: str) -> Client:
    add_header(key="Authorization", value=auth)
    return Client(transport=AIOHTTPTransport(url=__url + __root, headers=__headers))


"""
BILLING CLIENT
"""


def request_billing_approval(auth: str, amount: float, currency: str) -> bool:
    """
    precheck billing approval to ensure a
    """
    __request_billing_approval_query = gql(
        """
        query requestBillingApproval ($amount: Float!, $currency: Currency!) {
            requestBillingApproval(amount: $amount, currency: $currency){
                isApproved
                rejectionMessage
            }
        }
    """
    )
    client = __new_client(auth)
    res = client.execute(
        __request_billing_approval_query,
        variable_values={"amount": amount, "currency": currency},
    )
    if res["requestBillingApproval"]["isApproved"] == False:
        raise RuntimeError(res["rejectionMessage"])
    return True


def create_billing_transaction(
    auth: str,
    job_slug: str,
    amount: float,
    unit: str,
    description: str,
    memo: str = None,
) -> BillingTransaction:
    """
    create a billing transaction associated to the resource
    """
    __create_billing_transaction_mutation = gql(
        """
        mutation createBillingTransaction ($jobSlug: String!, $amount: Float!, $unit: Currency!, $description: String!, $memo: String) {
            createBillingTransaction(input: {
                jobSlug: $jobSlug,
                amount: $amount,
                unit: $unit,
                description: $description,
                memo: $memo,
            }) {
                billingTransaction {
                    id
                    status
                    amount
                    unit
                    description
                    memo
                }
            }
        }
        """
    )
    client = __new_client(auth)
    res = client.execute(
        __create_billing_transaction_mutation,
        variable_values={
            "jobSlug": job_slug,
            "amount": amount,
            "unit": unit,
            "description": description,
            "memo": memo,
        },
    )
    if not res["createBillingTransaction"]:
        raise RuntimeError(res["errors"])
    return BillingTransaction.from_dict(
        res["createBillingTransaction"]["billingTransaction"]
    )


"""
JOB CLIENT
"""


def create_job(
    auth: str,
    parent_job_slug: str = None,
    remote_job_id: str = None,
    member_slug: str = None,
    status: str = None,
    remote_status: str = None,
    job_data_schema: str = None,
    job_data: dict = None,
) -> Job:
    """
    create a job associated with the resource
    """
    __create_job_mutation = gql(
        """
        mutation createJob($parentJobSlug: String, $remoteJobId: String, $memberSlug: String, $status: JobStatus, $remoteStatus: String, $jobDataSchema: String, $jobData: JSON) {
            createJob(input: {
                parentJobSlug: $parentJobSlug,
                remoteJobId: $remoteJobId,
                memberSlug: $memberSlug,
                status: $status,
                remoteStatus: $remoteStatus,
                jobDataSchema: $jobDataSchema,
                jobData: $jobData,
            }) {
                job {
                id
                remoteJobId
                slug
                status
                isTerminalState
                remoteStatus
                jobDataSchema
                jobData
                }
            }
        }
        """
    )
    client = __new_client(auth)
    res = client.execute(
        __create_job_mutation,
        variable_values={
            "parentJobSlug": parent_job_slug,
            "remoteJobId": remote_job_id,
            "memberSlug": member_slug,
            "status": status,
            "remoteStatus": remote_status,
            "jobDataSchema": job_data_schema,
            "jobData": job_data,
        },
    )
    if not res["createJob"]:
        raise RuntimeError(res["errors"])
    return Job.from_dict(res["createJob"]["job"])


def update_job(
    auth: str,
    job_slug: str,
    parent_job_slug: str = None,
    remote_job_id: str = None,
    member_slug: str = None,
    status: str = None,
    remote_status: str = None,
    job_data_schema: str = None,
    job_data: dict = None,
) -> Job:
    """
    update a job owned by the resource
    """
    __update_job_mutation = gql(
        """
        mutation updateJob($jobSlug: String!, $parentJobSlug: String, $remoteJobId: String, $status: JobStatus, $remoteStatus: String, $jobDataSchema: String, $jobData: JSON) {
            updateJob(input: {
                jobSlug: $jobSlug,
                parentJobSlug: $parentJobSlug,
                remoteJobId: $remoteJobId,
                status: $status,
                remoteStatus: $remoteStatus,
                jobDataSchema: $jobDataSchema,
                jobData: $jobData,
            }) {
                job {
                id
                remoteJobId
                slug
                status
                isTerminalState
                remoteStatus
                jobDataSchema
                jobData
                }
            }
        }
        """
    )
    client = __new_client(auth)
    res = client.execute(
        __update_job_mutation,
        variable_values={
            "jobSlug": job_slug,
            "parentJobSlug": parent_job_slug,
            "remoteJobId": remote_job_id,
            "memberSlug": member_slug,
            "status": status,
            "remoteStatus": remote_status,
            "jobDataSchema": job_data_schema,
            "jobData": job_data,
        },
    )
    if not res["updateJob"]:
        raise RuntimeError(res["errors"])
    return Job.from_dict(res["updateJob"]["job"])


def upload_job_file(
    auth: str,
    job_slug: str,
    file_name: str,
    file_path: str = None,
    file_url: str = None,
    should_override_existing_file: bool = False,
) -> File:
    """
    upload a job file either from local disk using file_path or from
    a location using file_url
    """
    __upload_job_file = gql(
        """
        mutation uploadJobFile($jobSlug: String!, $shouldOverrideExistingFile: Boolean!, $file: Upload!, $fileName: String){
            uploadJobFile(
                upload: {jobSlug: $jobSlug, shouldOverrideExistingFile: $shouldOverrideExistingFile, file: $file, fileName: $fileName}
            ) {
                file {
                    id
                    slug
                    label
                    fileName
                    url
                    metaFileType
                    metaDateCreated
                    metaDateModified
                    metaSizeBytes
                    jsonSchema
                    dateCreated
                    dateUpdated
                }
            }
        }
        """
    )
    client = __new_client(auth)

    # upload file from url
    if file_url:

        async def downloaded_file(file_url):
            async with aiohttp.ClientSession() as http_client:
                async with http_client.get(file_url) as resp:
                    return resp

        res = client.execute(
            __upload_job_file,
            variable_values={
                "jobSlug": job_slug,
                "fileName": file_name,
                "shouldOverrideExistingFile": should_override_existing_file,
                "file": downloaded_file(file_url),
            },
            upload_files=True,
        )
        if not res["uploadJobFile"]:
            raise RuntimeError(res["errors"])
        return File.from_dict(res["uploadJobFile"]["file"])

    # throw error if neither file_path nor url are selected
    if not file_path:
        raise RuntimeError(
            "must include either file_path or file_url to upload job file"
        )

    # set up chunking function
    async def file_sender(file_name):
        async with aiofiles.open(file_name, "rb") as f:
            chunk = await f.read(64 * 1024)
            while chunk:
                yield chunk
                chunk = await f.read(64 * 1024)

    # upload file from disk
    res = client.execute(
        __upload_job_file,
        variable_values={
            "fileName": file_name,
            "jobSlug": job_slug,
            "shouldOverrideExistingFile": should_override_existing_file,
            "file": file_sender(file_name=file_path),
        },
        upload_files=True,
    )
    if not res["uploadJobFile"]:
        raise RuntimeError(res["errors"])
    return File.from_dict(res["uploadJobFile"]["file"])


def fetch_job(auth: str, job_slug: str) -> Job:
    """
    fetch a job by its slug, must be owned by
    the resource defined in the auth, though
    child jobs / parent jobs can also be fetched
    as part of the query
    """
    __get_job_query = gql(
        """
        query job ($jobSlug: String!) {
            job(jobSlug: $jobSlug){
                id
                childJobs {
                    id
                }
                remoteJobId
                slug
                status
                isTerminalState
                remoteStatus
                jobDataSchema
                jobData
            }
        }
    """
    )
    client = __new_client(auth)
    res = client.execute(__get_job_query, variable_values={"jobSlug": job_slug})
    if not res["job"]:
        raise RuntimeError(res["error"])
    return Job.from_dict(res["job"])


"""
RESOURCE CLIENT
"""


def store_resource_configuration(
    auth: str,
    key: str,
    config_type: ResourceConfigurationValueType,
    is_editable: bool,
    is_visible: bool,
    value,
) -> ResourceConfiguration:
    """
    store a new resource configuration for the resource
    provided by the auth
    """

    __store_resource_configuration_mutation = gql(
        """
        mutation storeResourceConfiguration($key: String!, $type: ResourceConfigurationValueType!,
        $isEditable: Boolean!, $isVisible: Boolean!, $valueBool: Boolean, $valueString: String,
        $valueSecure: String, $valueInt: Int, $valueJson: String, $valueDate: Time, $valueFloat: Float) {
            storeResourceConfiguration(
                input: { key: $key, type: $type, isEditable: $isEditable,
                isVisible: $isVisible, valueBool: $valueBool, valueString: $valueString,
                valueSecure: $valueSecure, valueInt: $valueInt, valueJson: $valueJson,
                valueDate: $valueDate, valueFloat: $valueFloat
                }
            ) {
                resourceConfiguration {
                    key
                    type
                    valueBool
                    valueString
                    valueSecure
                    valueInt
                    valueJson
                    valueDate
                    valueFloat
                    isEditable
                }
            }
        }
        """
    )

    params = {
        "key": key,
        "type": config_type.name,
        "isEditable": is_editable,
        "isVisible": is_visible,
    }
    if config_type == ResourceConfigurationValueType.BOOL:
        params["valueBool"] = value
    elif config_type == ResourceConfigurationValueType.STRING:
        params["valueString"] = value
    elif config_type == ResourceConfigurationValueType.SECURE:
        params["valueSecure"] = value
    elif config_type == ResourceConfigurationValueType.INT:
        params["valueInt"] = value
    elif config_type == ResourceConfigurationValueType.JSON:
        params["valueJson"] = value
    elif config_type == ResourceConfigurationValueType.DATE:
        params["valueDate"] = value
    elif config_type == ResourceConfigurationValueType.FLOAT:
        params["valueFloat"] = value
    else:
        raise RuntimeError(
            "resource configuration value type must match one of the enums"
        )

    client = __new_client(auth)
    res = client.execute(
        __store_resource_configuration_mutation, variable_values=params
    )
    if not res["storeResourceConfiguration"]:
        raise RuntimeError(res["error"])
    return ResourceConfiguration.from_dict(
        res["storeResourceConfiguration"]["resourceConfiguration"]
    )


def fetch_resource(auth: str) -> Resource:
    """
    fetches the resource w/ configuration from platform
    can only fetch resource associated with auth passed in
    """
    __fetch_resource_query = gql(
        """
        query resource {
            resource{
                resource {
                    id
                    slug
                    name
                    isAvailableToWorkspaceMembers
                    isDisabled
                    isDeleted
                    dateCreated
                    dateUpdated
                }
                configuration {
                    key
                    type
                    valueBool
                    valueString
                    valueSecure
                    valueInt
                    valueJson
                    valueDate
                    valueFloat
                    isEditable
                }
            }
        }
    """
    )
    client = __new_client(auth)
    res = client.execute(__fetch_resource_query)
    if not res["resource"]:
        raise RuntimeError(res["error"])
    return Resource.from_dict(res["resource"])
