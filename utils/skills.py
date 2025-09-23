# utils/skills.py
# Robust, ATS-style skill extraction & matching (exact + fuzzy + aliases)
from __future__ import annotations
import re
import difflib
from typing import Dict, List, Set, Tuple

# ----------------------------- Taxonomy ---------------------------------------
TAXONOMY: Dict[str, Set[str]] = {
    # Languages
    "Python": {"py"},
    "Java": set(),
    "JavaScript": {"js", "vanilla js"},
    "TypeScript": {"ts"},
    "SQL": {"postgres sql", "t-sql", "pl/sql", "structured query language"},
    "Bash": {"shell", "sh"},
    "C": set(),
    "C++": {"cpp"},

    # Frontend
    "React.js": {"react", "reactjs"},
    "React Native": {"react-native"},
    "Next.js": {"nextjs"},
    "Redux": set(),
    "AngularJS": {"angular", "angular.js"},
    "HTML5": {"html"},
    "CSS3": {"css"},
    "Bootstrap": set(),
    "Figma": set(),
    "D3.js": {"d3"},

    # Backend
    "Node.js": {"node", "nodejs"},
    "Express.js": {"express", "expressjs"},
    "Spring Boot": {"springboot", "spring-boot", "spring"},
    "FastAPI": set(),
    "Flask": set(),
    "REST APIs": {"rest", "restful api", "rest api"},
    "Microservices Architecture": {"microservices", "service oriented", "soa"},

    # Databases
    "PostgreSQL": {"postgres", "psql"},
    "MySQL": set(),
    "MongoDB": {"mongo"},
    "SQLite": set(),
    "Redis": set(),
    "Oracle": {"oracle db", "oracle database"},
    "Redshift": set(),
    "BigQuery": {"google bigquery", "gcp bigquery"},
    "Cassandra": set(),
    "DynamoDB": set(),
    "Vector Databases": {"vector db", "vectorstore"},
    "FAISS": set(),
    "Pinecone": set(),
    "Weaviate": set(),

    # Cloud & DevOps
    "AWS": {"amazon web services"},
    "Azure": set(),
    "Google Cloud Platform": {"gcp", "google cloud"},
    "AWS EC2": {"ec2"},
    "AWS S3": {"s3"},
    "AWS RDS": {"rds"},
    "AWS Lambda": {"lambda"},
    "IAM": {"aws iam"},
    "CloudWatch": {"amazon cloudwatch"},
    "Docker": set(),
    "Kubernetes": {"k8s"},
    "EKS": set(),
    "ECS": set(),
    "Terraform": {"iac terraform"},
    "Jenkins": set(),
    "Git": set(),
    "GitHub Actions": {"gha", "github actions ci"},
    "Ansible": set(),
    "CI/CD": {"cicd", "ci cd"},
    "VPC": set(),

    # Data / ML / MLOps
    "Scikit-learn": {"sklearn"},
    "PyTorch": {"pytorch lightning", "torch"},
    "TensorFlow": {"tf"},
    "MLflow": set(),
    "TorchServe": set(),
    "TensorFlow Serving": set(),
    "Feature Stores": {"feature store", "feast"},
    "Data Modeling": {"data model"},
    "ETL": {"elt", "extract transform load"},
    "Data Warehousing": {"data warehouse", "dw"},
    "Airflow": {"apache airflow"},
    "Spark": {"apache spark", "pyspark"},
    "Kafka": {"apache kafka"},
    "Data Quality": {"dq"},
    "Data Governance": set(),
    "Streaming": {"stream processing", "real time streaming", "realtime"},
    "Kinesis": set(),
    "PubSub": {"pub/sub", "google pubsub"},
    "RabbitMQ": set(),

    # NLP / LLM
    "Natural Language Processing": {"nlp"},
    "Large Language Models": {"llm", "foundation models"},
    "Hugging Face Transformers": {"transformers", "huggingface"},
    "OpenAI APIs": {"openai", "gpt api"},
    "LangChain": set(),
    "RAG Pipelines": {"rag"},
    "Prompt Engineering": {"prompting"},
    "BERT": set(),
    "RoBERTa": set(),
    "GPT": {"gpt-4", "gpt4", "gpt-3.5"},

    # Monitoring / Analytics
    "Amazon CloudWatch": set(),
    "Prometheus": set(),
    "Grafana": set(),
    "ELK Stack": {"elk", "elasticsearch logstash kibana"},
    "Elasticsearch": set(),
    "Logstash": set(),
    "Kibana": set(),
    "Tableau": set(),
    "Power BI": {"powerbi"},

    # Testing / Practices
    "Unit Testing": {"unit tests"},
    "Integration Testing": {"integration tests"},
    "Debugging": set(),
    "TDD": {"test driven development"},
    "Agile/Scrum": {"agile", "scrum"},
    "Jest": set(),
    "Cypress": set(),
    "JUnit": set(),
    "Mockito": set(),
    "A/B Testing": {"ab testing", "a b testing"},
    "Experiment Tracking": {"exp tracking"},
}

