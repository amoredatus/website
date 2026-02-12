"""
Main orchestrator for synthetic HR data generation
Coordinates all generators and handles output
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

from .config import GeneratorConfig
from .generators import DimensionGenerator, EmployeeGenerator, FactGenerator


class SyntheticDataGenerator:
    """
    Main class for generating synthetic HR/workforce data.

    This generator creates realistic workforce data that mirrors
    a real HRIS system's output, suitable for demos, training,
    and analytics development.

    Usage:
        from data_generator import SyntheticDataGenerator

        generator = SyntheticDataGenerator()
        generator.generate()
        generator.save_all()
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """
        Initialize the generator.

        Args:
            config: Optional GeneratorConfig. If not provided, uses defaults.
        """
        self.config = config or GeneratorConfig()
        self.dimensions: Dict[str, pd.DataFrame] = {}
        self.employees: Optional[pd.DataFrame] = None
        self.facts: Dict[str, pd.DataFrame] = {}
        self.analytics: Dict[str, pd.DataFrame] = {}
        self._generated = False

    def generate(self, verbose: bool = True) -> "SyntheticDataGenerator":
        """
        Generate all synthetic data.

        Args:
            verbose: If True, print progress messages.

        Returns:
            self for method chaining.
        """
        if verbose:
            print("=" * 60)
            print("SYNTHETIC HR DATA GENERATOR")
            print("=" * 60)
            print(f"\nConfiguration:")
            print(f"  - Target employees: {self.config.target_employees:,}")
            print(f"  - Date range: {self.config.start_date} to {self.config.end_date}")
            print(f"  - Companies: {self.config.num_companies}")
            print(f"  - Locations: {self.config.num_locations}")
            print()

        # Step 1: Generate dimensions
        if verbose:
            print("[1/4] Generating dimension tables...")
        dim_gen = DimensionGenerator(self.config)
        self.dimensions = dim_gen.generate_all()
        if verbose:
            for name, df in self.dimensions.items():
                print(f"       {name}: {len(df):,} rows")

        # Step 2: Generate employee population
        if verbose:
            print("\n[2/4] Generating employee population...")
        emp_gen = EmployeeGenerator(self.config, self.dimensions)
        self.employees, lifecycle_events = emp_gen.generate_population()
        if verbose:
            print(f"       Generated {len(self.employees):,} employees")
            print(f"       Generated {len(lifecycle_events):,} lifecycle events")

        # Step 3: Assign supervisors
        if verbose:
            print("\n[3/4] Assigning supervisors...")
        self.employees = emp_gen.assign_supervisors(self.employees)
        assigned = self.employees["supervisor_employee_number"].notna().sum()
        if verbose:
            print(f"       Assigned supervisors to {assigned:,} employees")

        # Add employees to dimensions
        self.dimensions["dim_employee_info"] = self.employees

        # Step 4: Generate fact tables
        if verbose:
            print("\n[4/4] Generating fact tables...")
        fact_gen = FactGenerator(
            self.config, self.dimensions, self.employees, lifecycle_events
        )
        self.facts = fact_gen.generate_all()
        if verbose:
            for name, df in self.facts.items():
                print(f"       {name}: {len(df):,} rows")

        # Generate analytics summaries
        if verbose:
            print("\n[+] Generating analytics summaries...")
        self.analytics = fact_gen.generate_analytics_summary()
        if verbose:
            for name, df in self.analytics.items():
                print(f"       {name}: {len(df):,} rows")

        self._generated = True

        if verbose:
            print("\n" + "=" * 60)
            print("GENERATION COMPLETE")
            print("=" * 60)
            self._print_summary()

        return self

    def _print_summary(self):
        """Print summary statistics of generated data"""
        emp_df = self.dimensions["dim_employee_info"]
        fact_df = self.facts.get("fact_employee_history", pd.DataFrame())

        print("\nData Summary:")
        print(f"  - Total employees generated: {len(emp_df):,}")
        print(f"  - Active employees (current): {(emp_df['employment_status_code'] == 'A').sum():,}")
        print(f"  - Terminated employees: {(emp_df['employment_status_code'] == 'T').sum():,}")

        if not fact_df.empty:
            latest_month = fact_df["report_date"].max()
            latest_data = fact_df[fact_df["report_date"] == latest_month]
            print(f"\n  Latest snapshot ({latest_month}):")
            print(f"    - Headcount: {latest_data['f_active'].sum():,}")
            print(f"    - FTE: {latest_data[latest_data['f_active'] == 1]['scheduled_fte'].sum():,.1f}")

        if "termination_history" in self.facts:
            term_df = self.facts["termination_history"]
            print(f"\n  Terminations:")
            print(f"    - Total terminations: {len(term_df):,}")
            if "termination_type_code" in term_df.columns:
                vol = (term_df["termination_type_code"] == "V").sum()
                invol = (term_df["termination_type_code"] == "I").sum()
                print(f"    - Voluntary: {vol:,} ({vol/len(term_df)*100:.1f}%)")
                print(f"    - Involuntary: {invol:,} ({invol/len(term_df)*100:.1f}%)")

    def save_all(
        self,
        output_dir: Optional[str] = None,
        format: str = "csv",
        include_analytics: bool = True,
    ) -> Path:
        """
        Save all generated data to files.

        Args:
            output_dir: Output directory. Defaults to config.output_dir.
            format: Output format ('csv' or 'parquet').
            include_analytics: If True, also save analytics summaries.

        Returns:
            Path to the output directory.
        """
        if not self._generated:
            raise RuntimeError("Must call generate() before save_all()")

        output_dir = output_dir or self.config.output_dir
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(output_dir) / f"run_{timestamp}"

        # Create directory structure
        bronze_path = output_path / "bronze"
        silver_path = output_path / "silver"
        gold_path = output_path / "gold"

        for p in [bronze_path, silver_path, gold_path]:
            p.mkdir(parents=True, exist_ok=True)

        print(f"\nSaving data to: {output_path}")

        # Save dimensions (bronze layer)
        print("\nSaving bronze layer (dimensions)...")
        for name, df in self.dimensions.items():
            self._save_df(df, bronze_path / f"{name}.{format}", format)
            print(f"  - {name}.{format}")

        # Save job history (bronze layer)
        if "job_history" in self.facts:
            self._save_df(
                self.facts["job_history"], bronze_path / f"job_history.{format}", format
            )
            print(f"  - job_history.{format}")

        # Save termination history (silver layer)
        if "termination_history" in self.facts:
            self._save_df(
                self.facts["termination_history"],
                silver_path / f"termination_history.{format}",
                format,
            )
            print(f"  - termination_history.{format}")

        # Save fact employee history (gold layer)
        print("\nSaving gold layer (facts)...")
        if "fact_employee_history" in self.facts:
            self._save_df(
                self.facts["fact_employee_history"],
                gold_path / f"fact_employee_history.{format}",
                format,
            )
            print(f"  - fact_employee_history.{format}")

        # Save analytics summaries
        if include_analytics and self.analytics:
            analytics_path = output_path / "analytics"
            analytics_path.mkdir(parents=True, exist_ok=True)
            print("\nSaving analytics summaries...")
            for name, df in self.analytics.items():
                self._save_df(df, analytics_path / f"{name}.{format}", format)
                print(f"  - {name}.{format}")

        print(f"\nAll data saved to: {output_path}")
        return output_path

    def _save_df(self, df: pd.DataFrame, path: Path, format: str):
        """Save a DataFrame to file"""
        if format == "parquet":
            df.to_parquet(path, index=False)
        else:
            df.to_csv(path, index=False)

    def get_dimension(self, name: str) -> pd.DataFrame:
        """Get a dimension table by name"""
        if not self._generated:
            raise RuntimeError("Must call generate() first")
        return self.dimensions.get(name, pd.DataFrame())

    def get_fact(self, name: str) -> pd.DataFrame:
        """Get a fact table by name"""
        if not self._generated:
            raise RuntimeError("Must call generate() first")
        return self.facts.get(name, pd.DataFrame())

    def get_employees(self) -> pd.DataFrame:
        """Get the employee dimension table"""
        return self.get_dimension("dim_employee_info")

    def get_monthly_headcount(self) -> pd.DataFrame:
        """Get the monthly headcount summary"""
        if not self._generated:
            raise RuntimeError("Must call generate() first")
        return self.analytics.get("monthly_headcount", pd.DataFrame())


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate synthetic HR data for demos and development"
    )
    parser.add_argument(
        "--employees",
        type=int,
        default=3000,
        help="Number of employees to generate (default: 3000)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output directory (default: output)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "parquet"],
        default="csv",
        help="Output format (default: csv)",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2018,
        help="Start year for data generation (default: 2018)",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=2026,
        help="End year for data generation (default: 2026)",
    )

    args = parser.parse_args()

    from datetime import date

    config = GeneratorConfig(
        target_employees=args.employees,
        output_dir=args.output,
        output_format=args.format,
        random_seed=args.seed,
        start_date=date(args.start_year, 1, 1),
        end_date=date(args.end_year, 1, 31),
    )

    generator = SyntheticDataGenerator(config)
    generator.generate()
    generator.save_all(format=args.format)


if __name__ == "__main__":
    main()
