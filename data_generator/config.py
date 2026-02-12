"""
Configuration for synthetic data generation
All parameters for generating realistic workforce data
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List

@dataclass
class GeneratorConfig:
    """Configuration parameters for synthetic data generation"""

    # Population settings
    target_employees: int = 3000  # Total employees to generate
    start_date: date = field(default_factory=lambda: date(2018, 1, 1))
    end_date: date = field(default_factory=lambda: date(2026, 1, 31))

    # Company settings
    num_companies: int = 4

    # Location settings
    num_locations: int = 25

    # Organization settings
    num_org_level_1: int = 40  # Business units / regions
    num_org_level_2: int = 12  # Departments

    # Workforce composition (percentages)
    pct_full_time: float = 0.85
    pct_salaried: float = 0.35
    pct_contractor: float = 0.08
    pct_temp: float = 0.05

    # Attrition patterns (annual rates by tenure bucket)
    attrition_rates: Dict[str, float] = field(default_factory=lambda: {
        "0-1_years": 0.25,   # 25% annual attrition in first year
        "1-2_years": 0.18,
        "2-5_years": 0.12,
        "5-10_years": 0.08,
        "10+_years": 0.05
    })

    # Termination reason distribution (for voluntary)
    voluntary_reasons: Dict[str, float] = field(default_factory=lambda: {
        "100": 0.40,  # Other job
        "101": 0.25,  # Personal/Family
        "102": 0.15,  # Moving
        "103": 0.08,  # Education
        "202": 0.12   # Retirement
    })

    # Termination reason distribution (for involuntary)
    involuntary_reasons: Dict[str, float] = field(default_factory=lambda: {
        "200": 0.30,  # Lack of work
        "201": 0.15,  # Temporary job ended
        "205": 0.25,  # Performance
        "206": 0.10,  # Gross misconduct
        "207": 0.15,  # Failed probation
        "210": 0.05   # Non-culpable
    })

    # Voluntary vs involuntary split
    pct_voluntary_terminations: float = 0.70

    # Hiring patterns (relative weight by month, 1-12)
    monthly_hiring_weights: List[float] = field(default_factory=lambda: [
        0.8,   # January
        0.7,   # February
        1.0,   # March
        1.1,   # April
        1.2,   # May
        1.0,   # June
        0.9,   # July
        0.8,   # August
        1.3,   # September (back to school hiring)
        1.1,   # October
        0.7,   # November
        0.4    # December
    ])

    # Age distribution at hire
    age_at_hire_mean: float = 32
    age_at_hire_std: float = 10
    age_at_hire_min: int = 18
    age_at_hire_max: int = 65

    # Job level distribution (approximate pyramid)
    job_level_distribution: Dict[str, float] = field(default_factory=lambda: {
        "entry": 0.35,
        "intermediate": 0.30,
        "senior": 0.20,
        "lead": 0.10,
        "manager": 0.04,
        "director": 0.008,
        "executive": 0.002
    })

    # Internal mobility rate (job changes per year for active employees)
    internal_mobility_rate: float = 0.15

    # Leave of absence rate
    loa_rate: float = 0.03

    # Output settings
    output_dir: str = "output"
    output_format: str = "csv"  # csv or parquet

    # Random seed for reproducibility
    random_seed: int = 42


# Realistic company names for synthetic data
COMPANY_TEMPLATES = [
    {"code": "NRTHP", "name": "Northern Pipeline Services Inc."},
    {"code": "WSTMF", "name": "Westmark Manufacturing Co."},
    {"code": "PRMRE", "name": "Prairie Resources Ltd."},
    {"code": "ALPNC", "name": "Alpine Construction Group"},
    {"code": "CSTLG", "name": "Coastal Logistics Corp."},
    {"code": "MTNVW", "name": "Mountain View Energy"},
]

# Realistic location templates (Canadian focus)
LOCATION_TEMPLATES = [
    {"city": "Calgary", "province": "AB", "country": "Canada"},
    {"city": "Edmonton", "province": "AB", "country": "Canada"},
    {"city": "Vancouver", "province": "BC", "country": "Canada"},
    {"city": "Toronto", "province": "ON", "country": "Canada"},
    {"city": "Mississauga", "province": "ON", "country": "Canada"},
    {"city": "Saskatoon", "province": "SK", "country": "Canada"},
    {"city": "Regina", "province": "SK", "country": "Canada"},
    {"city": "Winnipeg", "province": "MB", "country": "Canada"},
    {"city": "Fort McMurray", "province": "AB", "country": "Canada"},
    {"city": "Grande Prairie", "province": "AB", "country": "Canada"},
    {"city": "Red Deer", "province": "AB", "country": "Canada"},
    {"city": "Lethbridge", "province": "AB", "country": "Canada"},
    {"city": "Kamloops", "province": "BC", "country": "Canada"},
    {"city": "Prince George", "province": "BC", "country": "Canada"},
    {"city": "Kelowna", "province": "BC", "country": "Canada"},
    {"city": "Ottawa", "province": "ON", "country": "Canada"},
    {"city": "Hamilton", "province": "ON", "country": "Canada"},
    {"city": "London", "province": "ON", "country": "Canada"},
    {"city": "Thunder Bay", "province": "ON", "country": "Canada"},
    {"city": "Sudbury", "province": "ON", "country": "Canada"},
    {"city": "Halifax", "province": "NS", "country": "Canada"},
    {"city": "Saint John", "province": "NB", "country": "Canada"},
    {"city": "Moncton", "province": "NB", "country": "Canada"},
    {"city": "St. John's", "province": "NL", "country": "Canada"},
    {"city": "Anchorage", "province": "AK", "country": "USA"},
    {"city": "Fairbanks", "province": "AK", "country": "USA"},
    {"city": "Houston", "province": "TX", "country": "USA"},
    {"city": "Denver", "province": "CO", "country": "USA"},
]

# Department/Org Level 2 templates
DEPARTMENT_TEMPLATES = [
    {"code": "10", "name": "Operations"},
    {"code": "20", "name": "Service"},
    {"code": "30", "name": "Sales"},
    {"code": "40", "name": "Parts"},
    {"code": "50", "name": "Finance & Accounting"},
    {"code": "60", "name": "Human Resources"},
    {"code": "70", "name": "Information Technology"},
    {"code": "80", "name": "Marketing"},
    {"code": "90", "name": "Legal & Compliance"},
    {"code": "100", "name": "Supply Chain"},
    {"code": "110", "name": "Quality Assurance"},
    {"code": "120", "name": "Health & Safety"},
]

# Job family templates
JOB_FAMILY_TEMPLATES = [
    {"code": "ADMIN", "name": "Administrative"},
    {"code": "ACCTG", "name": "Accounting"},
    {"code": "CSR", "name": "Customer Service"},
    {"code": "ENGR", "name": "Engineering"},
    {"code": "HR", "name": "Human Resources"},
    {"code": "IT", "name": "Information Technology"},
    {"code": "LEGAL", "name": "Legal"},
    {"code": "MGR", "name": "Management"},
    {"code": "MKTG", "name": "Marketing"},
    {"code": "OPS", "name": "Operations"},
    {"code": "SALES", "name": "Sales"},
    {"code": "TECH", "name": "Technical"},
    {"code": "TRD", "name": "Trades"},
    {"code": "WHSE", "name": "Warehouse"},
    {"code": "SUPV", "name": "Supervision"},
    {"code": "EXEC", "name": "Executive"},
    {"code": "ANLYT", "name": "Analytics"},
    {"code": "PROJ", "name": "Project Management"},
]

# Job templates by family and level
JOB_TEMPLATES = {
    "ADMIN": [
        {"level": "entry", "title": "Administrative Assistant"},
        {"level": "intermediate", "title": "Administrative Coordinator"},
        {"level": "senior", "title": "Senior Administrative Coordinator"},
        {"level": "lead", "title": "Executive Assistant"},
    ],
    "ACCTG": [
        {"level": "entry", "title": "Accounts Payable Clerk"},
        {"level": "entry", "title": "Accounts Receivable Clerk"},
        {"level": "intermediate", "title": "Accountant"},
        {"level": "senior", "title": "Senior Accountant"},
        {"level": "lead", "title": "Accounting Lead"},
        {"level": "manager", "title": "Accounting Manager"},
        {"level": "director", "title": "Controller"},
        {"level": "executive", "title": "Chief Financial Officer"},
    ],
    "CSR": [
        {"level": "entry", "title": "Customer Service Representative"},
        {"level": "intermediate", "title": "Customer Service Specialist"},
        {"level": "senior", "title": "Senior Customer Service Specialist"},
        {"level": "lead", "title": "Customer Service Team Lead"},
        {"level": "manager", "title": "Customer Service Manager"},
    ],
    "ENGR": [
        {"level": "entry", "title": "Junior Engineer"},
        {"level": "intermediate", "title": "Engineer"},
        {"level": "senior", "title": "Senior Engineer"},
        {"level": "lead", "title": "Principal Engineer"},
        {"level": "manager", "title": "Engineering Manager"},
        {"level": "director", "title": "Director of Engineering"},
        {"level": "executive", "title": "VP of Engineering"},
    ],
    "HR": [
        {"level": "entry", "title": "HR Coordinator"},
        {"level": "intermediate", "title": "HR Generalist"},
        {"level": "senior", "title": "Senior HR Generalist"},
        {"level": "lead", "title": "HR Business Partner"},
        {"level": "manager", "title": "HR Manager"},
        {"level": "director", "title": "Director of Human Resources"},
        {"level": "executive", "title": "Chief People Officer"},
    ],
    "IT": [
        {"level": "entry", "title": "IT Support Technician"},
        {"level": "intermediate", "title": "Systems Administrator"},
        {"level": "intermediate", "title": "Software Developer"},
        {"level": "senior", "title": "Senior Developer"},
        {"level": "senior", "title": "Senior Systems Administrator"},
        {"level": "lead", "title": "Technical Lead"},
        {"level": "manager", "title": "IT Manager"},
        {"level": "director", "title": "Director of IT"},
        {"level": "executive", "title": "Chief Information Officer"},
    ],
    "SALES": [
        {"level": "entry", "title": "Sales Representative"},
        {"level": "intermediate", "title": "Account Executive"},
        {"level": "senior", "title": "Senior Account Executive"},
        {"level": "lead", "title": "Sales Team Lead"},
        {"level": "manager", "title": "Sales Manager"},
        {"level": "director", "title": "Director of Sales"},
        {"level": "executive", "title": "VP of Sales"},
    ],
    "OPS": [
        {"level": "entry", "title": "Operations Assistant"},
        {"level": "intermediate", "title": "Operations Coordinator"},
        {"level": "senior", "title": "Operations Specialist"},
        {"level": "lead", "title": "Operations Lead"},
        {"level": "manager", "title": "Operations Manager"},
        {"level": "director", "title": "Director of Operations"},
        {"level": "executive", "title": "Chief Operating Officer"},
    ],
    "TRD": [
        {"level": "entry", "title": "Apprentice Technician"},
        {"level": "intermediate", "title": "Journeyman Technician"},
        {"level": "senior", "title": "Senior Technician"},
        {"level": "lead", "title": "Lead Technician"},
        {"level": "manager", "title": "Shop Foreman"},
    ],
    "WHSE": [
        {"level": "entry", "title": "Warehouse Associate"},
        {"level": "intermediate", "title": "Warehouse Clerk"},
        {"level": "senior", "title": "Senior Warehouse Clerk"},
        {"level": "lead", "title": "Warehouse Lead"},
        {"level": "manager", "title": "Warehouse Manager"},
    ],
    "TECH": [
        {"level": "entry", "title": "Field Technician"},
        {"level": "intermediate", "title": "Service Technician"},
        {"level": "senior", "title": "Senior Service Technician"},
        {"level": "lead", "title": "Technical Specialist"},
        {"level": "manager", "title": "Technical Services Manager"},
    ],
    "MKTG": [
        {"level": "entry", "title": "Marketing Coordinator"},
        {"level": "intermediate", "title": "Marketing Specialist"},
        {"level": "senior", "title": "Senior Marketing Specialist"},
        {"level": "lead", "title": "Marketing Lead"},
        {"level": "manager", "title": "Marketing Manager"},
        {"level": "director", "title": "Director of Marketing"},
        {"level": "executive", "title": "Chief Marketing Officer"},
    ],
    "ANLYT": [
        {"level": "entry", "title": "Data Analyst"},
        {"level": "intermediate", "title": "Business Analyst"},
        {"level": "senior", "title": "Senior Data Analyst"},
        {"level": "lead", "title": "Analytics Lead"},
        {"level": "manager", "title": "Analytics Manager"},
        {"level": "director", "title": "Director of Analytics"},
    ],
    "SUPV": [
        {"level": "lead", "title": "Shift Supervisor"},
        {"level": "manager", "title": "Area Supervisor"},
        {"level": "manager", "title": "Regional Supervisor"},
    ],
    "EXEC": [
        {"level": "executive", "title": "Chief Executive Officer"},
        {"level": "executive", "title": "President"},
        {"level": "director", "title": "Vice President"},
    ],
    "PROJ": [
        {"level": "intermediate", "title": "Project Coordinator"},
        {"level": "senior", "title": "Project Manager"},
        {"level": "lead", "title": "Senior Project Manager"},
        {"level": "manager", "title": "Program Manager"},
        {"level": "director", "title": "Director of PMO"},
    ],
    "LEGAL": [
        {"level": "intermediate", "title": "Paralegal"},
        {"level": "senior", "title": "Legal Counsel"},
        {"level": "lead", "title": "Senior Legal Counsel"},
        {"level": "director", "title": "General Counsel"},
    ],
}

# Employee status codes
STATUS_CODES = {
    "A": "Active",
    "T": "Terminated",
    "L": "Leave of Absence",
    "S": "Suspended",
    "R": "Released/Laid Off",
}

# Employee type templates
EMPLOYEE_TYPE_TEMPLATES = [
    {"code": "RFT", "name": "Regular Full Time"},
    {"code": "RPT", "name": "Regular Part Time"},
    {"code": "CON", "name": "Contractor"},
    {"code": "TAW", "name": "Temporary Assignment"},
    {"code": "TFT", "name": "Temporary Fixed Term"},
    {"code": "CAS", "name": "Casual"},
    {"code": "INT", "name": "Intern"},
]

# Termination types
TERMINATION_TYPES = {
    "V": "Voluntary",
    "I": "Involuntary",
    "T": "Transfer",
}

# Termination reasons
TERMINATION_REASONS = [
    {"code": "100", "type": "V", "description": "Other Employment Opportunity"},
    {"code": "101", "type": "V", "description": "Personal/Family Reasons"},
    {"code": "102", "type": "V", "description": "Relocation"},
    {"code": "103", "type": "V", "description": "Return to Education"},
    {"code": "202", "type": "V", "description": "Retirement"},
    {"code": "200", "type": "I", "description": "Lack of Work"},
    {"code": "201", "type": "I", "description": "End of Temporary Assignment"},
    {"code": "205", "type": "I", "description": "Performance"},
    {"code": "206", "type": "I", "description": "Misconduct"},
    {"code": "207", "type": "I", "description": "Failed Probation"},
    {"code": "210", "type": "I", "description": "Position Elimination"},
    {"code": "TRO", "type": "T", "description": "Transfer Out"},
]

# First names for synthetic data (gender-neutral mix)
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Carolyn", "Patrick", "Janet", "Jack", "Catherine",
    "Dennis", "Maria", "Jerry", "Heather", "Tyler", "Diane", "Aaron", "Ruth",
    "Jose", "Julie", "Adam", "Olivia", "Nathan", "Joyce", "Henry", "Virginia",
    "Wei", "Priya", "Mohammed", "Fatima", "Carlos", "Sofia", "Raj", "Aisha",
    "Yuki", "Mei", "Ahmed", "Zara", "Dmitri", "Olga", "Pierre", "Marie",
    "Hans", "Ingrid", "Giovanni", "Isabella", "Kenji", "Sakura", "Lars", "Astrid",
]

# Last names for synthetic data
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
    "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers",
    "Long", "Ross", "Foster", "Jimenez", "Chen", "Singh", "Kumar", "Shah",
    "Wong", "Zhang", "Li", "Wang", "Liu", "Yamamoto", "Tanaka", "Mueller",
    "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz",
    "Eriksson", "Larsson", "Johansson", "Karlsson", "Andersson", "Nilsson", "Olsson", "Persson",
]
