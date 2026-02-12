"""
Fact table generator for synthetic HR data
Generates monthly snapshots and transaction history for workforce analytics
"""

from datetime import date, timedelta
from typing import Dict, List
import pandas as pd
import numpy as np

from ..config import GeneratorConfig


class FactGenerator:
    """Generates fact tables for workforce analytics"""

    def __init__(
        self,
        config: GeneratorConfig,
        dimensions: Dict[str, pd.DataFrame],
        employees: pd.DataFrame,
        lifecycle_events: List[Dict],
    ):
        self.config = config
        self.dimensions = dimensions
        self.employees = employees
        self.lifecycle_events = lifecycle_events

        # Convert lifecycle events to DataFrame for easier processing
        self.events_df = pd.DataFrame(lifecycle_events)

    def generate_all(self) -> Dict[str, pd.DataFrame]:
        """Generate all fact tables"""
        facts = {}

        # Generate job history (event-based)
        facts["job_history"] = self._generate_job_history()

        # Generate monthly employee history snapshots
        facts["fact_employee_history"] = self._generate_employee_history()

        # Generate termination history
        facts["termination_history"] = self._generate_termination_history()

        return facts

    def _generate_job_history(self) -> pd.DataFrame:
        """Generate job history fact table from lifecycle events"""
        records = []

        for event in self.lifecycle_events:
            record = {
                "employee_number": event["employee_number"],
                "transaction_date": event["effective_date"],
                "effective_date": event["effective_date"],
                "employee_status_code": event["status_code"],
                "employee_type_code": event["employee_type_code"],
                "fullpart_time_code": "F" if event["scheduled_fte"] >= 0.75 else "P",
                "scheduled_fte": event["scheduled_fte"],
                "job_code": event["job_code"],
                "job_family_code": event["job_family_code"],
                "company_code": event["company_code"],
                "location_code": event["location_code"],
                "org_1_code": event["org_1_code"],
                "org_2_code": event["org_2_code"],
                "last_hire_date": event["last_hire_date"],
                "seniority_date": event["last_hire_date"],
                "date_in_job": event.get("date_in_job", event["effective_date"]),
                "termination_date": event.get("termination_date"),
                "termination_reason_code": event.get("termination_reason_code"),
                "termination_type_code": event.get("termination_type_code"),
                "salaryhourly_code": event["salaryhourly_code"],
                "earning_group_code": f"EG{hash(event['job_code']) % 10 + 1:02d}",
                "pay_group_code": f"PG{hash(event['company_code']) % 5 + 1:02d}",
                "supervisor_employee_number": None,  # Will be populated from employee data
                "orglvl1reportcategory": "Operations",
            }
            records.append(record)

        df = pd.DataFrame(records)

        # Add supervisor info from employees
        sup_lookup = self.employees.set_index("employee_number")["supervisor_employee_number"].to_dict()
        df["supervisor_employee_number"] = df["employee_number"].map(sup_lookup)

        return df

    def _generate_employee_history(self) -> pd.DataFrame:
        """
        Generate monthly snapshot fact table.
        Each row represents an employee's state at the end of each month.
        """
        records = []

        # Get all month-end dates in range
        month_ends = self._get_month_ends()

        # Process each employee
        for _, employee in self.employees.iterrows():
            emp_num = employee["employee_number"]
            emp_events = self.events_df[self.events_df["employee_number"] == emp_num].sort_values("effective_date")

            if emp_events.empty:
                continue

            # Get employee's timeline of states
            for report_date in month_ends:
                # Find the most recent event before or on this date
                relevant_events = emp_events[emp_events["effective_date"] <= report_date]

                if relevant_events.empty:
                    continue  # Employee not yet hired

                current_state = relevant_events.iloc[-1]

                # Skip if terminated before this month
                if current_state["status_code"] == "T":
                    term_date = current_state.get("termination_date")
                    if term_date and term_date < report_date.replace(day=1):
                        continue  # Don't include in months after termination

                # Calculate flags
                hire_date = current_state["last_hire_date"]
                is_new_hire = (
                    hire_date.year == report_date.year and hire_date.month == report_date.month
                )

                is_termination = current_state["status_code"] == "T"
                term_date = current_state.get("termination_date")
                is_term_this_month = (
                    is_termination
                    and term_date
                    and term_date.year == report_date.year
                    and term_date.month == report_date.month
                )

                # Determine workforce group
                emp_type = current_state["employee_type_code"]
                if emp_type in ["CON"]:
                    workforce_group = "Contractor"
                elif emp_type in ["TAW", "TFT", "CAS"]:
                    workforce_group = "Temporary"
                else:
                    workforce_group = "Regular"

                # Build job info lookup
                jobs_df = self.dimensions["dim_jobs"]
                job_info = jobs_df[jobs_df["job_code"] == current_state["job_code"]]
                is_supervisor = False
                is_staff = False
                if not job_info.empty:
                    is_supervisor = bool(job_info.iloc[0].get("is_supervisor", False))
                    is_staff = bool(job_info.iloc[0].get("is_staff", False))

                record = {
                    "report_date": report_date,
                    "report_year": report_date.year,
                    "report_month": report_date.month,
                    "primary_key": f"{emp_num}_{current_state['company_code']}",
                    "employee_number": emp_num,
                    "eeceeid": employee["eeceeid"],
                    "eeccoid": employee["eeccoid"],
                    "scheduled_fte": current_state["scheduled_fte"],
                    "pay_group_code": f"PG{hash(current_state['company_code']) % 5 + 1:02d}",
                    "salaryhourly_code": current_state["salaryhourly_code"],
                    "employee_status_code": current_state["status_code"],
                    "employee_type_code": emp_type,
                    "fullpart_time_code": "F" if current_state["scheduled_fte"] >= 0.75 else "P",
                    "job_code": current_state["job_code"],
                    "job_family_code": current_state["job_family_code"],
                    "location_code": current_state["location_code"],
                    "company_code": current_state["company_code"],
                    "org_1_code": current_state["org_1_code"],
                    "org_2_code": current_state["org_2_code"],
                    "last_hire_date": hire_date,
                    "seniority_date": hire_date,
                    "date_in_job": current_state.get("date_in_job", hire_date),
                    "termination_date": current_state.get("termination_date"),
                    "termination_reason_code": current_state.get("termination_reason_code"),
                    "termination_type_code": current_state.get("termination_type_code"),
                    "supervisor_employee_number": employee["supervisor_employee_number"],
                    "earning_group_code": f"EG{hash(current_state['job_code']) % 10 + 1:02d}",
                    "orglvl1reportcategory": "Operations",
                    "status_code": current_state["status_code"],
                    "loa_reason_code": current_state.get("loa_reason_code"),
                    "loa_type_code": None,
                    "record_id": f"{emp_num}_{report_date.strftime('%Y%m')}",
                    "allocation_percentage": 100.0,
                    "view": "Home",
                    "f_active": 1 if current_state["status_code"] == "A" else 0,
                    "f_termination": 1 if is_term_this_month else 0,
                    "f_new_hires": 1 if is_new_hire else 0,
                    "recoverable": 0,
                    "workforce_group": workforce_group,
                    "is_sales_pssr": False,
                    "is_hourly_supervisor": is_supervisor and current_state["salaryhourly_code"] == "H",
                    "is_hourly": current_state["salaryhourly_code"] == "H",
                    "is_staff": is_staff,
                    "staff_ratio_segment": "Staff" if is_staff else "Non-Staff",
                }
                records.append(record)

        return pd.DataFrame(records)

    def _generate_termination_history(self) -> pd.DataFrame:
        """Generate dedicated termination fact table"""
        term_events = self.events_df[self.events_df["transaction_type"] == "TERMINATION"]

        records = []
        for _, event in term_events.iterrows():
            records.append(
                {
                    "primary_key": f"{event['employee_number']}_{event['termination_date']}",
                    "employee_number": event["employee_number"],
                    "datetime_processed": event["effective_date"],
                    "termination_date": event["termination_date"],
                    "termination_type_code": event["termination_type_code"],
                    "termination_reason_code": event["termination_reason_code"],
                    "is_termination_cleared": True,
                }
            )

        return pd.DataFrame(records)

    def _get_month_ends(self) -> List[date]:
        """Get all month-end dates in the configured range"""
        month_ends = []
        current = self.config.start_date.replace(day=1)

        while current <= self.config.end_date:
            # Get last day of month
            if current.month == 12:
                month_end = current.replace(day=31)
            else:
                month_end = current.replace(month=current.month + 1, day=1) - timedelta(days=1)

            if month_end <= self.config.end_date:
                month_ends.append(month_end)

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return month_ends

    def generate_analytics_summary(self) -> Dict[str, pd.DataFrame]:
        """
        Generate pre-aggregated analytics tables for quick dashboarding.
        These represent the 'gold' layer analytics views.
        """
        fact_history = self.generate_all()["fact_employee_history"]

        summaries = {}

        # Monthly headcount summary
        summaries["monthly_headcount"] = (
            fact_history[fact_history["f_active"] == 1]
            .groupby(["report_year", "report_month", "company_code"])
            .agg(
                headcount=("employee_number", "nunique"),
                fte=("scheduled_fte", "sum"),
                new_hires=("f_new_hires", "sum"),
                terminations=("f_termination", "sum"),
            )
            .reset_index()
        )

        # Attrition by department
        summaries["attrition_by_department"] = (
            fact_history.groupby(["report_year", "report_month", "org_2_code"])
            .agg(
                headcount=("employee_number", "nunique"),
                terminations=("f_termination", "sum"),
            )
            .reset_index()
        )
        summaries["attrition_by_department"]["attrition_rate"] = (
            summaries["attrition_by_department"]["terminations"]
            / summaries["attrition_by_department"]["headcount"]
        ).fillna(0)

        # Tenure distribution
        fact_history_with_tenure = fact_history.copy()
        fact_history_with_tenure["tenure_days"] = (
            pd.to_datetime(fact_history_with_tenure["report_date"])
            - pd.to_datetime(fact_history_with_tenure["last_hire_date"])
        ).dt.days
        fact_history_with_tenure["tenure_bucket"] = pd.cut(
            fact_history_with_tenure["tenure_days"] / 365,
            bins=[0, 1, 2, 5, 10, 100],
            labels=["0-1 years", "1-2 years", "2-5 years", "5-10 years", "10+ years"],
        )

        summaries["tenure_distribution"] = (
            fact_history_with_tenure[fact_history_with_tenure["f_active"] == 1]
            .groupby(["report_year", "report_month", "tenure_bucket"])
            .agg(headcount=("employee_number", "nunique"))
            .reset_index()
        )

        # Termination reason analysis
        term_records = fact_history[fact_history["f_termination"] == 1]
        summaries["termination_reasons"] = (
            term_records.groupby(
                ["report_year", "termination_type_code", "termination_reason_code"]
            )
            .size()
            .reset_index(name="count")
        )

        return summaries