# Softer category weights (de-tuned)
CATEGORY_WEIGHTS: Dict[str, float] = {
    "Languages": 0.85,
    "Frontend": 0.70,
    "Backend": 0.85,
    "Databases": 0.80,
    "Cloud & DevOps": 0.85,
    "Data / ML / MLOps": 0.90,
    "NLP / LLM": 0.75,
    "Monitoring / Analytics": 0.45,
    "Testing / Practices": 0.50,
}

# Per-skill priors: ubiquitous skills have smaller influence
SKILL_PRIOR: Dict[str, float] = {
    # Dev basics
    "Git": 0.35,
    "Agile/Scrum": 0.35,
    "CI/CD": 0.40,
    "REST APIs": 0.45,
    "Debugging": 0.40,
    "Unit Testing": 0.40,
    "Integration Testing": 0.40,

    # Cloud basics & logging
    "AWS": 0.60,
    "Azure": 0.50,
    "Google Cloud Platform": 0.50,
    "Amazon CloudWatch": 0.35,
    "CloudWatch": 0.35,
    "Jenkins": 0.45,
    "GitHub Actions": 0.45,
    "Docker": 0.55,
    "Kubernetes": 0.55,

    # Generic data buzzwords
    "Data Modeling": 0.50,
    "ETL": 0.50,
    "Data Warehousing": 0.50,
    "Data Quality": 0.45,

    # Analytics platforms commonly mentioned
    "Tableau": 0.45,
    "Power BI": 0.45,
}

# Per-category caps: limit JD influence
CAT_CAP: Dict[str, int] = {
    "Languages": 4,
    "Frontend": 4,
    "Backend": 4,
    "Databases": 4,
    "Cloud & DevOps": 4,
    "Data / ML / MLOps": 5,
    "NLP / LLM": 3,
    "Monitoring / Analytics": 3,
    "Testing / Practices": 3,
}

# Canonical maps and patterns
CANONICAL: Set[str] = set(TAXONOMY.keys())
ALIAS2CANON: Dict[str, str] = {}
for canon, aliases in TAXONOMY.items():
    ALIAS2CANON[canon.lower()] = canon
    for a in aliases:
        ALIAS2CANON[a.lower()] = canon

# exact word/alias patterns (word-ish boundaries that allow +/#/.)
EXACT_PATTERNS: Dict[str, re.Pattern] = {
    canon: re.compile(rf"(?<![#\w]){re.escape(canon)}(?![-\w])", re.IGNORECASE) for canon in CANONICAL
}
for alias, canon in ALIAS2CANON.items():
    if alias == canon.lower():
        continue
    EXACT_PATTERNS[f"{canon}__{alias}"] = re.compile(
        rf"(?<![#\w]){re.escape(alias)}(?![-\w])", re.IGNORECASE
    )

# ----------------------------- Normalization ----------------------------------
def _clean_text(s: str) -> str:
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[•·●▪►▶]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def _normalize_token(s: str) -> str:
    s = s.lower().strip()
    s = s.replace("/", " ").replace("-", " ")
    s = re.sub(r"[^\w\s.+#]", "", s)
    return s

def _ngrams(words: List[str], n: int) -> List[str]:
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]

# ----------------------------- Extraction -------------------------------------
def extract_skills(text: str) -> List[str]:
    if not text:
        return []
    text_clean = _clean_text(text)
    found: Set[str] = set()

    # 1) exact hits (canon + aliases)
    for key, pat in EXACT_PATTERNS.items():
        canon = key.split("__", 1)[0]
        if pat.search(text_clean):
            found.add(canon)

    # 2) fuzzy windows (for extraction only)
    tokens = [_normalize_token(t) for t in re.findall(r"[A-Za-z0-9+.#]+", text_clean)]
    grams = set(tokens)
    for n in (2, 3):
        grams.update(_ngrams(tokens, n))

    def _fuzzy_hit(window: str, target: str) -> bool:
        if not window or not target:
            return False
        t = target.lower()
        w = window.lower()
        if t in w:
            return True
        ratio = difflib.SequenceMatcher(a=w, b=t).ratio()
        if len(t) >= 10:
            return ratio >= 0.86
        elif len(t) >= 6:
            return ratio >= 0.88
        else:
            return ratio >= 0.92

    for canon in CANONICAL:
        targets = {canon.lower(), *[a.lower() for a in TAXONOMY[canon]]}
        if canon in found:
            continue
        if any(_fuzzy_hit(g, t) for g in grams for t in targets):
            found.add(canon)

    return sorted(found)

