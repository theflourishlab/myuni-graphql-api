import math
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from .schemas import StudentPreferenceInput, MatchResult, UniversityType
from .models import University
from .utils import parse_db_range_string, ranges_overlap, calculate_tuition_difference
from .database import SessionLocal

from .crud import get_all_universities

async def get_university_matches(preferences: StudentPreferenceInput) -> List[MatchResult]:
    """
    Main resolver logic to find and score university matches based on student preferences.
    """
    db: Session = SessionLocal()
    try:
        student_tuition_min, student_tuition_max = parse_db_range_string(preferences.tuition_range)
        student_cost_min, student_cost_max = parse_db_range_string(preferences.cost_of_living_range)

        pref_specialties = set(s.strip() for s in preferences.specialties if s.strip())
        pref_ownerships = set(o.strip() for o in preferences.ownerships if o.strip()) 
        pref_states = set(st.strip() for st in preferences.states if st.strip())
        pref_regions = set(r.strip() for r in preferences.regions if r.strip())

        all_unis = get_all_universities(db)

        potential_matches: List[Dict] = []

        # Primary Filtering & Initial Scoring
        for uni in all_unis:
            # --- PRIMARY FILTERING (Mulit-select) ---
            specialty_match = uni.specialty in pref_specialties
            ownership_match = uni.ownership in pref_ownerships
            location_match = (uni.state in pref_states) or (uni.geopolitical_region in pref_regions)

            if specialty_match and ownership_match and location_match:
                    # --- SECONDARY FILTERING (Tuition) and SCORE CALCULATION ---
                    tuition_match = ranges_overlap(student_tuition_min, student_tuition_max, uni.tuition_min, uni.tuition_max)

                    if tuition_match:
                        # Calculate positive score
                        academic_score = preferences.academic_importance * (uni.academic_rigor or 0)
                        hostel_score = preferences.hostel_importance * (uni.hostel_quality or 0)
                        sports_score = preferences.sports_importance * (uni.sports_facilities or 0)
                        social_life_score = preferences.social_life_importance * (uni.social_life or 0)

                        cost_match = ranges_overlap(student_cost_min, student_cost_max, uni.cost_of_living_min, uni.cost_of_living_max)
                        cost_bonus = 5 if cost_match else 0

                        total_score = float(academic_score + hostel_score + sports_score + social_life_score + cost_bonus)

                        potential_matches.append({"uni": uni, "score": total_score})

                # Fallback Logic (If no matches found with tuition overlap)
            if not potential_matches:
                print("No matches found with tuition overlap, entering fallback")
                for uni in all_unis:
                    # Apply the primary filter again
                    specialty_match = uni.specialty in pref_specialties
                    ownership_match = uni.ownership in pref_ownerships
                    location_match = (uni.state in pref_states) or (uni.geopolitical_region in pref_regions)

                    if specialty_match and ownership_match and location_match:
                        # Calculate tuition difference (lower is better)
                        tuition_diff = calculate_tuition_difference(student_tuition_min, student_tuition_max, uni.tuition_min, uni.tuition_max)
                        # Use negative difference for sorting (higher negative = closer)
                        potential_matches.append({"uni": uni, "score": -tuition_diff})


            potential_matches.sort(key=lambda x: x["score"], reverse=True)
            top_matches_data = potential_matches[:10]

            # Format results into Graphql MatchResult type
            results: List
        
            # Format results into Graphql MatchResult type
            results: List[MatchResult] = []
            for match_data in top_matches_data:
                uni_model = match_data["uni"]
                score = match_data["score"]

                # Create the UniversityType instance for the result
                uni_type_instance = UniversityType(
                id=uni_model.id,
                name=uni_model.name,
                geopolitical_region=uni_model.geopolitical_region,
                state=uni_model.state,
                specialty=uni_model.specialty,
                ownership=uni_model.ownership,
                type=uni_model.type,
                academic_rigor=uni_model.academic_rigor,
                sports_facilities=uni_model.sports_facilities,
                hostel_quality=uni_model.hostel_quality,
                social_life=uni_model.social_life,
                # Use the stored string representations for display
                tuition_display=uni_model.tuition_category_str,
                cost_of_living_display=uni_model.cost_category_str,
                source_url_1=uni_model.source_url_1,
                source_url_2=uni_model.source_url_2
                )

                results.append(MatchResult(university=uni_type_instance), score=score)

                return results
    finally:
        db.close()