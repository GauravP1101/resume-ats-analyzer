import re

COMMON_SKILLS = [
    "Python", "Java", "SQL", "AWS", "React", "Node.js", "Docker", "Kubernetes", "JavaScript",
    "Spring Boot", "NLP", "Machine Learning", "Deep Learning", "API", "Cloud", "Git", "REST",
    "FastAPI", "Flutter", "BERT", "RoBERTa"
]
ALIASES = {
    "nodejs": "Node.js", "node": "Node.js", "ml": "Machine Learning",
    "aws": "AWS", "bert": "BERT", "roberta": "RoBERTa"
}

def normalize_skill(skill):
    s = skill.strip().lower()
    return ALIASES.get(s, s.title())

def extract_skills(text):
    found = set()
    for skill in COMMON_SKILLS:
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text, re.IGNORECASE):
            found.add(skill)
    # Block extraction for Skills section
    block = re.search(r'(Skills:|Technical Skills:)(.*?)(\n|$)', text, re.IGNORECASE)
    if block:
        raw = block.group(2)
        for skill in raw.split(','):
            nskill = normalize_skill(skill)
            if nskill in COMMON_SKILLS:
                found.add(nskill)
    return sorted(found)

def compare_skills(resume_skills, jd_skills):
    return sorted(set(jd_skills) - set(resume_skills))