# ----------------------------- JD comparison ----------------------------------
def compare_skills(resume_skills: List[str], jd_skills: List[str]) -> List[str]:
    norm_resume = {ALIAS2CANON.get(s.lower(), s) for s in resume_skills}
    norm_jd     = {ALIAS2CANON.get(s.lower(), s) for s in jd_skills}
    return sorted(norm_jd - norm_resume)

# ----------------------------- Category helper --------------------------------
def _category_of(canon: str) -> str:
    cat_map = [
        ("Languages", {"Python","Java","JavaScript","TypeScript","SQL","Bash","C","C++"}),
        ("Frontend", {"React.js","React Native","Next.js","Redux","AngularJS","HTML5","CSS3","Bootstrap","Figma","D3.js"}),
        ("Backend", {"Node.js","Express.js","Spring Boot","FastAPI","Flask","REST APIs","Microservices Architecture"}),
        ("Databases", {"PostgreSQL","MySQL","MongoDB","SQLite","Redis","Oracle","Redshift","BigQuery","Cassandra","DynamoDB","Vector Databases","FAISS","Pinecone","Weaviate"}),
        ("Cloud & DevOps", {"AWS","Azure","Google Cloud Platform","AWS EC2","AWS S3","AWS RDS","AWS Lambda","IAM","CloudWatch","Docker","Kubernetes","EKS","ECS","Terraform","Jenkins","Git","GitHub Actions","Ansible","CI/CD","VPC"}),
        ("Data / ML / MLOps", {"Scikit-learn","PyTorch","TensorFlow","MLflow","TorchServe","TensorFlow Serving","Feature Stores","Data Modeling","ETL","Data Warehousing","Airflow","Spark","Kafka","Data Quality","Data Governance","Streaming","Kinesis","PubSub","RabbitMQ"}),
        ("NLP / LLM", {"Natural Language Processing","Large Language Models","Hugging Face Transformers","OpenAI APIs","LangChain","RAG Pipelines","Prompt Engineering","BERT","RoBERTa","GPT"}),
        ("Monitoring / Analytics", {"Amazon CloudWatch","Prometheus","Grafana","ELK Stack","Elasticsearch","Logstash","Kibana","Tableau","Power BI"}),
        ("Testing / Practices", {"Unit Testing","Integration Testing","Debugging","TDD","Agile/Scrum","Jest","Cypress","JUnit","Mockito","A/B Testing","Experiment Tracking"}),
    ]
    for cat, items in cat_map:
        if canon in items:
            return cat
    return "Other"

# ----------------------------- Rich analyzer ----------------------------------
def extract_jd_skills(text: str) -> List[str]:
    """
    Extract JD skills conservatively, union base + section hits,
    then cap per category to avoid overfitting to long JDs.
    """
    if not text:
        return []
    text_clean = _clean_text(text)

    base = set(extract_skills(text_clean))

    sections = re.findall(
        r"(Requirements|Qualifications|What you’ll do|What we look for|Preferred|Must have)[:\s]+(.+?)(?=\n[A-Z][^\n]{0,40}:|\Z)",
        text_clean, flags=re.IGNORECASE | re.DOTALL
    )
    sec_skills: Set[str] = set()
    for _, sec in sections:
        sec_skills.update(extract_skills(sec))

    combined_sorted = sorted(base | sec_skills)

    # Apply per-category caps
    per_cat: Dict[str, int] = {}
    trimmed: List[str] = []
    for s in combined_sorted:
        c = _category_of(s)
        cap = CAT_CAP.get(c, 4)
        used = per_cat.get(c, 0)
        if used < cap:
            trimmed.append(s)
            per_cat[c] = used + 1

    return trimmed

