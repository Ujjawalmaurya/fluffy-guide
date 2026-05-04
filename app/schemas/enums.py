"""
SkillBridge AI — Enumerations
All string-based categorical fields defined here.
"""
from enum import Enum


class UserRole(str, Enum):
    """System-level user roles/categories."""
    USER = "user"
    STUDENT = "individual_youth"
    BLUE_COLLAR = "individual_bluecollar"
    INFORMAL = "individual_informal"
    NGO = "org_ngo"
    EMPLOYER = "org_employer"
    GOVT_OFFICER = "org_govt"


class CareerStage(str, Enum):
    STUDENT = "student"
    FRESHER = "fresher"
    EARLY = "early"
    MID = "mid"
    SENIOR = "senior"
    BLUE_COLLAR = "blue_collar"
    INFORMAL = "informal"


class EducationLevel(str, Enum):
    NONE = "none"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HIGHER_SECONDARY = "higher_secondary"
    GRADUATE = "graduate"
    POSTGRADUATE = "postgraduate"
    VOCATIONAL = "vocational"
    DROPOUT = "dropout"
    TEN = "10th"
    TWELVE = "12th"


class EducationStream(str, Enum):
    SCIENCE = "science"
    COMMERCE = "commerce"
    ARTS = "arts"
    VOCATIONAL = "vocational"
    OTHER = "other"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    GIG = "gig"
    APPRENTICESHIP = "apprenticeship"
    INTERNSHIP = "internship"


class WorkMode(str, Enum):
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class SkillCategory(str, Enum):
    TECHNICAL = "technical"
    SOFT = "soft"
    VOCATIONAL = "vocational"
    DIGITAL = "digital"
    LANGUAGE = "language"
    DOMAIN = "domain"


class TrainingStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"


class PlacementStatus(str, Enum):
    PLACED = "placed"
    NOT_PLACED = "not_placed"
    IN_PROCESS = "in_process"
    SELF_EMPLOYED = "self_employed"


class AssessmentType(str, Enum):
    QUIZ = "quiz"
    MOCK_INTERVIEW = "mock_interview"
    CODING = "coding"
    PRACTICAL = "practical"
    LANGUAGE = "language"


class Language(str, Enum):
    HINDI = "hindi"
    ENGLISH = "english"
    HINGLISH = "hinglish"


class Region(str, Enum):
    # Common Indian states/UTs
    ANDHRA_PRADESH = "andhra_pradesh"
    ARUNACHAL_PRADESH = "arunachal_pradesh"
    ASSAM = "assam"
    BIHAR = "bihar"
    CHHATTISGARH = "chhattisgarh"
    GOA = "goa"
    GUJARAT = "gujarat"
    HARYANA = "haryana"
    HIMACHAL_PRADESH = "himachal_pradesh"
    JHARKHAND = "jharkhand"
    KARNATAKA = "karnataka"
    KERALA = "kerala"
    MADHYA_PRADESH = "madhya_pradesh"
    MAHARASHTRA = "maharashtra"
    MANIPUR = "manipur"
    MEGHALAYA = "meghalaya"
    MIZORAM = "mizoram"
    NAGALAND = "nagaland"
    ODISHA = "odisha"
    PUNJAB = "punjab"
    RAJASTHAN = "rajasthan"
    SIKKIM = "sikkim"
    TAMIL_NADU = "tamil_nadu"
    TELANGANA = "telangana"
    TRIPURA = "tripura"
    UTTAR_PRADESH = "uttar_pradesh"
    UTTARAKHAND = "uttarakhand"
    WEST_BENGAL = "west_bengal"
    DELHI = "delhi"
    JAMMU_KASHMIR = "jammu_kashmir"
    LADAKH = "ladakh"
    OTHER = "other"


class TradeSkill(str, Enum):
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"
    CARPENTER = "carpenter"
    WELDER = "welder"
    MASON = "mason"
    PAINTER = "painter"
    MECHANIC = "mechanic"
    OTHER = "other"


class ExperienceRange(str, Enum):
    ZERO_ONE = "0-1"
    ONE_THREE = "1-3"
    THREE_FIVE = "3-5"
    FIVE_PLUS = "5+"


class WorkRadius(str, Enum):
    LOCAL = "local"
    DISTRICT = "district"
    STATE = "state"
    ANYWHERE = "anywhere"


class InformalWorkType(str, Enum):
    STREET_VENDOR = "street_vendor"
    DOMESTIC_WORKER = "domestic_worker"
    DAILY_WAGE = "daily_wage"
    HOME_BASED = "home_based"
    AGRICULTURAL = "agricultural"
    OTHER = "other"


class IncomeRange(str, Enum):
    BELOW_5K = "below_5k"
    FROM_5K_10K = "5k_10k"
    FROM_10K_20K = "10k_20k"
    ABOVE_20K = "above_20k"


class DigitalLiteracy(str, Enum):
    NONE = "none"
    BASIC = "basic"
    APPS = "apps"
    COMFORTABLE = "comfortable"


class CompanySize(str, Enum):
    TINY = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "200+"


class NGOFocusSector(str, Enum):
    SKILLING = "skilling"
    EMPLOYMENT = "employment"
    WOMEN_EMPOWERMENT = "women_empowerment"
    YOUTH_DEVELOPMENT = "youth_development"
    DIGITAL_LITERACY = "digital_literacy"
    OTHER = "other"


class NGOBeneficiaryType(str, Enum):
    YOUTH = "youth"
    WOMEN = "women"
    BLUE_COLLAR = "blue_collar"
    INFORMAL = "informal"
    ALL = "all"


class GovtDept(str, Enum):
    LABOUR = "labour"
    SKILL_DEVELOPMENT = "skill_development"
    EDUCATION = "education"
    OTHER = "other"


class GovtAccessLevel(str, Enum):
    DISTRICT = "district"
    STATE = "state"
    NATIONAL = "national"


class JobLocationPreference(str, Enum):
    SAME_CITY = "same_city"
    STATE = "state"
    ANYWHERE = "anywhere"
