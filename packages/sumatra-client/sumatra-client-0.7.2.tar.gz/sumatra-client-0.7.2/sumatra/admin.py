from collections import defaultdict
import boto3
import pendulum
import pandas as pd
import awswrangler as wr
from logging import getLogger
from botocore.exceptions import ProfileNotFound, ClientError
from sumatra.config import CONFIG
from typing import Dict

logger = getLogger("sumatra.admin")

TENANT_PREFIX = "sumatra_"


class AdminClient:
    def __init__(self, aws_profile=None):
        aws_profile = aws_profile or CONFIG.aws_profile
        logger.info(f"Using AWS profile: {aws_profile}\n")
        try:
            boto3.setup_default_session(profile_name=aws_profile)
        except ProfileNotFound:
            raise Exception(
                f"AWS profile '{aws_profile}' not found in aws credentials file"
            )
        self._cognito = boto3.client("cognito-idp")
        self._apigateway = boto3.client("apigateway")
        try:
            self.list_tenants()
        except ClientError as e:
            raise Exception(
                f"Error connecting with '{aws_profile}' as the AWS profile for {CONFIG.instance}: {e}"
            )

    def query_athena(self, tenant, sql):
        return wr.athena.read_sql_query(
            workgroup=TENANT_PREFIX + tenant, database=TENANT_PREFIX + tenant, sql=sql
        )

    def _tenants_from_groups(self, resp):
        tenants = []
        for group in resp["Groups"]:
            name = group["GroupName"]
            if name.startswith(TENANT_PREFIX) and name != "sumatra_admin":
                tenants.append(name[len(TENANT_PREFIX) :])
        return tenants

    def list_tenants(self):
        resp = self._cognito.list_groups(UserPoolId=CONFIG.user_pool_id)
        return self._tenants_from_groups(resp)

    def list_users(self):
        resp = self._cognito.list_users(UserPoolId=CONFIG.user_pool_id)
        return [list(user.values())[0] for user in resp["Users"]]

    def current_tenant(self, username):
        resp = self._cognito.admin_list_groups_for_user(
            UserPoolId=CONFIG.user_pool_id, Username=username
        )
        tenants = self._tenants_from_groups(resp)
        if len(tenants) > 1:
            logger.warning(f"user '{username}' assigned to multiple tenants: {tenants}")
        if len(tenants) == 0:
            return None
        return tenants[0]

    def _remove_tenant(self, username, tenant=None):
        if tenant is None:
            tenant = self.current_tenant(username)
        self._cognito.admin_remove_user_from_group(
            UserPoolId=CONFIG.user_pool_id,
            GroupName=TENANT_PREFIX + tenant,
            Username=username,
        )

    def _add_tenant(self, username, tenant):
        self._cognito.admin_add_user_to_group(
            UserPoolId=CONFIG.user_pool_id,
            GroupName=TENANT_PREFIX + tenant,
            Username=username,
        )
        self._cognito.admin_add_user_to_group(
            UserPoolId=CONFIG.user_pool_id,
            GroupName="sumatra_admin",
            Username=username,
        )

    def assign_tenant(self, username, tenant):
        current = self.current_tenant(username)
        if current == tenant:
            logger.warning(f"user '{username}' already assigned to tenant '{tenant}'")
            return
        elif current:
            self._remove_tenant(username, current)
        self._add_tenant(username, tenant)

    def _get_keys(self) -> Dict:
        keys = defaultdict(dict)
        resp = self._apigateway.get_api_keys(includeValues=True)
        for item in resp.get("items", []):
            name = item["name"]
            if name.startswith("api_") or name.startswith("sdk_"):
                keys[name[4:]][name[:3]] = {"id": item["id"], "value": item["value"]}
        return dict(keys)

    def get_keys(self) -> pd.DataFrame:
        rows = []
        for tenant, keys in self._get_keys().items():
            for typ, val in keys.items():
                rows.append((tenant, typ, val["value"]))
        return (
            pd.DataFrame(rows, columns=("Tenant", "Type", "Key"))
            .set_index(["Tenant", "Type"])
            .sort_index()
        )

    def _get_usage_plans(self):
        ids = {}
        resp = self._apigateway.get_usage_plans()
        for item in resp.get("items", []):
            name = item["name"]
            ids[name] = item["id"]
        return ids

    def _get_key_usage(self, days):
        if not days:
            raise Exception("empty date range")
        usage_by_key = {}
        for usage_plan_id in self._get_usage_plans().values():
            resp = self._apigateway.get_usage(
                usagePlanId=usage_plan_id, startDate=days[0], endDate=days[-1]
            )
            for key, usage in resp.get("items", {}).items():
                if len(usage) != len(days):
                    raise Exception(
                        f"expected {len(days)} data points, found {len(usage)}"
                    )
                used = [row[0] for row in usage]
                usage_by_key[key] = used
        return usage_by_key

    def get_key_usage(self, start_date=None, end_date=None):
        end_date = end_date or pendulum.today()
        start_date = start_date or end_date.subtract(days=6)
        days = [d.to_date_string() for d in end_date - start_date]
        usage = self._get_key_usage(days)
        rows = []
        for tenant, keys in self._get_keys().items():
            for typ, val in keys.items():
                used = usage.get(val["id"], [0 for _ in days])
                rows.append([tenant, typ] + used)
        return (
            pd.DataFrame(rows, columns=["Tenant", "Type"] + days)
            .set_index(["Tenant", "Type"])
            .sort_index()
        )
