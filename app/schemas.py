import strawberry 
from typing import List, Optional
from .resolvers import get_university_matches



# Input type mirroring form responses / student preferences
@strawberry.input
class StudentPreferenceInput:
    # email: str  # Keep if needed for other purposes, not directly for matching logic
    specialties: List[str]
    ownerships: List[str]
    states: List[str]
    regions: List[str]
    academic_importance: int = strawberry.field(description="Importance rating (1 - 5)")
    hostel_importance: int = strawberry.field(description="Importance rating (1 - 5)")
    social_life_importance: int = strawberry.field(description="Importance rating (1 - 5)")
    sports_importance: int = strawberry.field(description="Importance rating (1 - 5)")
    tuition_range: str = strawberry.field(description="e.g., '100,000 - 300,000 naira', 'Greater than 2,000,000 naira")
    cost_of_living_range: str = strawberry.field(description="e.g., '70,000 - 100,000 naira'")


# Output type for University details
@strawberry.type
class UniversityType:
    id: int
    name: str
    geopolitical_region: str
    state: str
    specialty: str
    ownership: str
    type: Optional[str]
    academic_rigor: Optional[int]
    sports_facilities: Optional[int]
    hostel_quality: Optional[list]
    social_life: Optional[int]
    tuition_display: Optional[str] = strawberry.field(alias="tuition_category_str")  # Use alias if needed
    cost_of_living_display: Optional[str] = strawberry.field(alias="cost_category_str")  # Use alias if needed
    source_url_1: Optional[str]
    source_url_2: Optional[str]


# Output type for a matched university including its score
@strawberry.type
class MatchResult:
    university: UniversityType
    score: float

# Define the main Query type 
@strawberry.type 
class Query: 

    @strawberry.field
    async def match_universities(self, preferences: StudentPreferenceInput) -> List[MatchResult]:
        matches  = await get_university_matches(preferences)
        return matches
    
    # --- Future Extensibility Example ---
    # @strawberry.field
    # async def rank_universities_by_state(self, state: str) -> List[UniversityType]:
    #     # Implement logic to fetch and return universities ordered by some criteria
    #     # possibly calling a function in crud.py
    #     pass

    # @strawberry.field
    # async def rank_universities_by_academic(self) -> List[UniversityType]:
    #     # Implement logic...
    #     pass