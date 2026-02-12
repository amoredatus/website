"""
Employee population generator for synthetic HR data
Generates realistic employee records with demographics, hiring patterns, and assignments
"""

import random
import hashlib
from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

from ..config import (
    GeneratorConfig,
    FIRST_NAMES,
    LAST_NAMES,
)


class EmployeeGenerator:
    """Generates a realistic employee population"""

    def __init__(self, config: GeneratorConfig, dimensions: Dict[str, pd.DataFrame]):
        self.config = config
        self.dimensions = dimensions
        random.seed(config.random_seed)
        np.random.seed(config.random_seed)

        # Pre-process dimensions for faster lookups
        self._prepare_lookups()

    def _prepare_lookups(self):
        """Prepare lookup structures from dimensions"""
        self.companies = self.dimensions["dim_company"]["company_code"].tolist()
        self.locations = self.dimensions["dim_locations"]["location_code"].tolist()
        self.org_1_codes = self.dimensions["dim_organizations"]["organization_code"].tolist()
        self.org_2_codes = self.dimensions["dim_organization_2"]["organization_code"].tolist()

        # Build job lookup by level
        jobs_df = self.dimensions["dim_jobs"]
        self.jobs_by_level = {}
        for level in jobs_df["job_level"].unique():
            self.jobs_by_level[level] = jobs_df[jobs_df["job_level"] == level][
                ["job_code", "job_family_code", "job"]
            ].to_dict("records")

        # Location-company mapping
        loc_comp = self.dimensions["dim_location_company"]
        self.locations_by_company = {}
        for company in self.companies:
            self.locations_by_company[company] = loc_comp[
                loc_comp["company_code"] == company
            ]["location_code"].tolist()

    def _add_months(self, d: date, months: int) -> date:
        """Safely add months to a date, handling month boundary issues"""
        month = d.month - 1 + months
        year = d.year + month // 12
        month = month % 12 + 1
        # Use day 1 to avoid issues with different month lengths
        return date(year, month, 1)

    def generate_population(self) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Generate the employee population.
        Returns:
            - dim_employee_info DataFrame
            - List of employee lifecycle events for fact table generation
        """
        employees = []
        lifecycle_events = []
        employee_number = 100001

        # Calculate hiring distribution across time
        hire_dates = self._generate_hire_date_distribution()

        for hire_date in hire_dates:
            emp, events = self._generate_employee(employee_number, hire_date)
            employees.append(emp)
            lifecycle_events.extend(events)
            employee_number += 1

        df = pd.DataFrame(employees)
        return df, lifecycle_events

    def _generate_hire_date_distribution(self) -> List[date]:
        """Generate realistic hire dates based on configuration"""
        hire_dates = []
        total_months = (
            (self.config.end_date.year - self.config.start_date.year) * 12
            + (self.config.end_date.month - self.config.start_date.month)
        )

        # Calculate target hires per month (accounting for attrition to maintain population)
        # Slightly more hires early on to build up population
        base_monthly_hires = self.config.target_employees / total_months * 1.3

        current = self.config.start_date
        while current < self.config.end_date and len(hire_dates) < self.config.target_employees:
            # Apply seasonal weight
            month_weight = self.config.monthly_hiring_weights[current.month - 1]
            monthly_hires = int(base_monthly_hires * month_weight)

            # Add some randomness
            monthly_hires = max(1, monthly_hires + random.randint(-3, 3))

            for _ in range(monthly_hires):
                if len(hire_dates) >= self.config.target_employees:
                    break
                # Random day within the month (business days preferred)
                day = random.randint(1, 28)
                hire_date = current.replace(day=day)
                # Avoid weekends for hire dates
                while hire_date.weekday() >= 5:
                    hire_date -= timedelta(days=1)
                hire_dates.append(hire_date)

            # Move to next month (using helper to handle month boundaries)
            current = self._add_months(current, 1)

        return sorted(hire_dates)

    def _generate_employee(
        self, employee_number: int, hire_date: date
    ) -> Tuple[Dict, List[Dict]]:
        """Generate a single employee with their lifecycle events"""

        # Basic demographics
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        # Age at hire (normal distribution)
        age_at_hire = int(
            np.clip(
                np.random.normal(
                    self.config.age_at_hire_mean, self.config.age_at_hire_std
                ),
                self.config.age_at_hire_min,
                self.config.age_at_hire_max,
            )
        )
        date_of_birth = hire_date - timedelta(days=age_at_hire * 365 + random.randint(0, 364))

        # Company and location
        company_code = random.choice(self.companies)
        location_options = self.locations_by_company.get(company_code, self.locations)
        location_code = random.choice(location_options) if location_options else random.choice(self.locations)

        # Job assignment based on level distribution
        job_level = self._select_job_level()
        job = random.choice(self.jobs_by_level.get(job_level, self.jobs_by_level["entry"]))

        # Organization
        org_1_code = random.choice(self.org_1_codes)
        org_2_code = random.choice(self.org_2_codes)

        # Employment type
        employee_type_code = self._select_employee_type()

        # FTE
        if employee_type_code in ["RPT", "CAS"]:
            scheduled_fte = round(random.uniform(0.4, 0.8), 2)
        else:
            scheduled_fte = 1.0

        # Salary/hourly based on job level
        if job_level in ["manager", "director", "executive", "lead", "senior"]:
            salaryhourly_code = "S"
        else:
            salaryhourly_code = random.choice(["H", "H", "H", "S"])  # Bias toward hourly for lower levels

        # Generate email
        email = self._generate_email(first_name, last_name, company_code)

        # Generate internal IDs
        eeceeid = f"EE{employee_number}"
        eeccoid = f"CO{self.companies.index(company_code) + 1:03d}"

        # Supervisor (will be assigned later in a second pass)
        supervisor_employee_number = None

        # Determine employee lifecycle (termination, rehires, etc.)
        lifecycle_events = self._generate_lifecycle(
            employee_number=employee_number,
            hire_date=hire_date,
            company_code=company_code,
            location_code=location_code,
            org_1_code=org_1_code,
            org_2_code=org_2_code,
            job_code=job["job_code"],
            job_family_code=job["job_family_code"],
            employee_type_code=employee_type_code,
            scheduled_fte=scheduled_fte,
            salaryhourly_code=salaryhourly_code,
            date_of_birth=date_of_birth,
        )

        # Determine current status based on lifecycle
        final_event = lifecycle_events[-1]
        employment_status_code = final_event.get("status_code", "A")
        termination_date = final_event.get("termination_date")

        employee = {
            "employee_number": employee_number,
            "eeceeid": eeceeid,
            "eeccoid": eeccoid,
            "first_name": first_name,
            "preferred_first_name": first_name,
            "last_name": last_name,
            "email_address": email,
            "date_of_birth": date_of_birth,
            "original_hire_date": hire_date,
            "seniority_date": hire_date,
            "retirement_date": None,
            "job_code": job["job_code"],
            "job_title": job["job"],
            "job_family_code": job["job_family_code"],
            "employee_type_code": employee_type_code,
            "employment_status_code": employment_status_code,
            "employment_status": self._get_status_name(employment_status_code),
            "company_code": company_code,
            "location_code": location_code,
            "org_level_1_code": org_1_code,
            "supervisor_employee_number": supervisor_employee_number,
            "supervisor_name": None,
            "supervisor_email": None,
            "primary_key": f"{employee_number}_{company_code}",
            "secondary_key": f"{eeceeid}_{eeccoid}",
            "scheduled_fte": scheduled_fte,
            "termination_date": termination_date,
        }

        return employee, lifecycle_events

    def _select_job_level(self) -> str:
        """Select job level based on configured distribution"""
        levels = list(self.config.job_level_distribution.keys())
        weights = list(self.config.job_level_distribution.values())
        return random.choices(levels, weights=weights, k=1)[0]

    def _select_employee_type(self) -> str:
        """Select employee type based on configured ratios"""
        roll = random.random()
        if roll < self.config.pct_contractor:
            return "CON"
        elif roll < self.config.pct_contractor + self.config.pct_temp:
            return random.choice(["TAW", "TFT"])
        elif roll < self.config.pct_contractor + self.config.pct_temp + (1 - self.config.pct_full_time):
            return "RPT"
        else:
            return "RFT"

    def _generate_email(self, first_name: str, last_name: str, company_code: str) -> str:
        """Generate realistic email address"""
        domain_map = {
            "NRTHP": "northernpipeline.com",
            "WSTMF": "westmarkmanufacturing.com",
            "PRMRE": "prairieresources.ca",
            "ALPNC": "alpineconstruction.com",
            "CSTLG": "coastallogistics.com",
            "MTNVW": "mountainviewenergy.com",
        }
        domain = domain_map.get(company_code, "company.com")
        # Clean names for email
        first = first_name.lower().replace("'", "").replace(" ", "")
        last = last_name.lower().replace("'", "").replace(" ", "")
        return f"{first}.{last}@{domain}"

    def _get_status_name(self, code: str) -> str:
        """Get status name from code"""
        status_map = {
            "A": "Active",
            "T": "Terminated",
            "L": "Leave of Absence",
            "S": "Suspended",
            "R": "Released/Laid Off",
        }
        return status_map.get(code, "Unknown")

    def _generate_lifecycle(
        self,
        employee_number: int,
        hire_date: date,
        company_code: str,
        location_code: str,
        org_1_code: str,
        org_2_code: str,
        job_code: str,
        job_family_code: str,
        employee_type_code: str,
        scheduled_fte: float,
        salaryhourly_code: str,
        date_of_birth: date,
    ) -> List[Dict]:
        """
        Generate lifecycle events for an employee.
        This creates realistic patterns of:
        - Initial hire
        - Potential job changes
        - Potential termination
        - Potential leaves of absence
        """
        events = []
        current_date = hire_date
        current_status = "A"
        current_job = job_code
        current_job_family = job_family_code
        current_location = location_code
        current_org_1 = org_1_code
        current_org_2 = org_2_code

        # Initial hire event
        events.append(
            {
                "employee_number": employee_number,
                "effective_date": hire_date,
                "transaction_type": "HIRE",
                "status_code": "A",
                "job_code": current_job,
                "job_family_code": current_job_family,
                "company_code": company_code,
                "location_code": current_location,
                "org_1_code": current_org_1,
                "org_2_code": current_org_2,
                "employee_type_code": employee_type_code,
                "scheduled_fte": scheduled_fte,
                "salaryhourly_code": salaryhourly_code,
                "termination_date": None,
                "termination_type_code": None,
                "termination_reason_code": None,
                "last_hire_date": hire_date,
                "date_in_job": hire_date,
            }
        )

        # Simulate lifecycle until end date or termination
        while current_date < self.config.end_date and current_status == "A":
            # Calculate tenure for attrition probability
            tenure_years = (current_date - hire_date).days / 365

            # Check for termination
            if self._should_terminate(tenure_years, employee_type_code):
                term_date = current_date + timedelta(days=random.randint(1, 60))
                if term_date > self.config.end_date:
                    break

                term_type, term_reason = self._get_termination_details(tenure_years, employee_type_code)

                events.append(
                    {
                        "employee_number": employee_number,
                        "effective_date": term_date,
                        "transaction_type": "TERMINATION",
                        "status_code": "T",
                        "job_code": current_job,
                        "job_family_code": current_job_family,
                        "company_code": company_code,
                        "location_code": current_location,
                        "org_1_code": current_org_1,
                        "org_2_code": current_org_2,
                        "employee_type_code": employee_type_code,
                        "scheduled_fte": scheduled_fte,
                        "salaryhourly_code": salaryhourly_code,
                        "termination_date": term_date,
                        "termination_type_code": term_type,
                        "termination_reason_code": term_reason,
                        "last_hire_date": hire_date,
                        "date_in_job": events[-1]["date_in_job"],
                    }
                )
                current_status = "T"
                break

            # Check for internal job change
            if random.random() < self.config.internal_mobility_rate / 12:  # Monthly check
                new_job = self._get_promotion_or_lateral(current_job)
                if new_job and new_job["job_code"] != current_job:
                    change_date = current_date + timedelta(days=random.randint(1, 30))
                    if change_date < self.config.end_date:
                        current_job = new_job["job_code"]
                        current_job_family = new_job["job_family_code"]

                        events.append(
                            {
                                "employee_number": employee_number,
                                "effective_date": change_date,
                                "transaction_type": "JOB_CHANGE",
                                "status_code": "A",
                                "job_code": current_job,
                                "job_family_code": current_job_family,
                                "company_code": company_code,
                                "location_code": current_location,
                                "org_1_code": current_org_1,
                                "org_2_code": current_org_2,
                                "employee_type_code": employee_type_code,
                                "scheduled_fte": scheduled_fte,
                                "salaryhourly_code": salaryhourly_code,
                                "termination_date": None,
                                "termination_type_code": None,
                                "termination_reason_code": None,
                                "last_hire_date": hire_date,
                                "date_in_job": change_date,
                            }
                        )

            # Check for leave of absence
            if random.random() < self.config.loa_rate / 12:  # Monthly check
                loa_start = current_date + timedelta(days=random.randint(1, 30))
                loa_duration = random.randint(14, 180)  # 2 weeks to 6 months
                loa_end = loa_start + timedelta(days=loa_duration)

                if loa_start < self.config.end_date:
                    events.append(
                        {
                            "employee_number": employee_number,
                            "effective_date": loa_start,
                            "transaction_type": "LOA_START",
                            "status_code": "L",
                            "job_code": current_job,
                            "job_family_code": current_job_family,
                            "company_code": company_code,
                            "location_code": current_location,
                            "org_1_code": current_org_1,
                            "org_2_code": current_org_2,
                            "employee_type_code": employee_type_code,
                            "scheduled_fte": scheduled_fte,
                            "salaryhourly_code": salaryhourly_code,
                            "termination_date": None,
                            "termination_type_code": None,
                            "termination_reason_code": None,
                            "last_hire_date": hire_date,
                            "date_in_job": events[-1]["date_in_job"],
                            "loa_reason_code": random.choice(["MED", "PER", "MAT", "PAT", "EDU"]),
                        }
                    )

                    if loa_end < self.config.end_date:
                        events.append(
                            {
                                "employee_number": employee_number,
                                "effective_date": loa_end,
                                "transaction_type": "LOA_RETURN",
                                "status_code": "A",
                                "job_code": current_job,
                                "job_family_code": current_job_family,
                                "company_code": company_code,
                                "location_code": current_location,
                                "org_1_code": current_org_1,
                                "org_2_code": current_org_2,
                                "employee_type_code": employee_type_code,
                                "scheduled_fte": scheduled_fte,
                                "salaryhourly_code": salaryhourly_code,
                                "termination_date": None,
                                "termination_type_code": None,
                                "termination_reason_code": None,
                                "last_hire_date": hire_date,
                                "date_in_job": events[-1]["date_in_job"],
                            }
                        )

            # Advance time by one month (safely handle month boundaries)
            current_date = self._add_months(current_date, 1)

        return events

    def _should_terminate(self, tenure_years: float, employee_type_code: str) -> bool:
        """Determine if employee should terminate based on tenure and type"""
        # Get base attrition rate for tenure bucket
        if tenure_years < 1:
            base_rate = self.config.attrition_rates["0-1_years"]
        elif tenure_years < 2:
            base_rate = self.config.attrition_rates["1-2_years"]
        elif tenure_years < 5:
            base_rate = self.config.attrition_rates["2-5_years"]
        elif tenure_years < 10:
            base_rate = self.config.attrition_rates["5-10_years"]
        else:
            base_rate = self.config.attrition_rates["10+_years"]

        # Adjust for employee type (temps/contractors have higher turnover)
        if employee_type_code in ["CON", "TAW", "TFT"]:
            base_rate *= 1.5

        # Monthly probability
        monthly_rate = base_rate / 12

        return random.random() < monthly_rate

    def _get_termination_details(
        self, tenure_years: float, employee_type_code: str
    ) -> Tuple[str, str]:
        """Get termination type and reason based on patterns"""
        # Temps often end due to assignment completion
        if employee_type_code in ["TAW", "TFT"]:
            if random.random() < 0.6:
                return "I", "201"  # End of temporary assignment

        # Contractors often leave for other opportunities
        if employee_type_code == "CON":
            if random.random() < 0.7:
                return "V", "100"  # Other employment

        # Voluntary vs involuntary
        if random.random() < self.config.pct_voluntary_terminations:
            term_type = "V"
            reasons = self.config.voluntary_reasons
        else:
            term_type = "I"
            reasons = self.config.involuntary_reasons

        # Select reason based on distribution
        reason_codes = list(reasons.keys())
        reason_weights = list(reasons.values())
        term_reason = random.choices(reason_codes, weights=reason_weights, k=1)[0]

        return term_type, term_reason

    def _get_promotion_or_lateral(self, current_job_code: str) -> Optional[Dict]:
        """Get a potential new job (promotion or lateral move)"""
        jobs_df = self.dimensions["dim_jobs"]
        current_job = jobs_df[jobs_df["job_code"] == current_job_code]

        if current_job.empty:
            return None

        current_level = current_job.iloc[0]["job_level"]
        current_family = current_job.iloc[0]["job_family_code"]

        # 70% chance of promotion, 30% lateral
        if random.random() < 0.7:
            # Promotion
            level_order = ["entry", "intermediate", "senior", "lead", "manager", "director", "executive"]
            try:
                current_idx = level_order.index(current_level)
                if current_idx < len(level_order) - 1:
                    next_level = level_order[current_idx + 1]
                    if next_level in self.jobs_by_level and self.jobs_by_level[next_level]:
                        # Prefer same family
                        same_family = [
                            j for j in self.jobs_by_level[next_level]
                            if j["job_family_code"] == current_family
                        ]
                        if same_family:
                            return random.choice(same_family)
                        return random.choice(self.jobs_by_level[next_level])
            except ValueError:
                pass
        else:
            # Lateral move (same level, different family)
            if current_level in self.jobs_by_level:
                diff_family = [
                    j for j in self.jobs_by_level[current_level]
                    if j["job_family_code"] != current_family
                ]
                if diff_family:
                    return random.choice(diff_family)

        return None

    def assign_supervisors(self, employees_df: pd.DataFrame) -> pd.DataFrame:
        """
        Assign supervisors to employees based on job levels.
        Higher level employees supervise lower level employees in same location/org.
        """
        df = employees_df.copy()
        jobs_df = self.dimensions["dim_jobs"]

        # Create job level lookup
        job_levels = dict(zip(jobs_df["job_code"], jobs_df["job_level"]))
        level_order = {"entry": 1, "intermediate": 2, "senior": 3, "lead": 4, "manager": 5, "director": 6, "executive": 7}

        df["job_level_num"] = df["job_code"].map(job_levels).map(level_order).fillna(1)

        # Group by location and org
        for (loc, org), group in df.groupby(["location_code", "org_level_1_code"]):
            # Sort by level descending
            sorted_group = group.sort_values("job_level_num", ascending=False)

            for idx, row in sorted_group.iterrows():
                if row["job_level_num"] >= 7:  # Executives don't have supervisors in this org
                    continue

                # Find potential supervisors (higher level in same org)
                potential_sups = sorted_group[
                    (sorted_group["job_level_num"] > row["job_level_num"])
                    & (sorted_group["employment_status_code"] == "A")
                    & (sorted_group["employee_number"] != row["employee_number"])
                ]

                if not potential_sups.empty:
                    supervisor = potential_sups.iloc[0]
                    df.loc[idx, "supervisor_employee_number"] = supervisor["employee_number"]
                    df.loc[idx, "supervisor_name"] = f"{supervisor['last_name']}, {supervisor['first_name']}"
                    df.loc[idx, "supervisor_email"] = supervisor["email_address"]

        df.drop(columns=["job_level_num"], inplace=True)
        return df
