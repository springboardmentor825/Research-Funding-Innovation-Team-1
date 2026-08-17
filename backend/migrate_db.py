import pymysql

def run_migration():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Madhu@123',
        database='research_platform',
        autocommit=True
    )
    cur = conn.cursor()

    print("--- 1. Migrating funding_opportunities table ---")
    columns_to_add = [
        ("description", "TEXT NULL"),
        ("research_domains", "VARCHAR(500) NULL"),
        ("technology_areas", "VARCHAR(500) NULL"),
        ("keywords", "VARCHAR(500) NULL"),
        ("eligibility", "VARCHAR(500) NULL"),
        ("research_stage", "VARCHAR(100) NULL"),
        ("geographic_scope", "VARCHAR(100) NULL"),
        ("funding_type", "VARCHAR(100) NULL"),
        ("status", "VARCHAR(50) NOT NULL DEFAULT 'open'")
    ]

    cur.execute("DESCRIBE funding_opportunities")
    existing_cols = [r[0] for r in cur.fetchall()]

    for col_name, col_type in columns_to_add:
        if col_name not in existing_cols:
            print(f"Adding column `{col_name}` to `funding_opportunities`...")
            cur.execute(f"ALTER TABLE funding_opportunities ADD COLUMN `{col_name}` {col_type};")
        else:
            print(f"Column `{col_name}` already exists.")

    print("\n--- 2. Creating funding_recommendations table ---")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS funding_recommendations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            funding_id INT NOT NULL,
            match_score FLOAT NOT NULL,
            reason TEXT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'recommended',
            feedback VARCHAR(50) NULL,
            INDEX idx_rec_user (user_id),
            INDEX idx_rec_funding (funding_id),
            CONSTRAINT fk_rec_user FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
            CONSTRAINT fk_rec_funding FOREIGN KEY (funding_id) REFERENCES funding_opportunities(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    print("\n--- 3. Enriching funding_opportunities data with matching features ---")
    # Mapping specific opportunities to detailed domain/tech/keyword/eligibility features
    enrichment = [
        {
            "id": 1,
            "domains": "Quantum Computing, Computation Theory",
            "tech": "Quantum Information Science, Superconducting Qubits",
            "keywords": "Quantum Computing, Qubits, Quantum Algorithms, Entanglement",
            "desc": "Funding for pioneering quantum algorithms, physical qubit scalability, and quantum fault tolerance.",
            "eligibility": "Ph.D. degree required, Academic or Industry Research Labs",
            "stage": "Basic Research", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 2,
            "domains": "Energy & Sustainability, Environmental Science",
            "tech": "Decarbonization, Clean Energy, Carbon Capture",
            "keywords": "Decarbonization, Clean Energy, Solar, Wind, Carbon Storage",
            "desc": "Research initiative focused on industrial decarbonization, renewable grid integration, and zero-emission tech.",
            "eligibility": "University, National Lab, or Non-profit Organization",
            "stage": "Applied Research", "geo": "North America", "type": "Grant", "status": "open"
        },
        {
            "id": 3,
            "domains": "Bioinformatics & Machine Learning, Medicine",
            "tech": "Artificial Intelligence, Deep Learning, Pathology Diagnostics",
            "keywords": "AI, Deep Learning, Medical Diagnostics, Pathology, Bioinformatics",
            "desc": "Grant focusing on applying deep learning architectures to clinical genomics, pathology images, and disease prediction.",
            "eligibility": "Tenure-track or Clinical Faculty",
            "stage": "Translational Research", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 4,
            "domains": "Materials Science, Nanotechnology",
            "tech": "Advanced Nanomaterials, Metamaterials",
            "keywords": "Nanotechnology, Materials Science, Metamaterials, Nanofabrication",
            "desc": "DARPA program for novel synthetic materials, high-temperature superconductors, and nanostructures.",
            "eligibility": "US Citizens or Permanent Residents",
            "stage": "Applied Research", "geo": "USA Only", "type": "Contract", "status": "open"
        },
        {
            "id": 5,
            "domains": "Artificial Intelligence, Data Science",
            "tech": "Retrieval Augmented Generation, Large Language Models, Natural Language Processing",
            "keywords": "AI, Machine Learning, RAG, LLM, Natural Language Processing, Deep Learning",
            "desc": "NSF flagship grant program supporting foundational advances in generative AI, Retrieval Augmented Generation (RAG), and Large Language Models (LLM).",
            "eligibility": "Ph.D., Postdoctoral Researchers, Faculty Investigators",
            "stage": "Basic & Applied Research", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 6,
            "domains": "Healthcare, Biomedical Engineering",
            "tech": "Digital Health, Telemedicine, Health Informatics",
            "keywords": "Healthcare, Health Informatics, Digital Health, Biomedical Systems",
            "desc": "Global WHO innovation fund for scalable digital healthcare interventions and health monitoring systems.",
            "eligibility": "Healthcare Institutions & Research Foundations",
            "stage": "Development", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 7,
            "domains": "Agriculture, Environmental Science",
            "tech": "Precision Agriculture, Smart Sensing, Soil Analytics",
            "keywords": "Agriculture, Precision Farming, Crop Yield, Soil Monitoring, AgTech",
            "desc": "FAO smart agriculture grant aimed at climate-resilient farming, precision sensor networks, and soil quality analysis.",
            "eligibility": "Agricultural Researchers & Institutes",
            "stage": "Applied Research", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 8,
            "domains": "Cybersecurity, Computer Networks",
            "tech": "Network Cryptography, Zero Trust Systems, Threat Detection",
            "keywords": "Cybersecurity, Cryptography, Zero Trust, Network Security, Encryption",
            "desc": "NIST research grant for resilient network security, automated vulnerability analysis, and zero-trust protocol designs.",
            "eligibility": "Cybersecurity Researchers",
            "stage": "Applied Research", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 9,
            "domains": "Robotics, Control Systems",
            "tech": "Autonomous Mobile Robotics, Haptics, Computer Vision",
            "keywords": "Robotics, Autonomous Systems, Mechatronics, Kinematics, SLAM",
            "desc": "IEEE Robotics and Automation grant for next-generation surgical and field robotics.",
            "eligibility": "IEEE Members & Robotics Researchers",
            "stage": "Prototyping", "geo": "Global", "type": "Award", "status": "open"
        },
        {
            "id": 10,
            "domains": "Quantum Computing",
            "tech": "Qubit Control, Quantum Error Correction",
            "keywords": "Quantum, Qubit, Superconducting Qubits, Quantum Software",
            "desc": "IBM quantum research initiative for error mitigation and quantum algorithms.",
            "eligibility": "Quantum Researchers",
            "stage": "Basic Research", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 11,
            "domains": "Data Science, Machine Learning",
            "tech": "Big Data Processing, Statistical Learning",
            "keywords": "Data Science, Machine Learning, Data Mining, Analytics",
            "desc": "Google Data Science Fellowship for doctoral students and early-career researchers.",
            "eligibility": "Ph.D. Candidates & Early Career Researchers",
            "stage": "Fellowship", "geo": "Global", "type": "Fellowship", "status": "open"
        },
        {
            "id": 12,
            "domains": "Artificial Intelligence, Natural Language Processing",
            "tech": "NLP, Transformer Architectures, Semantic Search, Language Models",
            "keywords": "NLP, LLM, Natural Language Processing, Text Analytics, Semantic Matching, Transformers",
            "desc": "Microsoft NLP research grant for large language models, semantic matching systems, and conversational AI.",
            "eligibility": "AI & NLP Researchers",
            "stage": "Basic & Applied Research", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 13,
            "domains": "Energy, Environmental Science",
            "tech": "Renewable Microgrids, Energy Storage",
            "keywords": "Energy, Green Energy, Microgrids, Battery Systems",
            "desc": "UNDP green energy grant for sustainable power networks in developing communities.",
            "eligibility": "Energy & Sustainability Scholars",
            "stage": "Deployment", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 14,
            "domains": "Earth Science, Climate Analytics",
            "tech": "Satellite Remote Sensing, Geospatial AI",
            "keywords": "Climate, Earth Science, Remote Sensing, Geospatial AI",
            "desc": "NASA climate science grant utilizing satellite observational data and geospatial machine learning.",
            "eligibility": "Earth & Environmental Scientists",
            "stage": "Applied Research", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 15,
            "domains": "Patent Analytics, Innovation Management",
            "tech": "IP Commercialization, Patent Similarity Analysis",
            "keywords": "Patents, Intellectual Property, Commercialization, Patent Analytics",
            "desc": "WIPO grant supporting intellectual property commercialization and automated patent analytics.",
            "eligibility": "Inventors & Technology Transfer Offices",
            "stage": "Commercialization", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 16,
            "domains": "Software Engineering, Innovation Systems",
            "tech": "Cloud Computing, Enterprise AI",
            "keywords": "Innovation, Cloud, Software Systems, Scalability",
            "desc": "Infosys Innovation Accelerator for technology-driven start-ups and university labs.",
            "eligibility": "Tech Innovators & Research Startups",
            "stage": "Accelerator", "geo": "India & Global", "type": "Grant", "status": "open"
        },
        {
            "id": 17,
            "domains": "Entrepreneurship, Technology Management",
            "tech": "Venture Acceleration, Prototyping",
            "keywords": "Startup, Commercialization, Prototyping, Venture",
            "desc": "Startup India research support program for deep tech early-stage ventures.",
            "eligibility": "Registered DeepTech Startups",
            "stage": "Early Stage", "geo": "India Only", "type": "Grant", "status": "open"
        },
        {
            "id": 18,
            "domains": "Urban Planning, Civil Engineering",
            "tech": "IoT Smart Grid, Urban Mobility, Traffic Sensing",
            "keywords": "Smart Cities, Urban Tech, IoT, Traffic Intelligence, Infrastructure",
            "desc": "World Bank grant for sustainable urban infrastructure and smart grid management.",
            "eligibility": "Urban Tech Researchers",
            "stage": "Deployment", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 19,
            "domains": "Bioinformatics, Computational Biology",
            "tech": "Genomic Sequencing, Protein Structure Analysis",
            "keywords": "Bioinformatics, Proteomics, DNA Sequencing, Computational Biology",
            "desc": "NIH Bioinformatics research grant for high-throughput gene expression and proteomic modeling.",
            "eligibility": "Computational Biologists",
            "stage": "Basic Research", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 20,
            "domains": "Aerospace Engineering, Space Sciences",
            "tech": "Satellite Propulsion, Payload Design",
            "keywords": "Space, Aerospace, Satellite, Propulsion, Orbit Mechanics",
            "desc": "ISRO space technology research grant for microsatellite payloads and deep space communications.",
            "eligibility": "Aerospace Researchers",
            "stage": "Applied Research", "geo": "India", "type": "Grant", "status": "open"
        },
        {
            "id": 21,
            "domains": "Education, Social Sciences",
            "tech": "Adaptive Learning Systems, EdTech AI",
            "keywords": "EdTech, Adaptive Learning, Educational Analytics, Digital Literacy",
            "desc": "UNESCO grant for AI-driven adaptive learning systems in underserved regions.",
            "eligibility": "EdTech Scholars & Educators",
            "stage": "Field Trial", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 22,
            "domains": "Artificial Intelligence, Data Science",
            "tech": "Ethical AI, AI for Social Good, Machine Learning",
            "keywords": "AI, Social Good, Ethical AI, Public Health AI, Climate AI",
            "desc": "Google.org program funding AI applications in healthcare access, climate action, and community resilience.",
            "eligibility": "Non-profit Organizations & Academic Labs",
            "stage": "Applied Research", "geo": "Global", "type": "Grant", "status": "open"
        },
        {
            "id": 23,
            "domains": "Multidisciplinary Science",
            "tech": "Scientific Computing, Experimental Instrumentation",
            "keywords": "Research, Multidisciplinary, Basic Science, Laboratory",
            "desc": "DST national award for outstanding research achievements across STEM disciplines.",
            "eligibility": "Indian STEM Faculty",
            "stage": "Excellence Award", "geo": "India", "type": "Award", "status": "open"
        },
        {
            "id": 24,
            "domains": "Computer Engineering, High-Performance Computing",
            "tech": "Parallel Architectures, GPU Accelerators, Heterogeneous Computing",
            "keywords": "Computing, HPC, GPU Acceleration, Supercomputing, Systems",
            "desc": "Intel grant supporting high-performance computing architectures and parallel algorithm acceleration.",
            "eligibility": "HPC Systems Researchers",
            "stage": "Basic & Applied Research", "geo": "Global", "type": "Grant", "status": "open"
        }
    ]

    for item in enrichment:
        cur.execute("""
            UPDATE funding_opportunities
            SET research_domains = %s,
                technology_areas = %s,
                keywords = %s,
                description = %s,
                eligibility = %s,
                research_stage = %s,
                geographic_scope = %s,
                funding_type = %s,
                status = %s
            WHERE id = %s
        """, (
            item["domains"], item["tech"], item["keywords"], item["desc"],
            item["eligibility"], item["stage"], item["geo"], item["type"], item["status"],
            item["id"]
        ))

    # Also add an EXPIRED opportunity for testing Task 16 & Task 17 (e.g. set one opportunity or insert an explicit expired test opportunity if not present)
    cur.execute("SELECT id FROM funding_opportunities WHERE title = 'Expired Research Grant Test'")
    if not cur.fetchone():
        print("Inserting sample expired opportunity for testing...")
        cur.execute("""
            INSERT INTO funding_opportunities (title, funder, amount_range, deadline, semantic_fit, match_badges, description, research_domains, technology_areas, keywords, eligibility, research_stage, geographic_scope, funding_type, status)
            VALUES ('Expired Research Grant Test', 'Legacy Foundation', '$10,000', '2023-01-01', 50, 'Expired', 'An old expired grant for testing exclusion.', 'Artificial Intelligence', 'Machine Learning', 'AI, ML', 'Open to all', 'Basic Research', 'Global', 'Grant', 'expired');
        """)

    print("Migration finished successfully!")
    conn.close()

if __name__ == '__main__':
    run_migration()
