import re

TECH_SKILLS = [
    # Programming Languages
    "Python", "Java", "JavaScript", "JS", "TypeScript", "SQL", "Bash", "PowerShell", "C",

    # Frontend Frameworks
    "React.js", "React", "React Native", "Redux", "Next.js", "AngularJS", "HTML5", "CSS3", "Bootstrap", "Figma", "D3.js",

    # Backend Frameworks
    "Node.js", "Express.js", "Spring Boot", "FastAPI", "Flask", "REST APIs", "Microservices Architecture", "API",

    # Databases
    "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis", "Redshift", "BigQuery", "Oracle", "Cassandra", "DynamoDB", "Vector Databases", "FAISS", "Pinecone", "Weaviate",

    # Cloud + DevOps
    "AWS", "Azure", "GCP", "Google Cloud Platform", "AWS EC2", "AWS S3", "AWS RDS", "AWS Lambda", "AWS Glue", "AWS EMR", "IAM", "CloudWatch", "Redshift", "SageMaker", "Vertex AI", "Docker", "Kubernetes", "EKS", "ECS", "Terraform", "Jenkins", "Git", "GitHub Actions", "Ansible", "CICD", "CICD Pipelines", "VPC",

    # ML / Data Engineering
    "Scikit-learn", "PyTorch", "TensorFlow", "MLflow", "TorchServe", "TensorFlow Serving", "Feature Stores", "Data Modeling", "ETL", "Data Warehousing", "Airflow", "Spark", "Kafka", "Apache Airflow", "Apache Spark", "Data Quality", "Data Governance", "Streaming", "Messaging", "Kinesis", "PubSub", "RabbitMQ", "Flask",

    # NLP / LLM
    "Natural Language Processing", "Large Language Models", "Hugging Face Transformers", "OpenAI APIs", "LangChain", "RAG Pipelines", "Prompt Engineering", "BERT", "RoBERTa", "GPT", "Embeddings", "Fine-tuning", "Adversarial Robustness",

    # Monitoring/Analytics
    "Amazon CloudWatch", "Prometheus", "Grafana", "ELK Stack", "Elasticsearch", "Logstash", "Kibana", "Tableau", "Power BI",

    # Testing/Practices
    "Unit Testing", "Integration Testing", "Debugging", "TDD", "AgileScrum", "Jest", "Cypress", "JUnit", "Mockito", "AB Testing", "Experiment Tracking",
]

ALIASES = {
    "js": "JavaScript", "tf": "TensorFlow", "pt": "PyTorch", "k8s": "Kubernetes",
    "gcp": "Google Cloud Platform", "ml": "Machine Learning", "faiss": "FAISS",
    "huggingface": "Hugging Face Transformers", "llm": "Large Language Models",
    "sql": "SQL", "aws": "AWS", "cicd": "CICD", "bert": "BERT", "roberta": "RoBERTa",
    "api": "API",
    # add more as needed!
}

def normalize_skill(skill):
    s = skill.lower().strip()
    return ALIASES.get(s, skill.strip())

def extract_skills(text):
    skills_found = set()
    # Scan for any direct hits in the text
    for skill in TECH_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            skills_found.add(normalize_skill(skill))
    # Block extraction for skills sections
    blocks = re.findall(r'(Skills:|Technical Skills:)(.+?)(?=\n[A-Z][a-z]+:|\Z)', text, re.IGNORECASE | re.DOTALL)
    for _, block in blocks:
        for part in block.split(','):
            nskill = normalize_skill(part)
            if nskill in TECH_SKILLS or nskill in ALIASES.values():
                skills_found.add(nskill)
    return sorted(skills_found)

def compare_skills(resume_skills, jd_skills):
    norm_resume = set([normalize_skill(s) for s in resume_skills])
    norm_jd = set([normalize_skill(s) for s in jd_skills])
    return sorted(norm_jd - norm_resume)
