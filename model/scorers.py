# Function to compute the skill overlap between required skills and worker skills
def compute_skill_overlap(required_skills: list[str], worker_skills: list[str]) -> dict:
    if not required_skills:
        return {
            "skill_overlap_score": 1.0, # If there are no required skills - everyone matches perfectly
            "missing_skills": [],
            "match_ratio": "0/0"
        }
    
    required_normalized = [skill.lower().strip() for skill in required_skills]
    worker_normalized = [skill.lower().strip() for skill in worker_skills]

    matched_skills = [skill for skill in required_skills if skill.lower().strip() in worker_normalized]
    missing_skills = [skill for skill in required_skills if skill.lower().strip() not in worker_normalized]

    score = len(matched_skills) / len(required_skills)

    return {
        "skill_overlap_score": round(score, 4),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_ratio": f"{len(matched_skills)}/{len(required_skills)}"
    }

# Penalize workers based on their current workload. 
# The more active tasks they have, the lower their score.
def compute_workload_score(active_tasks: int, max_tasks: int = 5) -> dict:
    if max_tasks <= 0:
        return {
            "workload_score": 0.0,
            "active_tasks": active_tasks,
        }
    
    score = max(0.0, 1.0 - (active_tasks / max_tasks))

    return {
        "workload_score": round(score, 4),
        "active_tasks": active_tasks,
    }