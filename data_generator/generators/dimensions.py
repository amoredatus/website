"""
Dimension table generators for synthetic HR data
Generates: companies, locations, jobs, organizations, status codes, etc.
"""

import random
from datetime import date, timedelta
from typing import Dict, List, Any
import pandas as pd

from ..config import (
    GeneratorConfig,
    COMPANY_TEMPLATES,
    LOCATION_TEMPLATES,
    DEPARTMENT_TEMPLATES,
    JOB_FAMILY_TEMPLATES,
    JOB_TEMPLATES,
    STATUS_CODES,
    EMPLOYEE_TYPE_TEMPLATES,
    TERMINATION_TYPES,
    TERMINATION_REASONS,
)


class DimensionGenerator:
    """Generates all dimension tables for the synthetic HR data model"""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        random.seed(config.random_seed)
        self.dimensions: Dict[str, pd.DataFrame] = {}

    def generate_all(self) -> Dict[str, pd.DataFrame]:
        """Generate all dimension tables"""
        self.dimensions["dim_company"] = self._generate_companies()
        self.dimensions["dim_locations"] = self._generate_locations()
        self.dimensions["dim_location_company"] = self._generate_location_company()
        self.dimensions["dim_organizations"] = self._generate_org_level_1()
        self.dimensions["dim_organization_2"] = self._generate_org_level_2()
        self.dimensions["dim_job_family"] = self._generate_job_families()
        self.dimensions["dim_jobs"] = self._generate_jobs()
        self.dimensions["dim_status"] = self._generate_status()
        self.dimensions["dim_employee_type"] = self._generate_employee_types()
        self.dimensions["dim_termination_type"] = self._generate_termination_types()
        self.dimensions["dim_termination_reason"] = self._generate_termination_reasons()
        self.dimensions["dim_dates"] = self._generate_date_dimension()
        return self.dimensions

    def _generate_companies(self) -> pd.DataFrame:
        """Generate company dimension"""
        companies = COMPANY_TEMPLATES[: self.config.num_companies]
        records = []
        for i, comp in enumerate(companies):
            records.append(
                {
                    "company_code": comp["code"],
                    "company_name": comp["name"],
                    "cmpcoid": f"CP{100 + i}",
                }
            )
        return pd.DataFrame(records)

    def _generate_locations(self) -> pd.DataFrame:
        """Generate location dimension with realistic addresses"""
        locations = LOCATION_TEMPLATES[: self.config.num_locations]
        records = []

        street_types = ["Street", "Avenue", "Boulevard", "Drive", "Road", "Way", "Place"]
        street_names = [
            "Industrial", "Commerce", "Enterprise", "Business", "Corporate",
            "Technology", "Innovation", "Logistics", "Gateway", "Parkway",
            "Main", "First", "Second", "Third", "Oak", "Maple", "Pine",
        ]

        for i, loc in enumerate(locations):
            location_code = str(100 + i)
            street_num = random.randint(100, 9999)
            street_name = random.choice(street_names)
            street_type = random.choice(street_types)

            postal_code = self._generate_postal_code(loc["province"], loc["country"])

            records.append(
                {
                    "location_code": location_code,
                    "description": f"{loc['city']} Office",
                    "address_line_1": f"{street_num} {street_name} {street_type}",
                    "address_line_2": "",
                    "city": loc["city"],
                    "county": "",
                    "stateprovince_code": loc["province"],
                    "country": loc["country"],
                    "address_country_code": "CA" if loc["country"] == "Canada" else "US",
                    "zippostal_code": postal_code,
                    "latitude": None,
                    "longitude": None,
                    "timezone": self._get_timezone(loc["province"]),
                }
            )

        return pd.DataFrame(records)

    def _generate_postal_code(self, province: str, country: str) -> str:
        """Generate realistic postal/zip code"""
        if country == "USA":
            return f"{random.randint(10000, 99999)}"

        # Canadian postal codes by province
        prefix_map = {
            "AB": ["T"],
            "BC": ["V"],
            "SK": ["S"],
            "MB": ["R"],
            "ON": ["K", "L", "M", "N", "P"],
            "QC": ["G", "H", "J"],
            "NS": ["B"],
            "NB": ["E"],
            "NL": ["A"],
            "PE": ["C"],
            "YT": ["Y"],
            "NT": ["X"],
            "NU": ["X"],
        }
        prefix = random.choice(prefix_map.get(province, ["X"]))
        return f"{prefix}{random.randint(0,9)}{random.choice('ABCDEFGHJKLMNPRSTUVWXY')} {random.randint(0,9)}{random.choice('ABCDEFGHJKLMNPRSTUVWXY')}{random.randint(0,9)}"

    def _get_timezone(self, province: str) -> str:
        """Get timezone for province"""
        tz_map = {
            "AB": "America/Edmonton",
            "BC": "America/Vancouver",
            "SK": "America/Regina",
            "MB": "America/Winnipeg",
            "ON": "America/Toronto",
            "QC": "America/Montreal",
            "NS": "America/Halifax",
            "NB": "America/Moncton",
            "NL": "America/St_Johns",
            "AK": "America/Anchorage",
            "TX": "America/Chicago",
            "CO": "America/Denver",
        }
        return tz_map.get(province, "America/Edmonton")

    def _generate_location_company(self) -> pd.DataFrame:
        """Generate location-company junction table"""
        companies = self.dimensions["dim_company"]
        locations = self.dimensions["dim_locations"]

        records = []
        for _, company in companies.iterrows():
            # Each company has presence in some locations
            num_locations = random.randint(
                len(locations) // 3, len(locations)
            )
            company_locations = locations.sample(n=num_locations)

            for _, loc in company_locations.iterrows():
                records.append(
                    {
                        "company_code": company["company_code"],
                        "company_name": company["company_name"],
                        "location_code": loc["location_code"],
                        "location": loc["description"],
                        "inactivation_date": None,
                        "inactive": False,
                    }
                )

        return pd.DataFrame(records)

    def _generate_org_level_1(self) -> pd.DataFrame:
        """Generate level 1 organizations (business units/regions)"""
        records = []

        # Generate business units based on locations
        locations = self.dimensions["dim_locations"]
        org_code = 10

        for _, loc in locations.iterrows():
            records.append(
                {
                    "organization_code": str(org_code),
                    "report_category": "Operations",
                    "status_code": "A",
                    "status": "Active",
                    "organization": f"{loc['city']} Operations",
                }
            )
            org_code += 10

        # Ensure we don't exceed configured limit
        return pd.DataFrame(records[: self.config.num_org_level_1])

    def _generate_org_level_2(self) -> pd.DataFrame:
        """Generate level 2 organizations (departments)"""
        records = []
        for dept in DEPARTMENT_TEMPLATES[: self.config.num_org_level_2]:
            records.append(
                {
                    "level": 2,
                    "organization_code": dept["code"],
                    "report_category": "Department",
                    "status_code": "A",
                    "status": "Active",
                    "organization": dept["name"],
                }
            )
        return pd.DataFrame(records)

    def _generate_job_families(self) -> pd.DataFrame:
        """Generate job family dimension"""
        records = []
        for family in JOB_FAMILY_TEMPLATES:
            records.append(
                {"job_family_code": family["code"], "job_family": family["name"]}
            )
        return pd.DataFrame(records)

    def _generate_jobs(self) -> pd.DataFrame:
        """Generate jobs dimension with realistic job codes"""
        records = []
        job_counter = 1

        level_map = {
            "entry": 1,
            "intermediate": 2,
            "senior": 3,
            "lead": 4,
            "manager": 5,
            "director": 6,
            "executive": 7,
        }

        for family_code, jobs in JOB_TEMPLATES.items():
            for job in jobs:
                job_code = f"{job_counter:02d}{family_code[:3].upper()}{level_map[job['level']]}"
                records.append(
                    {
                        "job_code": job_code,
                        "job_family_code": family_code,
                        "job": job["title"],
                        "job_level": job["level"],
                        "is_supervisor": job["level"] in ["lead", "manager", "director", "executive"],
                        "is_staff": job["level"] not in ["entry", "intermediate"],
                        "noc_group": None,
                        "work_environment_code": "O" if job["level"] in ["manager", "director", "executive"] else "F",
                    }
                )
                job_counter += 1

        return pd.DataFrame(records)

    def _generate_status(self) -> pd.DataFrame:
        """Generate status code dimension"""
        records = []
        for code, status in STATUS_CODES.items():
            records.append({"status_code": code, "status": status})
        return pd.DataFrame(records)

    def _generate_employee_types(self) -> pd.DataFrame:
        """Generate employee type dimension"""
        records = []
        for emp_type in EMPLOYEE_TYPE_TEMPLATES:
            records.append(
                {"employee_type_code": emp_type["code"], "employee_type": emp_type["name"]}
            )
        return pd.DataFrame(records)

    def _generate_termination_types(self) -> pd.DataFrame:
        """Generate termination type dimension"""
        records = []
        for code, term_type in TERMINATION_TYPES.items():
            records.append(
                {"termination_type_code": code, "termination_type": term_type}
            )
        return pd.DataFrame(records)

    def _generate_termination_reasons(self) -> pd.DataFrame:
        """Generate termination reason dimension"""
        records = []
        for reason in TERMINATION_REASONS:
            records.append(
                {
                    "code": reason["code"],
                    "type_code": reason["type"],
                    "description": reason["description"],
                    "type": TERMINATION_TYPES[reason["type"]],
                }
            )
        return pd.DataFrame(records)

    def _generate_date_dimension(self) -> pd.DataFrame:
        """Generate a comprehensive date dimension"""
        records = []

        # Generate dates from 5 years before start_date to end_date
        start = date(self.config.start_date.year - 5, 1, 1)
        end = self.config.end_date

        current = start
        while current <= end:
            is_weekend = current.weekday() >= 5

            records.append(
                {
                    "date_key": int(current.strftime("%Y%m%d")),
                    "date": current,
                    "calendar_year": current.year,
                    "calendar_month": current.month,
                    "calendar_month_name": current.strftime("%B"),
                    "calendar_day": current.day,
                    "calendar_quarter": (current.month - 1) // 3 + 1,
                    "day_of_week": current.weekday(),
                    "day_of_week_name": current.strftime("%A"),
                    "iso_year": current.isocalendar()[0],
                    "iso_week_number": current.isocalendar()[1],
                    "month_start_date": current.replace(day=1),
                    "month_end_date": self._get_month_end(current),
                    "is_month_end": current == self._get_month_end(current),
                    "is_business_day": not is_weekend,
                    "day_of_year": current.timetuple().tm_yday,
                    "is_leap_year": current.year % 4 == 0
                    and (current.year % 100 != 0 or current.year % 400 == 0),
                    "month_year": current.strftime("%b %Y"),
                    "quarter_year": f"Q{(current.month - 1) // 3 + 1} {current.year}",
                }
            )
            current += timedelta(days=1)

        return pd.DataFrame(records)

    def _get_month_end(self, d: date) -> date:
        """Get the last day of the month"""
        if d.month == 12:
            return d.replace(day=31)
        return d.replace(month=d.month + 1, day=1) - timedelta(days=1)
