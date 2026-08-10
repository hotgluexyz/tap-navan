"""Stream type classes for tap-navan."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from dateutil.relativedelta import relativedelta
from hotglue_singer_sdk import typing as th  # JSON Schema typing helpers
from typing_extensions import override

from tap_navan.client import NavanStream

# Navan rejects transaction_date ranges outside this lookback window.
_MAX_TRANSACTION_DATE_LOOKBACK = relativedelta(months=2)


class TransactionsStream(NavanStream):
    """Stream for Navan expense transactions."""

    name = "transactions"
    path = "/expense/transactions"
    primary_keys = ["id"]
    replication_key = "modified_timestamp"

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Transaction UUID"),
        th.Property("transaction_type", th.StringType),
        th.Property("transaction_description", th.StringType),
        th.Property("activity_type", th.StringType),
        th.Property("authorization_date", th.DateType),
        th.Property("posted_date", th.DateType),
        th.Property("posted_date_time", th.DateTimeType),
        th.Property("transaction_date", th.DateType),
        th.Property("erp_effective_date", th.DateType),
        th.Property("last_approver_action_date", th.DateType),
        th.Property(
            "modified_timestamp",
            th.DateTimeType,
            description="Last modification time; used as the replication key",
        ),
        th.Property("posted_amount", th.StringType),
        th.Property("posted_currency", th.StringType),
        th.Property("original_amount", th.StringType),
        th.Property("original_currency", th.StringType),
        th.Property("personal_amount", th.StringType),
        th.Property("rejected_amount", th.StringType),
        th.Property("vendor_name", th.StringType),
        th.Property("vendor_category", th.StringType),
        th.Property("vendor_address", th.StringType),
        th.Property("personal", th.BooleanType),
        th.Property("gl_code_number", th.StringType),
        th.Property("gl_code_name", th.StringType),
        th.Property("statement_id", th.StringType),
        th.Property("exchange_rate", th.NumberType),
        th.Property("cardholder", th.StringType),
        th.Property("cardholder_email", th.StringType),
        th.Property("employee_id", th.StringType),
        th.Property("legal_entity", th.StringType),
        th.Property("department", th.StringType),
        th.Property("region", th.StringType),
        th.Property("subsidiary", th.StringType),
        th.Property("cost_center", th.StringType),
        th.Property("user_attributes", th.ObjectType()),
        th.Property("traveler_department", th.StringType),
        th.Property("traveler_region", th.StringType),
        th.Property("traveler_subsidiary", th.StringType),
        th.Property("traveler_cost_center", th.StringType),
        th.Property("traveler_user_attributes", th.ObjectType()),
        th.Property("invoice_date", th.DateType),
        th.Property("invoice_number", th.StringType),
        th.Property("participants", th.StringType),
        th.Property("erp_sync_status", th.StringType),
        th.Property("approval_status", th.StringType),
        th.Property("flag_status", th.StringType),
        th.Property("flagged", th.BooleanType),
        th.Property("flag_reasons", th.StringType),
        th.Property("approver_type", th.StringType),
        th.Property("approved_by_email", th.StringType),
        th.Property("receipt", th.StringType),
        th.Property("receipt_navan", th.StringType),
        th.Property("policy", th.StringType),
        th.Property("policy_category", th.StringType),
        th.Property("itemized", th.BooleanType),
        th.Property("booking_details", th.ObjectType()),
        th.Property("line_items", th.ArrayType(th.ObjectType())),
        th.Property("custom_field_values", th.ArrayType(th.ObjectType())),
        th.Property("manually_added_date", th.DateType),
        th.Property("reimbursement_method", th.StringType),
        th.Property("reimbursement_date", th.DateType),
        th.Property("reimbursement_amount", th.StringType),
        th.Property("reimbursement_currency", th.StringType),
        th.Property("reimbursement_exchange_rate", th.NumberType),
        th.Property("direct_reimbursement_fee_amount", th.StringType),
        th.Property("billable_entity_amount", th.StringType),
        th.Property("billable_entity_currency", th.StringType),
        th.Property("distance_amount", th.StringType),
        th.Property("distance_unit", th.StringType),
        th.Property("tax_details", th.ArrayType(th.ObjectType())),
        th.Property("_type", th.StringType),
        th.Property("e_receipt", th.StringType),
        th.Property("e_receipt_navan", th.StringType),
    ).to_dict()

    def _transaction_date_bounds(self) -> tuple[date, date]:
        """Return a transaction_date range within Navan's 2-month lookback limit."""
        today = datetime.now(timezone.utc).date()
        earliest_allowed = today - _MAX_TRANSACTION_DATE_LOOKBACK

        start_date_raw = self.config.get("start_date")
        if start_date_raw:
            start = datetime.fromisoformat(
                str(start_date_raw).replace("Z", "+00:00")
            ).date()
        else:
            start = earliest_allowed

        return max(start, earliest_allowed), today

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Add transaction filters required by the expense transactions endpoint."""
        params = super().get_url_params(context, next_page_token)
        date_from, date_to = self._transaction_date_bounds()
        params.update(
            {
                "type": "TRANSACTIONS,MANUAL_TRANSACTIONS",
                "transaction_date.from": date_from.isoformat(),
                "transaction_date.to": date_to.isoformat(),
                "include_field_group": "ERP",
            }
        )
        return params
