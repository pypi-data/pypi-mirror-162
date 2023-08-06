from __future__ import annotations

import os
import time
import logging
import awswrangler as wr
import boto3
import gzip
import pendulum
import python_graphql_client
import pandas as pd
import requests
from time import sleep
from datetime import datetime
from typing import Optional, Dict, List, Union
from tqdm.auto import tqdm
from requests.auth import AuthBase
from sumatra.auth import SDKKeyAuth, CognitoJwtAuth
from sumatra.config import CONFIG

logger = logging.getLogger("sumatra.client")


def parse_timestamp_columns(df, columns):
    df = df.copy()
    for col in columns:
        times = []
        for t in df[col]:
            ts = "NaT"
            try:
                ts = (
                    pendulum.parse(t)
                    .astimezone(pendulum.timezone("UTC"))
                    .to_iso8601_string()
                )
            except:
                pass
            times.append(ts)
        df[col] = times
        df[col] = pd.to_datetime(df[col], unit="ns")
        if df[col].dt.tz is None:
            df[col] = df[col].dt.tz_localize("UTC")
        df[col] = df[col].dt.tz_convert(CONFIG.timezone)
    return df


def tz_convert_timestamp_columns(df):
    df = df.copy()
    for col in df.columns:
        if hasattr(df[col], "dt"):
            try:
                df[col] = df[col].dt.tz_localize("UTC")
            except:
                pass
            df[col] = df[col].dt.tz_convert(CONFIG.timezone)
    return df


def _load_scowl_files(dir: str) -> Dict[str, str]:
    scowls = {}
    for fname in os.listdir(dir):
        if fname.endswith(".scowl"):
            scowl = open(os.path.join(dir, fname)).read()
            scowls[fname] = scowl
    return scowls


def _splitext(path: str):
    fullext = ""
    while True:
        path, ext = os.path.splitext(path)
        if ext:
            fullext = ext + fullext
        else:
            break
    return os.path.basename(path), fullext