def coverage_score(resume_skills: List[str], jd_skills: List[str]) -> Tuple[float, Dict[str, List[str]]]:
    resume_set = {ALIAS2CANON.get(s.lower(), s) for s in resume_skills}
    jd_set     = {ALIAS2CANON.get(s.lower(), s) for s in jd_skills}

    detail: Dict[str, List[str]] = {"matched": [], "missing": [], "extra": []}

    # Build per-category lists to apply caps on the JD side
    per_cat_skills: Dict[str, List[str]] = {}
    for s in sorted(jd_set):
        cat = _category_of(s)
        per_cat_skills.setdefault(cat, []).append(s)

    # Apply category caps
    jd_trimmed: Set[str] = set()
    for cat, skills in per_cat_skills.items():
        cap = CAT_CAP.get(cat, 4)
        jd_trimmed.update(skills[:cap])

    # Fill details
    for s in sorted(jd_trimmed):
        if s in resume_set:
            detail["matched"].append(s)
        else:
            detail["missing"].append(s)
    for s in sorted(resume_set - jd_trimmed):
        detail["extra"].append(s)

    # Weighted scoring: category weights * per-skill prior
    total_weight = 0.0
    got_weight   = 0.0
    for s in jd_trimmed:
        cat_w = CATEGORY_WEIGHTS.get(_category_of(s), 0.8)
        skill_w = SKILL_PRIOR.get(s, 1.0)
        w = cat_w * skill_w
        total_weight += w
        if s in resume_set:
            got_weight += w

    score = 0.0 if total_weight == 0 else round(100.0 * got_weight / total_weight, 2)

    for k in detail:
        detail[k] = sorted(detail[k])
    return score, detail

def analyze_skills(resume_text: str, jd_text: str) -> Dict[str, object]:
    rs = extract_skills(resume_text)
    js = extract_jd_skills(jd_text)
    score, detail = coverage_score(rs, js)
    return {
        "resume_skills": sorted(rs),
        "jd_skills": sorted(js),
        "matched": detail["matched"],
        "missing": detail["missing"],
        "extra": detail["extra"],
        "coverage_score": score,
    }

# ========================== NEW: highlighting helpers =========================
def _html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def find_skill_mentions(text: str) -> List[Dict[str, object]]:
    """
    Return spans of exact/alias skill mentions in `text`.
    Each item: {"canon": str, "alias": str, "start": int, "end": int}
    """
    mentions: List[Dict[str, object]] = []
    if not text:
        return mentions
    for key, pat in EXACT_PATTERNS.items():
        canon = key.split("__", 1)[0]
        alias = key.split("__", 1)[1] if "__" in key else canon
        for m in pat.finditer(text):
            mentions.append({"canon": canon, "alias": alias, "start": m.start(), "end": m.end()})
    # sort, dedupe overlaps by preferring longer spans (more specific)
    mentions.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))
    non_overlap: List[Dict[str, object]] = []
    last_end = -1
    for m in mentions:
        if m["start"] >= last_end:
            non_overlap.append(m)
            last_end = m["end"]
    return non_overlap

def highlight_text_with_skills(
    text: str,
    skills_to_highlight: List[str] | Set[str] | None = None,
    mark_class: str = "skill-mark",
    color: str = "#fef3c7",   # amber-100
    border: str = "#f59e0b"   # amber-500
) -> Tuple[str, List[Dict[str, object]]]:
    """
    Return (html, mentions). Wrap matched skills in <mark> with a soft background.
    If `skills_to_highlight` is provided, only those canonicals are highlighted.
    """
    if not text:
        return "", []
    mentions = find_skill_mentions(text)
    if skills_to_highlight:
        canon_set = {ALIAS2CANON.get(s.lower(), s) for s in skills_to_highlight}
        mentions = [m for m in mentions if m["canon"] in canon_set]

    out = []
    i = 0
    for m in mentions:
        if i < m["start"]:
            out.append(_html_escape(text[i:m["start"]]))
        frag = _html_escape(text[m["start"]:m["end"]])
        out.append(
            f"<mark class='{mark_class}' "
            f"style='background:{color}; color:inherit; border:1px solid {border}; "
            f"border-radius:4px; padding:0 2px;'"
            f" title='{_html_escape(m['canon'])}'>"
            f"{frag}</mark>"
        )
        i = m["end"]
    out.append(_html_escape(text[i:]))
    return "".join(out), mentions

def highlight_resume_and_jd(resume_text: str, jd_text: str) -> Dict[str, object]:
    """
    Compute matched/missing skills and produce highlighted HTML for both resume and JD.
    """
    rs = extract_skills(resume_text)
    js = extract_jd_skills(jd_text)
    matched = sorted(set(rs) & set(js))
    missing = sorted(set(js) - set(rs))

    resume_html, resume_mentions = highlight_text_with_skills(resume_text, matched)
    jd_html, jd_mentions         = highlight_text_with_skills(jd_text, matched)

    return {
        "matched": matched,
        "missing": missing,
        "resume_html": resume_html,
        "jd_html": jd_html,
        "resume_mentions": resume_mentions,
        "jd_mentions": jd_mentions,
    }
