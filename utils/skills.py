# utils/skills.py
# Robust, ATS-style skill extraction & matching (exact + fuzzy + aliases)
from __future__ import annotations
import re
import difflib
from typing import Dict, List, Set, Tuple

# ----------------------------- Taxonomy ---------------------------------------
# Canonical -> set(aliases/variants); add freely as you see patterns in JDs.
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

# Optional category weights (tweak as you like)
CATEGORY_WEIGHTS: Dict[str, float] = {
    "Languages": 1.0,
    "Frontend": 0.8,
    "Backend": 1.0,
    "Databases": 0.9,
    "Cloud & DevOps": 1.1,
    "Data / ML / MLOps": 1.1,
    "NLP / LLM": 1.0,
    "Monitoring / Analytics": 0.6,
    "Testing / Practices": 0.7,
}

# Build canonical sets and a flat alias→canonical map
CANONICAL: Set[str] = set(TAXONOMY.keys())
ALIAS2CANON: Dict[str, str] = {}
for canon, aliases in TAXONOMY.items():
    ALIAS2CANON[canon.lower()] = canon
    for a in aliases:
        ALIAS2CANON[a.lower()] = canon

# Precompile regex for exact word-boundary matches
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
    s = s.replace("\u00a0", " ")  # non-breaking space
    s = re.sub(r"[•·●▪►▶]+", " ", s)  # bullets
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def _normalize_token(s: str) -> str:
    s = s.lower().strip()
    s = s.replace("/", " ").replace("-", " ")
    s = re.sub(r"[^\w\s.+#]", "", s)  # keep word chars and . + #
    return s

def _ngrams(words: List[str], n: int) -> List[str]:
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]

# ----------------------------- Extraction -------------------------------------
def extract_skills(text: str) -> List[str]:
    """
    Backwards-compatible API: returns list of canonical skills found in `text`.
    Uses exact match first; then fuzzy on 1–3 gram windows.
    """
    if not text:
        return []

    text_clean = _clean_text(text)
    found: Set[str] = set()

    # 1) Exact matches (canonical + aliases)
    for key, pat in EXACT_PATTERNS.items():
        canon = key.split("__", 1)[0]  # strip alias key
        if pat.search(text_clean):
            found.add(canon)

    # 2) Fuzzy matches on n-grams to catch spelling/format variants
    # Build candidate windows
    tokens = [_normalize_token(t) for t in re.findall(r"[A-Za-z0-9+.#]+", text_clean)]
    grams = set(tokens)
    for n in (2, 3):
        grams.update(_ngrams(tokens, n))

    def _fuzzy_hit(window: str, target: str) -> bool:
        if not window or not target:
            return False
        # Tighten threshold for short targets to avoid false positives
        t = target.lower()
        w = window.lower()
        # quick contain check
        if t in w:
            return True
        ratio = difflib.SequenceMatcher(a=w, b=t).ratio()
        if len(t) >= 10:
            return ratio >= 0.86
        elif len(t) >= 6:
            return ratio >= 0.88
        else:
            return ratio >= 0.92

    # Try fuzzy against aliases + canonicals
    for canon in CANONICAL:
        targets = {canon.lower(), *[a.lower() for a in TAXONOMY[canon]]}
        if canon in found:
            continue
        # speed: accept if any window is close to any target
        hit = any(_fuzzy_hit(g, t) for g in grams for t in targets)
        if hit:
            found.add(canon)

    return sorted(found)

# ----------------------------- JD comparison ----------------------------------
def compare_skills(resume_skills: List[str], jd_skills: List[str]) -> List[str]:
    """Backwards-compatible: returns list of missing JD skills."""
    norm_resume = {ALIAS2CANON.get(s.lower(), s) for s in resume_skills}
    norm_jd     = {ALIAS2CANON.get(s.lower(), s) for s in jd_skills}
    return sorted(norm_jd - norm_resume)

# ----------------------------- Rich analyzer ----------------------------------
def extract_jd_skills(text: str) -> List[str]:
    """
    Same as extract_skills but with extra JD-specific hints:
    we look into sections labeled 'Requirements', 'Qualifications', etc.
    """
    if not text:
        return []
    text_clean = _clean_text(text)
    main = extract_skills(text_clean)

    # section boost
    sections = re.findall(
        r"(Requirements|Qualifications|What you’ll do|What we look for|Preferred|Must have)[:\s]+(.+?)(?=\n[A-Z][^\n]{0,40}:|\Z)",
        text_clean, flags=re.IGNORECASE | re.DOTALL
    )
    boosted: Set[str] = set(main)
    for _, sec in sections:
        boosted.update(extract_skills(sec))
    return sorted(boosted)

def coverage_score(resume_skills: List[str], jd_skills: List[str]) -> Tuple[float, Dict[str, List[str]]]:
    """
    Weighted coverage score in [0,100] plus detail breakdown.
    """
    # Map each skill to a coarse category (best-effort; fallback to 'Other')
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

    resume_set = {ALIAS2CANON.get(s.lower(), s) for s in resume_skills}
    jd_set     = {ALIAS2CANON.get(s.lower(), s) for s in jd_skills}

    detail: Dict[str, List[str]] = {"matched": [], "missing": [], "extra": []}
    # per-category tallies
    cat_req: Dict[str, int] = {}
    cat_hit: Dict[str, int] = {}

    for s in jd_set:
        cat = _category_of(s)
        cat_req[cat] = cat_req.get(cat, 0) + 1
        if s in resume_set:
            detail["matched"].append(s)
            cat_hit[cat] = cat_hit.get(cat, 0) + 1
        else:
            detail["missing"].append(s)

    for s in resume_set - jd_set:
        detail["extra"].append(s)

    # weighted score
    total_weight = 0.0
    got_weight   = 0.0
    for cat, req in cat_req.items():
        w = CATEGORY_WEIGHTS.get(cat, 1.0)
        total_weight += w * req
        got_weight   += w * cat_hit.get(cat, 0)
    score = 0.0 if total_weight == 0 else round(100.0 * got_weight / total_weight, 2)
    # keep lists sorted for stable display
    for k in detail:
        detail[k] = sorted(detail[k])
    return score, detail

def analyze_skills(resume_text: str, jd_text: str) -> Dict[str, object]:
    """
    One-call helper used by the UI if you want rich skill analytics.
    """
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