class Client:
    """
    Client to connect to Sumatra GraphQL API

    __Humans:__ First, log in via the CLI: `sumatra login`

    __Bots:__ Set the `SUMATRA_INSTANCE` and `SUMATRA_SDK_KEY` environment variables
    """

    def __init__(
        self,
        instance: Optional[str] = None,
        branch: Optional[str] = None,
    ):
        """
        Create connection object.

        Arguments:
            instance: Sumatra instance url, e.g. `yourco.sumatra.ai`. If unspecified, the your config default will be used.
            branch: Set default branch. If unspecified, your config default will be used.
        """
        if instance:
            CONFIG.instance = instance
        if CONFIG.sdk_key:
            auth: AuthBase = SDKKeyAuth()
            endpoint = CONFIG.sdk_graphql_url
        else:
            auth = CognitoJwtAuth()
            endpoint = CONFIG.console_graphql_url

        self._branch = branch or CONFIG.default_branch

        self._gql_client = python_graphql_client.GraphqlClient(
            auth=auth, endpoint=endpoint
        )

    @property
    def instance(self) -> str:
        """
        Instance name from client config, e.g. `'yourco.sumatra.ai'`
        """
        return CONFIG.instance

    @property
    def branch(self) -> str:
        """
        Default branch name
        """
        return self._branch

    @branch.setter
    def branch(self, branch: str) -> None:
        self._branch = branch

    def tenant(self) -> str:
        """
        Return the assigned tenant name for the connected user.

        Returns:
            Tenant name
        """
        logger.debug("Fetching tenant")
        query = """
            query Tenant {
                tenant {
                    key
                }
            }
        """

        ret = self._gql_client.execute(query=query)

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["tenant"]["key"]

    def get_branch(self, branch: Optional[str] = None) -> Dict:
        """
        Return metadata about the branch.

        Arguments:
            branch: Specify a branch other than the client default.

        Returns:
            Branch metadata
        """
        branch = branch or self._branch
        logger.info(f"Getting branch {branch}")
        query = """
            query BranchScowl($id: String!) { 
              branch(id: $id) { id, hash, events, creator, lastUpdated, error } 
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": branch})

        if "errors" in ret:
            raise Exception(f"Error: {ret['errors'][0]['message']}")

        branch = ret["data"]["branch"]
        row = {
            "name": branch["id"],
            "creator": branch["creator"],
            "update_ts": branch["lastUpdated"],
            "event_types": branch["events"],
        }

        if "error" in branch and branch["error"]:
            row["error"] = branch["error"]

        return row

    def clone_branch(self, dest: str, branch: Optional[str] = None) -> None:
        """
        Copy branch to another branch name.

        Arguments:
            dest: Name of branch to be created or overwritten.
            branch: Specify a source branch other than the client default.
        """
        branch = branch or self._branch
        logger.info(f"Cloning branch {branch} to {dest}")
        query = """
            mutation CloneBranch($id: String!, $sourceId: String!) {
                cloneBranch(id: $id, sourceId: $sourceId) { id, creator, lastUpdated, scowl }
              }
        """

        ret = self._gql_client.execute(
            query=query, variables={"id": dest, "sourceId": branch}
        )

        if "errors" in ret:
            raise Exception(f"Error: {ret['errors'][0]['message']}")

    def _put_branch_object(
        self, key: str, scowl: str, branch: Optional[str] = None
    ) -> None:
        branch = branch or self._branch
        logger.info(f"Putting branch object {key} to branch {branch}")
        query = """
              mutation PutBranchObject($branchId: String!, $key: String!, $scowl: String!) {
                putBranchObject(branchId: $branchId, key: $key, scowl: $scowl) { key }
              }
        """

        ret = self._gql_client.execute(
            query=query, variables={"branchId": branch, "key": key, "scowl": scowl}
        )

        if "errors" in ret:
            raise Exception(f"Error: {ret['errors'][0]['message']}")

    def create_branch_from_scowl(self, scowl: str, branch: Optional[str] = None) -> str:
        """
        Create (or overwrite) branch with single file of scowl source code.

        Arguments:
            scowl: Scowl source code as string.
            branch: Specify a source branch other than the client default.

        Returns:
            Name of branch created
        """

        branch = branch or self._branch
        logger.info(f"Creating branch '{branch}' from scowl")
        try:
            self.delete_branch(branch)
        except:
            pass

        self._put_branch_object("main.scowl", scowl, branch)

        b = self.get_branch(branch)
        if "error" in b:
            raise Exception(b["error"])

        return b["name"]

    def create_branch_from_dir(
        self, scowl_dir: Optional[str] = None, branch: Optional[str] = None
    ) -> str:
        """
        Create (or overwrite) branch with local scowl files.

        Arguments:
            scowl_dir: Path to local .scowl files.
            branch: Specify a source branch other than the client default.

        Returns:
            Name of branch created
        """
        scowl_dir = scowl_dir or CONFIG.scowl_dir
        branch = branch or self._branch
        logger.info(f"Creating branch '{branch}' from dir '{scowl_dir}'")

        try:
            self.delete_branch(branch)
        except:
            pass

        scowls = _load_scowl_files(scowl_dir)
        if not scowls:
            raise Exception(
                f"Unable to push local dir. '{scowl_dir}' has no .scowl files."
            )

        for key in scowls:
            self._put_branch_object(key, scowls[key], branch)

        b = self.get_branch(branch)
        if "error" in b:
            raise Exception(b["error"])

        return b["name"]

    def publish_dir(self, scowl_dir: Optional[str] = None) -> None:
        """
        Push local scowl dir to branch and promote to LIVE.

        Arguments:
            scowl_dir: Path to .scowl files. Default: `'.'`
        """
        scowl_dir = scowl_dir or CONFIG.scowl_dir
        logger.info(f"Publishing dir '{scowl_dir}' to LIVE.")
        branch = self.create_branch_from_dir(scowl_dir, "main")
        self.publish_branch(branch)

    def publish_branch(self, branch: Optional[str] = None) -> None:
        """
        Promote branch to LIVE.

        Arguments:
            branch: Specify a branch other than the client default.
        """
        branch = branch or self._branch
        logger.info(f"Publishing '{branch}' branch to LIVE.")
        query = """
            mutation PublishBranch($id: String!) {
                publish(id: $id) {
                    id
                }
            }
        """
        ret = self._gql_client.execute(query=query, variables={"id": branch})

        if "errors" in ret:
            raise Exception(
                f"Error publishing branch '{branch}': {ret['errors'][0]['message']}"
            )

    def publish_scowl(self, scowl: str) -> None:
        """
        Push local scowl source to branch and promote to LIVE.

        Arguments:
            scowl: Scowl source code as string.
        """
        logger.info("Publishing scowl to LIVE.")
        branch = self.create_branch_from_scowl(scowl, "main")
        self.publish_branch(branch)

    def diff_branch_with_live(
        self, branch: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Compare branch to LIVE topology and return diff.

        Arguments:
            branch: Specify a source branch other than the client default.

        Returns:
            Events and features added, redefined, and deleted.
        """

        branch = branch or self._branch
        logger.info(f"Diffing '{branch}' branch against LIVE.")
        query = """
            query Branch($id: String!) {
                branch(id: $id) {
                liveDiff {
                    eventsAdded
                    eventsDeleted
                    topologyDiffs {
                        eventType
                        featuresDeleted
                        featuresAdded
                        featuresRedefined
                        featuresDirtied
                    }
                    warnings
                }
              }
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": branch})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["branch"]["liveDiff"]

    def get_branches(self) -> pd.DataFrame:
        """
        Return all branches and their metadata.

        Returns:
            Branch metadata.
        """
        logger.debug(f"Getting branches")
        query = """
            query BranchList {
                branches {
                    id
                    events
                    error
                    creator
                    lastUpdated
                }
            }
        """

        ret = self._gql_client.execute(query=query)

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        rows = []
        for branch in ret["data"]["branches"]:
            row = {
                "name": branch["id"],
                "creator": branch["creator"],
                "update_ts": branch["lastUpdated"],
                "event_types": branch["events"],
            }
            if branch["error"]:
                row["error"] = branch["error"]

            rows.append(row)
        if not rows:
            return pd.DataFrame(columns=["name", "creator", "update_ts", "event_types"])
        df = pd.DataFrame(rows)
        df = parse_timestamp_columns(df, ["update_ts"])
        return df.sort_values(["creator", "update_ts"], ascending=False).set_index(
            "name"
        )

    def get_live_scowl(self) -> str:
        """
        Return scowl source code for LIVE topology as single cleansed string.

        Returns:
            Scowl source code as string.
        """
        query = """
            query LiveScowl {
                liveBranch { scowl }
            }
        """

        ret = self._gql_client.execute(query=query)

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        scowl = ret["data"]["liveBranch"]["scowl"]
        return scowl

    def delete_branch(self, branch: Optional[str] = None) -> None:
        """
        Delete server-side branch

        Arguments:
            branch: Specify a branch other than the client default.
        """
        branch = branch or self._branch
        logger.info(f"Deleting branch '{branch}'.")
        query = """
            mutation DeleteBranch($id: String!) {
                deleteBranch(id: $id) {
                    id
                }
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": branch})

        if "errors" in ret:
            raise Exception(
                f"Error deleting branch '{branch}': {ret['errors'][0]['message']}"
            )

    def get_inputs_from_feed(
        self,
        start_ts: Optional[Union[pd.Timestamp, str]] = None,
        end_ts: Optional[Union[pd.Timestamp, str]] = None,
        count: Optional[int] = None,
        event_types: Optional[List[str]] = None,
        where: Dict[str, str] = {},
        batch_size: int = 10000,
    ) -> List[Dict]:
        """
        Return the raw input events from the Event Feed.

        Fetches events in descending time order from `end_ts`. May specify `count` or `start_ts`, but not both.

        Arguments:
            start_ts: Earliest event timestamp to fetch (local client timezone). If not specified, `count` will be used instead.
            end_ts: Latest event timestamp to fetch (local client timezone) [default: now].
            count: Number of rows to return (if start_ts not specified) [default: 10].
            event_types: Subset of event types to fetch. [default: all]
            where: Dictionary of equality conditions (all must be true for a match), e.g. {"zipcode": "90210", "email_domain": "gmail.com"}.
            batch_size: Maximum number of records to fetch per GraphQL call.

        Returns:
            List of events: [{"_id": , "_type": , "_time": , [inputs...]}] (in descending time order).
        """

        where = [{"key": k, "value": v} for k, v in where.items()]
        if batch_size < 1 or batch_size > 10000:
            raise Exception(f"batch size: {batch_size} is out of range [1,10000]")
        end_ts = end_ts or str(pendulum.now())
        if isinstance(end_ts, pd.Timestamp):
            end_ts = str(end_ts)
        end_ts = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )

        if event_types is not None:
            event_types = [{"type": t} for t in event_types]

        query = """
        query EventFeed($size: Int!, $end: DateTime!, $eventTypes: [EventSelection], $where: [FeatureFilter]!) {
            events {
                feed(
                    from: 0
                    size: $size
                    end: $end
                    types: $eventTypes
                    where: $where
                ) {
                id
                type
                time
                input
                }
            }
        }
        """
        if start_ts:
            if count:
                raise Exception("specify only one of: start_ts or count")
            if isinstance(start_ts, pd.Timestamp):
                start_ts = str(start_ts)
            start_ts = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
                pendulum.timezone("UTC")
            )

            rows = []
            done = False
            while not done:
                variables = {
                    "size": batch_size,
                    "end": end_ts.to_iso8601_string(),
                    "where": where,
                }
                if event_types:
                    variables["eventTypes"] = event_types
                ret = self._gql_client.execute(
                    query=query,
                    variables=variables,
                )
                if "errors" in ret:
                    raise Exception(ret["errors"][0]["message"])
                new_rows = []
                for event in ret["data"]["events"]["feed"]:
                    event_time = pendulum.parse(event["time"])
                    if event_time < start_ts:
                        done = True
                        break
                    row = {
                        "_id": event["id"],
                        "_type": event["type"],
                        "_time": str(event_time),
                    }
                    row.update(event["input"])
                    new_rows.append(row)
                rows.extend(new_rows)
                if done or not new_rows:
                    break
                end_ts = event_time
            return rows
        else:  # count
            if count is None:
                count = 10
            from_ = 0
            rows = []
            while True:
                size = min(batch_size, count - from_)
                if size <= 0:
                    break
                variables = {
                    "size": size,
                    "end": end_ts.to_iso8601_string(),
                    "where": where,
                }
                if event_types:
                    variables["eventTypes"] = event_types
                ret = self._gql_client.execute(
                    query=query,
                    variables=variables,
                )
                if "errors" in ret:
                    raise Exception(ret["errors"][0]["message"])
                new_rows = []
                for event in ret["data"]["events"]["feed"]:
                    event_time = pendulum.parse(event["time"])
                    row = {
                        "_id": event["id"],
                        "_type": event["type"],
                        "_time": str(event_time),
                    }
                    row.update(event["input"])
                    new_rows.append(row)
                rows.extend(new_rows)
                from_ += size
                if from_ >= count:
                    break
                end_ts = event_time
            return rows

    def get_features_from_feed(
        self,
        event_type: str,
        start_ts: Optional[Union[pd.Timestamp, str]] = None,
        end_ts: Optional[Union[pd.Timestamp, str]] = None,
        count: Optional[int] = None,
        where: Dict[str, str] = {},
        batch_size: int = 10000,
    ) -> pd.DataFrame:
        """
        For a given event type, return the feature values as they were
        calculated at event time.

        Fetches events in descending time order from `end_ts`. May specify `count` or `start_ts`, but not both.

        Arguments:
            event_type: Event type name.
            start_ts: Earliest event timestamp to fetch (local client timezone). If not specified, `count` will be used instead.
            end_ts: Latest event timestamp to fetch (local client timezone) [default: now].
            count: Number of rows to return (if start_ts not specified) [default: 10].
            where: Dictionary of equality conditions (all must be true for a match), e.g. {"zipcode": "90210", "email_domain": "gmail.com"}.
            batch_size: Maximum number of records to fetch per GraphQL call.

        Returns:
            Dataframe: _id, _time, [features...] (in descending time order).
        """

        where = [{"key": k, "value": v} for k, v in where.items()]
        if batch_size < 1 or batch_size > 10000:
            raise Exception(f"batch size: {batch_size} is out of range [1,10000]")
        end_ts = end_ts or str(pendulum.now())
        if isinstance(end_ts, pd.Timestamp):
            end_ts = str(end_ts)
        end_ts = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )

        query = """
        query EventFeed($size: Int!, $end: DateTime!, $eventType: String!, $where: [FeatureFilter]!) {
            events {
                feed(
                    from: 0
                    size: $size
                    end: $end
                    types: [{ type: $eventType, where: $where }]
                ) {
                id
                time
                features
                }
            }
        }
        """
        if start_ts:
            if count:
                raise Exception("specify only one of: start_ts or count")
            if isinstance(start_ts, pd.Timestamp):
                start_ts = str(start_ts)
            start_ts = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
                pendulum.timezone("UTC")
            )

            rows = []
            done = False
            while not done:
                ret = self._gql_client.execute(
                    query=query,
                    variables={
                        "size": batch_size,
                        "end": end_ts.to_iso8601_string(),
                        "eventType": event_type,
                        "where": where,
                    },
                )
                if "errors" in ret:
                    raise Exception(ret["errors"][0]["message"])
                new_rows = []
                for event in ret["data"]["events"]["feed"]:
                    event_time = pendulum.parse(event["time"])
                    if event_time < start_ts:
                        done = True
                        break
                    row = {"_id": event["id"], "_time": event_time}
                    row.update(event["features"])
                    new_rows.append(row)
                rows.extend(new_rows)
                if done or not new_rows:
                    break
                end_ts = event_time
            if not rows:
                return pd.DataFrame(columns=["_id", "_time"])
            df = pd.DataFrame(rows)
            df = tz_convert_timestamp_columns(df)
            return df.set_index("_id")
        else:  # count
            if count is None:
                count = 10
            from_ = 0
            rows = []
            while True:
                size = min(batch_size, count - from_)
                if size <= 0:
                    break
                ret = self._gql_client.execute(
                    query=query,
                    variables={
                        "size": size,
                        "end": end_ts.to_iso8601_string(),
                        "eventType": event_type,
                        "where": where,
                    },
                )
                if "errors" in ret:
                    raise Exception(ret["errors"][0]["message"])
                new_rows = []
                for event in ret["data"]["events"]["feed"]:
                    event_time = pendulum.parse(event["time"])
                    row = {"_id": event["id"], "_time": event_time}
                    row.update(event["features"])
                    new_rows.append(row)
                rows.extend(new_rows)
                from_ += size
                if from_ >= count:
                    break
                end_ts = event_time
            if not rows:
                return pd.DataFrame(columns=["_id", "_time"])
            df = pd.DataFrame(rows)
            df = tz_convert_timestamp_columns(df)
            return df.set_index("_id")

    def get_timelines(self) -> pd.DataFrame:
        """
        Return all timelines and their metadata.

        Returns:
            Timeline metadata.
        """

        logger.debug(f"Getting timelines")
        query = """
            query TimelineList {
                timelines { id, createUser, createTime, metadata { start, end, count, events }, source, state, error }
            }
        """
        ret = self._gql_client.execute(query)
        rows = []
        for timeline in ret["data"]["timelines"]:
            status = timeline["state"]
            row = {
                "name": timeline["id"],
                "creator": timeline["createUser"],
                "create_ts": timeline["createTime"],
                "event_types": timeline["metadata"]["events"],
                "event_count": timeline["metadata"]["count"],
                "start_ts": timeline["metadata"]["start"]
                if timeline["metadata"]["start"] != "0001-01-01T00:00:00Z"
                else "",
                "end_ts": timeline["metadata"]["end"]
                if timeline["metadata"]["end"] != "0001-01-01T00:00:00Z"
                else "",
                "source": timeline["source"],
                "status": status,
                "error": timeline["error"],
            }
            rows.append(row)
        if not rows:
            return pd.DataFrame(
                columns=[
                    "name",
                    "creator",
                    "create_ts",
                    "event_types",
                    "event_count",
                    "start_ts",
                    "end_ts",
                    "source",
                    "status",
                    "error",
                ]
            )
        df = pd.DataFrame(rows)
        df = parse_timestamp_columns(df, ["create_ts", "start_ts", "end_ts"])
        return df.sort_values(["creator", "create_ts"], ascending=False).set_index(
            "name"
        )

    def get_timeline(self, timeline: str) -> pd.Series:
        """
        Return metadata about the timeline.

        Arguments:
            timeline: Timeline name.

        Returns:
            Timeline metadata.
        """
        logger.debug(f"Getting timeline '{timeline}'")
        timelines = self.get_timelines()
        if timeline in timelines.index:
            return timelines.loc[timeline]
        raise Exception(f"Timeline '{timeline}' not found.")

    def delete_timeline(self, timeline: str) -> None:
        """
        Delete timeline

        Arguments:
            timeline: Timeline name.
        """
        logger.info(f"Deleting timeline '{timeline}'.")
        query = """
            mutation DeleteTimeline($id: String!) {
                deleteTimeline(id: $id) {
                    id
                }
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": timeline})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["deleteTimeline"]["id"]

    def infer_schema_from_timeline(self, timeline: str) -> str:
        """
        Attempt to infer the paths and data types of all fields in the timeline's
        input data. Generate the scowl to parse all JSON paths.

        This function helps bootstrap scowl code for new event types, with
        the expectation that most feature names will need to be modified.

        e.g.
        ```
            account_id := $.account.id as int
            purchase_items_0_amount := $.purchase.items[0].amount as float
        ```

        Arguments:
            timeline: Timeline name.

        Returns:
            Scowl source code as string.
        """
        query = """
            query TimelineScowl($id: String!) {
                timeline(id: $id) { id, scowl }
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": timeline})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["timeline"]["scowl"]

    def create_timeline_from_s3(
        self,
        timeline: str,
        s3_uri: str,
        time_path: str,
        data_path: str,
        default_type: Optional[str] = None,
        id_path: Optional[str] = None,
        type_path: Optional[str] = None,
    ):
        query = """
                    mutation SaveTimelineMutation($id: String!, $source: String!, $state: String!, $parameters: [KeyValueInput]!) {
                        saveTimeline(id: $id, source: $source, state: $state, parameters: $parameters) {
                            id
                        }
                    }
                """

        parameters = [
            {"key": "s3_uri", "value": s3_uri},
            {"key": "time_path", "value": time_path},
            {"key": "data_path", "value": data_path},
        ]

        if default_type:
            parameters.append({"key": "default_type", "value": default_type})

        if id_path:
            parameters.append({"key": "id_path", "value": id_path})

        if type_path:
            parameters.append({"key": "type_path", "value": type_path})

        ret = self._gql_client.execute(
            query=query,
            variables={
                "id": timeline,
                "source": "s3",
                "state": "processing",
                "parameters": parameters,
            },
        )

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["saveTimeline"]["id"]

    def create_timeline_from_feed(
        self,
        timeline: str,
        start_ts: Union[pd.Timestamp, str],
        end_ts: Union[pd.Timestamp, str],
        event_types: Optional[List[str]] = None,
    ) -> None:
        """
        Create (or overwrite) timeline from the Event Feed

        Arguments:
            timeline: Timeline name.
            start_ts: Earliest event timestamp to fetch (local client timezone).
            end_ts: Latest event timestamp to fetch (local client timezone).
            event_types: Event types to include (default: all).
        """

        query = """
            mutation SaveTimeline($id: String!, $parameters: [KeyValueInput]!) {
              saveTimeline(id: $id, source: "es", state: "processing", parameters: $parameters) {
                id
              }
            }
        """
        if isinstance(start_ts, pd.Timestamp):
            start_ts = str(start_ts)
        if isinstance(end_ts, pd.Timestamp):
            end_ts = str(end_ts)
        start_ts = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )
        end_ts = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )
        start_str = start_ts.to_iso8601_string()
        end_str = end_ts.to_iso8601_string()
        parameters = [
            {"key": "start", "value": start_str},
            {"key": "end", "value": end_str},
        ]

        if event_types:
            events = ",".join(event_types)
            parameters.append({"key": "events", "value": events})

        ret = self._gql_client.execute(
            query=query, variables={"id": timeline, "parameters": parameters}
        )
        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])
        self._wait_for_timeline_processing(timeline)

    def create_timeline_from_log(
        self,
        timeline: str,
        start_ts: Union[pd.Timestamp, str],
        end_ts: Union[pd.Timestamp, str],
        event_types: Optional[List[str]] = None,
    ) -> None:
        """
        Create (or overwrite) timeline from the Event Log

        Arguments:
            timeline: Timeline name.
            start_ts: Earliest event timestamp to fetch (local client timezone).
            end_ts: Latest event timestamp to fetch (local client timezone).
            event_types: Event types to include (default: all).
        """

        query = """
            mutation SaveTimeline($id: String!, $parameters: [KeyValueInput]!) {
              saveTimeline(id: $id, source: "athena", state: "processing", parameters: $parameters) {
                id
              }
            }
        """
        if isinstance(start_ts, pd.Timestamp):
            start_ts = str(start_ts)
        if isinstance(end_ts, pd.Timestamp):
            end_ts = str(end_ts)
        start_ts = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )
        end_ts = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
            pendulum.timezone("UTC")
        )
        start_str = start_ts.to_iso8601_string()
        end_str = end_ts.to_iso8601_string()
        parameters = [
            {"key": "start", "value": start_str},
            {"key": "end", "value": end_str},
        ]

        if event_types:
            events = ",".join(event_types)
            parameters.append({"key": "events", "value": events})

        ret = self._gql_client.execute(
            query=query, variables={"id": timeline, "parameters": parameters}
        )
        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])
        self._wait_for_timeline_processing(timeline)

    def create_timeline_from_dataframes(
        self,
        timeline: str,
        df_dict: Dict[str, pd.DataFrame],
        timestamp_column: Optional[str] = None,
    ) -> None:
        """
        Create (or overwrite) timeline from a collection of DataFrames—one per event type.

        Arguments:
            timeline: Timeline name.
            df_dict: Dictionary from event type name to DataFrame of events.
            timestamp_column: Name of timestamp column, default `_time`. If column not present, current timestamp used for all events.
        """
        jsonl = ""
        for event_type, df in df_dict.items():
            jsonl += self._df_to_jsonl(df, event_type, timestamp_column)
        self.create_timeline_from_jsonl(timeline, jsonl)

    def create_timeline_from_jsonl(self, timeline: str, jsonl: str) -> None:
        """
        Create (or overwrite) timeline from JSON events passed in as a string.

        Arguments:
            timeline: Timeline name.
            jsonl: JSON event data, one JSON dict per line.
        """

        if not jsonl.endswith("\n"):
            jsonl += "\n"
        data = gzip.compress(bytes(jsonl, "utf-8"))
        self._create_timeline_from_jsonl_gz(timeline, data)

    def _create_timeline_from_jsonl_gz(
        self,
        timeline: str,
        data: bytes,
    ) -> None:
        query = """
            mutation SaveTimelineMutation($id: String!,
                                          $filename: String!) {
                saveTimeline(id: $id, source: "file", state: "new") {
                    uploadUrl(name: $filename)
                }
            }
        """

        ret = self._gql_client.execute(
            query=query, variables={"id": timeline, "filename": "timeline.jsonl.gz"}
        )
        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        url = ret["data"]["saveTimeline"]["uploadUrl"]

        http_response = requests.put(url, data=data)
        if http_response.status_code != 200:
            raise Exception(http_response.error)

        query = """
            mutation SaveTimelineMutation($id: String!) {
                saveTimeline(id: $id, source: "file", state: "processing") {
                    id
                }
            }
        """

        ret = self._gql_client.execute(query=query, variables={"id": timeline})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        self._wait_for_timeline_processing(timeline)

    def _wait_for_timeline_processing(self, timeline: str) -> None:
        RETRIES = 180
        DELAY = 5.0
        retry_count = 0
        while retry_count < RETRIES:
            tl = self.get_timeline(timeline)
            if tl.status != "processing":
                return
            time.sleep(DELAY)
            retry_count += 1
        if self.status == "processing":
            raise Exception(f"Timed out after {DELAY * RETRIES} seconds")

    def create_timeline_from_file(self, timeline: str, filename: str) -> None:
        """
        Create (or overwrite) timeline from events stored in a file.

        Supported file types: `.jsonl`, `.jsonl.gz`

        Arguments:
            timeline: Timeline name.
            filename: Name of events file to upload.
        """

        _, ext = _splitext(filename)

        if ext in (".jsonl.gz", ".json.gz"):
            with open(filename, "rb") as f:
                self._create_timeline_from_jsonl_gz(timeline, f.read())
        elif ext in (".jsonl", ".json"):
            with open(filename, "r") as f:
                jsonl = f.read()
                self.create_timeline_from_jsonl(timeline, jsonl)
        else:
            raise Exception(f"Unsupported file extension: {ext}")

    def _df_to_jsonl(self, df, event_type, timestamp_column=None):
        df = df.copy()
        df["_type"] = event_type
        if timestamp_column:
            df.rename(columns={timestamp_column: "_time"}, inplace=True)
        if "_time" not in df.columns:
            df["_time"] = datetime.utcnow()
        df.sort_values("_time", inplace=True)
        jsonl = df.to_json(orient="records", lines=True, date_format="iso")
        if not jsonl.endswith("\n"):
            jsonl += "\n"
        return jsonl

    def get_materialization(self, id: str) -> Materialization:
        return Materialization(self, id)

    def materialize(
        self, timeline: str, branch: Optional[str] = None
    ) -> Materialization:
        """
        Enrich timeline using topology at branch.

        This is the primary function of the SDK.

        Arguments:
            timeline: Timeline name.
            branch: Specify a source branch other than the client default.

        Returns:
            Handle to Materialization job
        """

        return self.materialize_many([timeline], branch)

    def materialize_many(
        self, timelines: List[str], branch: Optional[str] = None
    ) -> Materialization:
        """
        Enrich collection of timelines using topology at branch. Timelines are merged based on timestamp.

        This is the primary function of the SDK.

        Arguments:
            timelines: Timeline names.
            branch: Specify a source branch other than the client default.

        Returns:
            Handle to Materialization job
        """
        branch = branch or self._branch
        query = """
            mutation Materialize($timelines: [String], $branch: String!) {
                materialize(timelines: $timelines, branch: $branch) { id }
            }
        """

        ret = self._gql_client.execute(
            query=query, variables={"timelines": timelines, "branch": branch}
        )

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return Materialization(self, ret["data"]["materialize"]["id"])

    def distributed_materialize_many(
        self,
        timelines: List[str],
        features: List[str] = None,
        start_ts: Optional[Union[pd.Timestamp, str]] = None,
        end_ts: Optional[Union[pd.Timestamp, str]] = None,
        branch: Optional[str] = None,
    ) -> Materialization:
        """
        Enrich collection of timelines using topology at branch. Timelines are merged based on timestamp.

        This is the primary function of the SDK.

        Arguments:
            timelines: Timeline names.
            branch: Specify a source branch other than the client default.
            start_ts: Earliest event timestamp to materialize (local client timezone).
            end_ts: Latest event timestamp to materialize (local client timezone).
            features: List of features to materialize, e.g. `['login.email', 'purchase.*']`

        Returns:
            Handle to Materialization job
        """

        variables = {
            "timelines": timelines,
            "branch": branch or self._branch,
            "features": features,
        }

        if start_ts:
            if isinstance(start_ts, pd.Timestamp):
                start_ts = str(start_ts)
            start_ts = pendulum.parse(start_ts, tz=CONFIG.timezone).astimezone(
                pendulum.timezone("UTC")
            )
            variables["start"] = start_ts.to_iso8601_string()

        if end_ts:
            if isinstance(end_ts, pd.Timestamp):
                end_ts = str(end_ts)
            end_ts = pendulum.parse(end_ts, tz=CONFIG.timezone).astimezone(
                pendulum.timezone("UTC")
            )
            variables["end"] = end_ts.to_iso8601_string()

        query = """
            mutation DistributedMaterialize($timelines: [String], $branch: String!, $features: [String], $start: DateTime, $end: DateTime) {
                distributedMaterialize(timelines: $timelines, branch: $branch, features: $features, start: $start, end: $end) { id }
            }        
        """

        ret = self._gql_client.execute(
            query=query,
            variables=variables,
        )

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return Materialization(self, ret["data"]["distributedMaterialize"]["id"])

    def get_models(self) -> pd.DataFrame:
        """
        Return all PMML models and their metadata.

        Returns:
            Model metadata.
        """
        query = """
                    query ModelList {
                        models { id, name, version, creator }
                    }
                """

        ret = self._gql_client.execute(query=query)

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        rows = []
        for model in ret["data"]["models"]:
            row = {
                "id": model["id"],
                "name": model["name"],
                "version": model["version"],
                "creator": model["creator"],
            }
            rows.append(row)
        df = pd.DataFrame(rows)
        return df.sort_values(
            ["creator", "name", "version"], ascending=False
        ).set_index("id")

    def put_model(self, name: str, version: str, filename: str) -> str:
        """
        Upload PMML model from file.

        Arguments:
            name: Model name, e.g. "churn_predictor".
            version: Model version id, e.g. "0.8.1".
            filename: Local PMML file, e.g. "my_model.xml"

        Returns:
            Server-side model identifier
        """
        query = """
                    mutation PutModel($name: String!, $version: String!) {
                        putModel (name: $name, version: $version) { id, name, version, uploadUri }
                    }
                """

        ret = self._gql_client.execute(
            query=query, variables={"name": name, "version": version}
        )
        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        uploadUri = ret["data"]["putModel"]["uploadUri"]

        with open(filename, "rb") as f:
            files = {"file": (filename, f)}
            http_response = requests.put(uploadUri, files=files)
            if http_response.status_code != 200:
                raise Exception(http_response.error)

        return ret["data"]["putModel"]["id"]

    def version(self) -> str:
        """
        Return the server-side version number.

        Returns:
            Version identifier
        """
        query = """
            query Version {
                version
            }
        """

        ret = self._gql_client.execute(query=query)
        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["version"]

    def _get_session(self):
        query = """
                    query TempCredentials {
                        tenant { credentials }
                    }
                """

        ret = self._gql_client.execute(query=query)

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        creds = ret["data"]["tenant"]["credentials"]

        return boto3.Session(
            aws_access_key_id=creds["AccessKeyID"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )


class Materialization:
    """
    A handle to a server-side materialization job, which enriches a Timeline
    (or set of Timelines) by running it (them) through a given Topology.

    Objects are not constructed directly. Materializations are returned by methods
    of the `Client` class.
    """

    def __init__(self, client, id):
        self._client = client
        self.id = id
        self._mtr = None

    def __repr__(self):
        return f"Materialization(id='{self.id}')"

    def _get_materialization(self):
        query = """
            query Materialization($id: String!) {
                materialization(id: $id) { id, state, path, timelines, events, branch, hash, jobsSubmitted, jobsCompleted }
            }
        """

        ret = self._client._gql_client.execute(query=query, variables={"id": self.id})

        if "errors" in ret:
            raise Exception(ret["errors"][0]["message"])

        return ret["data"]["materialization"]

    def status(self) -> str:
        """
        Current status of the job. One of {'processing', 'materialized', 'error'}
        """
        self._mtr = self._get_materialization()
        return self._mtr["state"]

    def wait(self) -> str:
        """
        Wait until materialization completes. In a Notebook, a progress bar is displayed.

        Returns:
            Materialization status
        """

        self._mtr = self._get_materialization()
        if self._mtr["state"] not in ["new", "processing", "materialized"]:
            raise Exception(f"Error in {self}: {self._mtr['state']}")

        # Do not show progress bars if already materialized
        if self._mtr["state"] == "materialized":
            return self._mtr["state"]

        while self._mtr["jobsSubmitted"] == 0 and self._mtr["state"] in ["new", "processing"]:
            sleep(0.5)
            self._mtr = self._get_materialization()

        submitted = self._mtr["jobsSubmitted"]
        completed = self._mtr["jobsCompleted"]

        with tqdm(total=submitted) as pbar:
            pbar.update(completed)
            while self._mtr["state"] == "processing":
                sleep(0.5)
                self._mtr = self._get_materialization()
                new_completed = self._mtr["jobsCompleted"]
                new_submitted = self._mtr["jobsSubmitted"]
                if new_submitted != submitted:
                    pbar.total = new_submitted
                    submitted = new_submitted

                pbar.update(new_completed - completed)
                completed = new_completed
            if self._mtr["state"] == "materialized":
                pbar.update(submitted - completed)

        return self._mtr["state"]

    def progress(self) -> str:
        """
        Current progress of subjobs: X of Y jobs completed.
        """
        self._mtr = self._get_materialization()

        if self._mtr["state"] != "processing":
            return self._mtr["state"]
        else:
            completed = self._mtr["jobsCompleted"]
            submitted = self._mtr["jobsSubmitted"]
            return f"{completed} / {submitted} jobs completed."

    @property
    def timelines(self) -> List[str]:
        """
        Timelines materialized by the job.
        """
        if self._mtr is None:
            self._mtr = self._get_materialization()
        return list(sorted(self._mtr["timelines"]))

    @property
    def event_types(self) -> List[str]:
        """
        Materialized event types
        """
        if self._mtr is None:
            self._mtr = self._get_materialization()
        return list(sorted(self._mtr["events"]))

    @property
    def branch(self) -> str:
        """
        Topology branch used for materialization.
        """
        if self._mtr is None:
            self._mtr = self._get_materialization()
        return self._mtr["branch"]

    @property
    def hash(self) -> str:
        """
        Unique hash identifying the job.
        """
        if self._mtr is None:
            self._mtr = self._get_materialization()
        return self._mtr["hash"]

    @property
    def path(self) -> str:
        """
        S3 bucket path where results are stored.
        """
        self.wait()
        return self._mtr["path"]

    def get_events(self, event_type: str, features: List[str] = []) -> pd.DataFrame:
        """
        Return enriched events of specified type. Waits if
        job is still processing.

        Arguments:
            event_type: Name of event type to fetch.
            features: Feature names to fetch. By default, fetch all.

        Returns:
            Enriched events
        """
        # if event_type not in self.event_types:
        #    raise Exception(f"Event type '{event_type}' not found.")

        self.wait()
        session = self._client._get_session()

        path = f"{self.path}/events/event_type={event_type}/"
        cols = ["_id", "_type", "_time"]

        if not features:
            df = wr.s3.read_parquet(
                boto3_session=session,
                path=path,
                use_threads=8,
            )
        else:
            cols.extend(features)
            df = wr.s3.read_parquet(
                boto3_session=session,
                path=path,
                columns=cols,
                use_threads=8,
            )

        df = tz_convert_timestamp_columns(df)
        return df.set_index("_id")

    def get_errors(self, event_type: str, features: List[str] = []) -> pd.DataFrame:
        """
        Return event-level materialization errors for specified event type. Waits if
        job is still processing.

        Arguments:
            event_type: Name of event type to fetch.
            features: Feature names to fetch. By default, fetch all.

        Returns:
            Event-level errors
        """
        # if event_type not in self.event_types:
        #    raise Exception(f"Event type '{event_type}' not found.")

        self.wait()
        session = self._client._get_session()

        path = f"{self.path}/errors/event_type={event_type}/"
        cols = ["_id", "_type", "_time"]
        cols.extend(features)

        try:
            if not features:
                df = wr.s3.read_parquet(
                    boto3_session=session,
                    path=path,
                    ignore_empty=True,
                )
            else:
                df = wr.s3.read_parquet(
                    boto3_session=session,
                    path=path,
                    columns=cols,
                    ignore_empty=True,
                )
        except Exception as e:
            logger.debug(e)
            return pd.DataFrame(columns=cols)

        df = tz_convert_timestamp_columns(df)
        return df.set_index("_id")
