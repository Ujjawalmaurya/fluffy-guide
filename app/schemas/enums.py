from enum import Enum


class CaseInsensitiveEnum(str, Enum):
    """Base class for case-insensitive string enums with normalization."""
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            # Normalize: lowercase and remove separators
            norm_value = value.lower().replace("_", "").replace("-", "").replace(" ", "")
            
            # Check for aliases if defined in the subclass
            get_aliases = getattr(cls, "_get_aliases", None)
            aliases = get_aliases() if callable(get_aliases) else {}
            if isinstance(aliases, dict) and norm_value in aliases:
                norm_value = aliases[norm_value].lower().replace("_", "").replace("-", "").replace(" ", "")

            for member in cls:
                # Also normalize the member's value for comparison
                member_norm = member.value.lower().replace("_", "").replace("-", "").replace(" ", "")
                if member_norm == norm_value:
                    return member
        return None


class UserRole(CaseInsensitiveEnum):
    """System-level user roles/categories."""
    USER = "user"
    STUDENT = "individual_youth"
    BLUE_COLLAR = "individual_bluecollar"
    INFORMAL = "individual_informal"
    NGO = "org_ngo"
    EMPLOYER = "org_employer"
    GOVT_OFFICER = "org_govt"


class Gender(CaseInsensitiveEnum):
    """Gender identification."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class CareerStage(CaseInsensitiveEnum):
    STUDENT = "student"
    FRESHER = "fresher"
    EARLY = "early"
    MID = "mid"
    SENIOR = "senior"
    BLUE_COLLAR = "blue_collar"
    INFORMAL = "informal"


class EducationLevel(CaseInsensitiveEnum):
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


class EducationStream(CaseInsensitiveEnum):
    SCIENCE = "science"
    COMMERCE = "commerce"
    ARTS = "arts"
    VOCATIONAL = "vocational"
    OTHER = "other"


class SkillLevel(CaseInsensitiveEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class JobType(CaseInsensitiveEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    GIG = "gig"
    APPRENTICESHIP = "apprenticeship"
    INTERNSHIP = "internship"


class WorkMode(CaseInsensitiveEnum):
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class SkillCategory(CaseInsensitiveEnum):
    TECHNICAL = "technical"
    SOFT = "soft"
    VOCATIONAL = "vocational"
    DIGITAL = "digital"
    LANGUAGE = "language"
    DOMAIN = "domain"


class TrainingStatus(CaseInsensitiveEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"


class PlacementStatus(CaseInsensitiveEnum):
    PLACED = "placed"
    NOT_PLACED = "not_placed"
    IN_PROCESS = "in_process"
    SELF_EMPLOYED = "self_employed"


class AssessmentType(CaseInsensitiveEnum):
    QUIZ = "quiz"
    MOCK_INTERVIEW = "mock_interview"
    CODING = "coding"
    PRACTICAL = "practical"
    LANGUAGE = "language"


class Language(CaseInsensitiveEnum):
    HINDI = "hindi"
    ENGLISH = "english"
    BENGALI = "bengali"
    TELUGU = "telugu"
    MARATHI = "marathi"
    TAMIL = "tamil"
    URDU = "urdu"
    GUJARATI = "gujarati"
    KANNADA = "kannada"
    ODIA = "odia"
    PUNJABI = "punjabi"
    MALAYALAM = "malayalam"
    HINGLISH = "hinglish"

    @classmethod
    def _get_aliases(cls):
        return {
            "en": "english",
            "hi": "hindi",
            "mr": "marathi",
            "bn": "bengali",
            "te": "telugu",
            "ta": "tamil",
            "gu": "gujarati",
            "kn": "kannada",
            "ml": "malayalam"
        }


class Region(CaseInsensitiveEnum):
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


class TradeSkill(CaseInsensitiveEnum):
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"
    CARPENTER = "carpenter"
    WELDER = "welder"
    MASON = "mason"
    PAINTER = "painter"
    MECHANIC = "mechanic"
    OTHER = "other"


class ExperienceRange(CaseInsensitiveEnum):
    ZERO_ONE = "0-1"
    ONE_THREE = "1-3"
    THREE_FIVE = "3-5"
    FIVE_PLUS = "5+"


class WorkRadius(CaseInsensitiveEnum):
    LOCAL = "local"
    DISTRICT = "district"
    STATE = "state"
    ANYWHERE = "anywhere"


class InformalWorkType(CaseInsensitiveEnum):
    STREET_VENDOR = "street_vendor"
    DOMESTIC_WORKER = "domestic_worker"
    DAILY_WAGE = "daily_wage"
    HOME_BASED = "home_based"
    AGRICULTURAL = "agricultural"
    OTHER = "other"


class IncomeRange(CaseInsensitiveEnum):
    BELOW_5K = "below_5k"
    FROM_5K_10K = "5k_10k"
    FROM_10K_20K = "10k_20k"
    ABOVE_20K = "above_20k"


class DigitalLiteracy(CaseInsensitiveEnum):
    NONE = "none"
    BASIC = "basic"
    APPS = "apps"
    COMFORTABLE = "comfortable"


class CompanySize(CaseInsensitiveEnum):
    TINY = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "200+"


class NGOFocusSector(CaseInsensitiveEnum):
    SKILLING = "skilling"
    EMPLOYMENT = "employment"
    WOMEN_EMPOWERMENT = "women_empowerment"
    YOUTH_DEVELOPMENT = "youth_development"
    DIGITAL_LITERACY = "digital_literacy"
    OTHER = "other"


class NGOBeneficiaryType(CaseInsensitiveEnum):
    YOUTH = "youth"
    WOMEN = "women"
    BLUE_COLLAR = "blue_collar"
    INFORMAL = "informal"
    ALL = "all"


class GovtDept(CaseInsensitiveEnum):
    LABOUR = "labour"
    SKILL_DEVELOPMENT = "skill_development"
    EDUCATION = "education"
    OTHER = "other"


class GovtAccessLevel(CaseInsensitiveEnum):
    DISTRICT = "district"
    STATE = "state"
    NATIONAL = "national"


class JobLocationPreference(CaseInsensitiveEnum):
    SAME_CITY = "same_city"
    STATE = "state"
    ANYWHERE = "anywhere"
