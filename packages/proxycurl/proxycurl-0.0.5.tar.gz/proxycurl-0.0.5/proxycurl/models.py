from typing import TypedDict, List, Dict, Tuple


class EmployeeCount(TypedDict):
    total_employee: int


class UrlResult(TypedDict):
    url: str


class Job(TypedDict):
    company: str
    company_url: str
    job_title: str
    job_url: str
    list_date: str
    location: str


class ProfileUrl(TypedDict):
    profile_url: str


class ExtractionEmailResult(TypedDict):
    email: str
    status: str


class RoleSearchResult(TypedDict):
    linkedin_profile_url: str


class PDLPhoneNumberResult(TypedDict):
    numbers: List[str]


class PDLEmailResult(TypedDict):
    emails: List[str]


class Investor(TypedDict):
    linkedin_profile_url: str
    name: str
    type: str


class Exit(TypedDict):
    linkedin_profile_url: str
    crunchbase_profile_url: str
    name: str


class SimilarCompany(TypedDict):
    name: str
    link: str
    industry: str
    location: str


class CompanyLocation(TypedDict):
    country: str
    city: str
    postal_code: str
    line_1: str
    is_hq: bool
    state: str


class LinkedinJob(TypedDict):
    linkedin_internal_id: str
    job_description: str
    apply_url: str
    title: str
    location: Dict
    company: Dict
    seniority_level: str
    industry: List[str]
    employment_type: str
    job_functions: List[str]
    total_applicants: int


class InferredSalary(TypedDict):
    min: float
    max: float


class PersonGroup(TypedDict):
    profile_pic_url: str
    name: str
    url: str


class SimilarProfile(TypedDict):
    name: str
    link: str
    summary: str
    location: str


class Activity(TypedDict):
    title: str
    link: str
    activity_status: str


class PeopleAlsoViewed(TypedDict):
    link: str
    name: str
    summary: str
    location: str


class Course(TypedDict):
    name: str
    number: str


class Date(TypedDict):
    day: int
    month: int
    year: int


class DisposableEmail(TypedDict):
    is_disposable_email: bool
    is_free_email: bool


class CreditBalance(TypedDict):
    credit_balance: int


class Experience(TypedDict):
    starts_at: Date
    ends_at: Date
    company: str
    company_linkedin_profile_url: str
    title: str
    description: str
    location: str
    logo_url: str


class Education(TypedDict):
    starts_at: Date
    ends_at: Date
    field_of_study: str
    degree_name: str
    school: str
    school_linkedin_profile_url: str
    description: str
    logo_url: str


class AccomplishmentOrg(TypedDict):
    starts_at: Date
    ends_at: Date
    org_name: str
    title: str
    description: str


class Publication(TypedDict):
    name: str
    publisher: str
    published_on: Date
    description: str
    url: str


class HonourAward(TypedDict):
    title: str
    issuer: str
    issued_on: Date
    description: str


class Patent(TypedDict):
    title: str
    issuer: str
    issued_on: Date
    description: str
    application_number: str
    patent_number: str
    url: str


class Project(TypedDict):
    starts_at: Date
    ends_at: Date
    title: str
    description: str
    url: str


class TestScore(TypedDict):
    description: str
    score: str
    name: str
    date_on: Date


class VolunteeringExperience(TypedDict):
    starts_at: Date
    ends_at: Date
    cause: str
    company: str
    company_linkedin_profile_url: str
    title: str
    description: str
    logo_url: str


class Certification(TypedDict):
    starts_at: Date
    ends_at: Date
    url: str
    name: str
    license_number: str
    display_source: str
    authority: str


class Article(TypedDict):
    title: str
    link: str
    published_date: Date
    author: str
    image_url: str


class PersonEndpointResponse(TypedDict):
    public_identifier: str
    profile_pic_url: str
    background_cover_image_url: str
    first_name: str
    last_name: str
    full_name: str
    occupation: str
    headline: str
    summary: str
    country: str
    country_full_name: str
    city: str
    state: str
    experiences: List[Experience]
    education: List[Education]
    languages: List[str]
    accomplishment_organisations: List[AccomplishmentOrg]
    accomplishment_publications: List[Publication]
    accomplishment_honors_awards: List[HonourAward]
    accomplishment_patents: List[Patent]
    accomplishment_courses: List[Course]
    accomplishment_projects: List[Project]
    accomplishment_test_scores: List[TestScore]
    volunteer_work: List[VolunteeringExperience]
    certifications: List[Certification]
    connections: int
    people_also_viewed: List[PeopleAlsoViewed]
    recommendations: List[str]
    activities: List[Activity]
    similarly_named_profiles: List[SimilarProfile]
    articles: List[Article]
    groups: List[PersonGroup]
    skills: List[str]
    inferred_salary: InferredSalary
    github: str
    facebook: str
    gender: str
    birth_date: Date
    industry: str
    interests: List[str]


class CompanyUpdate(TypedDict):
    article_link: str
    image: str
    posted_on: Date
    text: str
    total_likes: int


class LinkedinSchool(TypedDict):
    linkedin_internal_id: str
    description: str
    website: str
    industry: str
    company_size: Tuple[int, int]
    company_size_on_linkedin: int
    hq: CompanyLocation
    company_type: str
    founded_year: int
    specialities: List[str]
    locations: List[CompanyLocation]
    name: str
    tagline: str
    universal_name_id: str
    profile_pic_url: str
    background_cover_image_url: str
    search_id: str
    similar_companies: List[SimilarCompany]
    updates: List[CompanyUpdate]
    follower_count: int


class AcquiredCompany(TypedDict):
    linkedin_profile_url: str
    crunchbase_profile_url: str
    announced_date: Date
    price: int


class Acquisitor(TypedDict):
    linkedin_profile_url: str
    crunchbase_profile_url: str
    announced_date: Date
    price: int


class Acquisition(TypedDict):
    acquired: List[AcquiredCompany]
    acquired_by: Acquisitor


class CompanyDetails(TypedDict):
    ipo_status: str
    crunchbase_rank: int
    founding_date: Date
    operating_status: str
    company_type: str
    contact_email: str
    phone_number: str
    facebook_id: str
    twitter_id: str
    number_of_funding_rounds: int
    total_funding_amount: int
    stock_symbol: str
    ipo_date: Date
    number_of_lead_investors: int
    number_of_investors: int
    total_fund_raised: int
    number_of_investments: int
    number_of_lead_investments: int
    number_of_exits: int
    number_of_acquisitions: int


class Funding(TypedDict):
    funding_type: str
    money_raised: int
    announced_date: Date
    number_of_investor: int
    investor_list: List[Investor]


class LinkedinCompany(TypedDict):
    linkedin_internal_id: str
    description: str
    website: str
    industry: str
    company_size: Tuple[int, int]
    company_size_on_linkedin: int
    hq: CompanyLocation
    company_type: str
    founded_year: int
    specialities: List[str]
    locations: List[CompanyLocation]
    name: str
    tagline: str
    universal_name_id: str
    profile_pic_url: str
    background_cover_image_url: str
    search_id: str
    similar_companies: List[SimilarCompany]
    updates: List[CompanyUpdate]
    follower_count: int
    acquisitions: Acquisition
    exit_data: List[Exit]
    extra: CompanyDetails
    funding_data: List[Funding]
    categories: List[str]


class EmployeeList(TypedDict):
    employees: List[ProfileUrl]


class JobListPage(TypedDict):
    job: List[Job]
    next_page_no: int
    next_page_api_url: str
    previous_page_no: int
    previous_page_api_url: str
