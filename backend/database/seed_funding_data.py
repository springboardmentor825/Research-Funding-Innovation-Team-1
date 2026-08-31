import sys
import os
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine
from sqlalchemy import text

SEED_DATA = [
    {
        "id": 1,
        "title": "Quantum Computing & Information Science Grant Initiative",
        "funder": "National Science Foundation (NSF)",
        "amount_range": "$150,000 - $500,000",
        "deadline": "2026-12-01",
        "semantic_fit": 96,
        "match_badges": "Topic match,Methodology match,PI overlap",
        "description": "Supports basic research in quantum algorithms, physical qubit scalability, entanglement metrics, and fault-tolerant quantum error correction architectures.",
        "research_domains": "Quantum Computing, Computation Theory",
        "technology_areas": "Quantum Information Science, Superconducting Qubits, Vector Search",
        "keywords": "Quantum Computing, Qubits, Quantum Algorithms, Entanglement, Qubit Control",
        "eligibility": "Ph.D. degree required, Academic or Industry Research Labs",
        "research_stage": "Basic Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 2,
        "title": "Decarbonization Technologies & Clean Energy Innovation",
        "funder": "U.S. Department of Energy (DOE)",
        "amount_range": "$500,000 - $1,200,000",
        "deadline": "2026-10-15",
        "semantic_fit": 88,
        "match_badges": "Methodology match,Equipment overlap",
        "description": "Research initiative focused on industrial decarbonization, renewable grid integration, green hydrogen production, and direct air carbon capture.",
        "research_domains": "Energy & Sustainability, Environmental Science",
        "technology_areas": "Decarbonization, Clean Energy, Carbon Capture, Smart Grid",
        "keywords": "Decarbonization, Clean Energy, Solar, Wind, Carbon Storage, Renewable Energy",
        "eligibility": "University, National Lab, or Non-profit Organization",
        "research_stage": "Applied Research",
        "geographic_scope": "United States",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 3,
        "title": "AI in Translational Medicine & Deep Pathology Diagnostics",
        "funder": "National Institutes of Health (NIH)",
        "amount_range": "$250,000 - $600,000",
        "deadline": "2026-11-30",
        "semantic_fit": 94,
        "match_badges": "Topic match,Co-author match",
        "description": "Grant focusing on applying deep learning architectures to clinical genomics, digital pathology image segmentation, and early stage disease biomarker prediction.",
        "research_domains": "Healthcare AI, Bioinformatics, Medicine",
        "technology_areas": "Artificial Intelligence, Deep Learning, Pathology Diagnostics, Computer Vision",
        "keywords": "Healthcare AI, Deep Learning, Medical Diagnostics, Pathology, Bioinformatics, Medical Imaging",
        "eligibility": "Tenure-track or Clinical Faculty",
        "research_stage": "Translational Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 4,
        "title": "Advanced Materials Research & Nanotechnology Grants",
        "funder": "Defense Advanced Research Projects Agency (DARPA)",
        "amount_range": "$300,000 - $800,000",
        "deadline": "2026-09-20",
        "semantic_fit": 75,
        "match_badges": "Topic match",
        "description": "Program supporting novel synthetic materials synthesis, high-temperature superconductors, self-healing polymers, and nanostructure fabrication.",
        "research_domains": "Materials Science, Nanotechnology",
        "technology_areas": "Advanced Nanomaterials, Metamaterials, Nanofabrication",
        "keywords": "Nanotechnology, Materials Science, Metamaterials, Nanofabrication, Polymers",
        "eligibility": "Approved US academic research teams and defense laboratories",
        "research_stage": "Applied Research",
        "geographic_scope": "United States",
        "funding_type": "Contract",
        "status": "active"
    },
    {
        "id": 5,
        "title": "AI Research Grant 2026",
        "funder": "National Science Foundation (NSF)",
        "amount_range": "$50,000 - $100,000",
        "deadline": "2026-12-31",
        "semantic_fit": 95,
        "match_badges": "AI,ML,RAG",
        "description": "Flagship grant program supporting foundational advances in generative AI, Retrieval Augmented Generation (RAG), Large Language Models (LLMs), and semantic memory systems.",
        "research_domains": "Artificial Intelligence, Data Science, Machine Learning",
        "technology_areas": "RAG, LLMs, NLP, Transformers, Generative AI, Vector Search",
        "keywords": "AI, Machine Learning, RAG, LLMs, NLP, Generative AI, Deep Learning, Vector Search",
        "eligibility": "Faculty researchers and academic research teams",
        "research_stage": "Basic Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 6,
        "title": "Healthcare Innovation Fund",
        "funder": "World Health Organization (WHO)",
        "amount_range": "$100,000 - $500,000",
        "deadline": "2026-11-30",
        "semantic_fit": 88,
        "match_badges": "Healthcare",
        "description": "Global WHO innovation fund for scalable digital healthcare interventions, remote patient monitoring devices, and community epidemiology tracking software.",
        "research_domains": "Healthcare AI, Data Science, Public Health",
        "technology_areas": "Digital Health, Telemedicine, Health Informatics, Wearable Sensors",
        "keywords": "Healthcare, Health Informatics, Digital Health, Biomedical Systems, Telemedicine",
        "eligibility": "Healthcare Institutions & Accredited Research Foundations",
        "research_stage": "Applied Research",
        "geographic_scope": "Global",
        "funding_type": "Innovation Grant",
        "status": "active"
    },
    {
        "id": 7,
        "title": "Smart Agriculture & Soil Precision Sensing Program",
        "funder": "Food and Agriculture Organization (FAO)",
        "amount_range": "$25,000 - $75,000",
        "deadline": "2026-10-15",
        "semantic_fit": 82,
        "match_badges": "Agriculture",
        "description": "FAO smart agriculture grant aimed at climate-resilient crop management, precision Internet-of-Things sensor networks, and autonomous soil nitrate analysis.",
        "research_domains": "Smart Agriculture, Environmental Science",
        "technology_areas": "Precision Agriculture, Smart Sensing, Soil Analytics, AgTech IoT",
        "keywords": "Agriculture, Precision Farming, Crop Yield, Soil Monitoring, AgTech, Sensors",
        "eligibility": "Agricultural researchers and agricultural university departments",
        "research_stage": "Applied Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 8,
        "title": "Cybersecurity & Zero-Trust Architecture Grant",
        "funder": "National Institute of Standards and Technology (NIST)",
        "amount_range": "$75,000 - $150,000",
        "deadline": "2026-09-20",
        "semantic_fit": 91,
        "match_badges": "Cybersecurity",
        "description": "NIST research grant for resilient network cryptography, automated vulnerability scanning using static analysis, and zero-trust verification protocols.",
        "research_domains": "Cybersecurity, Computer Networks",
        "technology_areas": "Network Cryptography, Zero Trust Systems, Threat Detection, Static Analysis",
        "keywords": "Cybersecurity, Cryptography, Zero Trust, Network Security, Encryption, Threat Detection",
        "eligibility": "University researchers and cybersecurity labs",
        "research_stage": "Applied Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 9,
        "title": "Robotics & Surgical Autonomous Systems Award",
        "funder": "IEEE Robotics and Automation Society",
        "amount_range": "$50,000 - $200,000",
        "deadline": "2026-09-15",
        "semantic_fit": 89,
        "match_badges": "Robotics",
        "description": "IEEE grant supporting next-generation minimally invasive surgical robotics, haptic feedback actuators, and real-time visual simultaneous localization and mapping (SLAM).",
        "research_domains": "Robotics, Computer Vision, Control Systems",
        "technology_areas": "Autonomous Mobile Robotics, Haptics, Computer Vision, SLAM",
        "keywords": "Robotics, Autonomous Systems, Mechatronics, Kinematics, SLAM, Haptics",
        "eligibility": "IEEE Members and robotics laboratory researchers",
        "research_stage": "Prototyping",
        "geographic_scope": "Global",
        "funding_type": "Award",
        "status": "active"
    },
    {
        "id": 10,
        "title": "Quantum Software & Error Mitigation Fellowship",
        "funder": "IBM Quantum Research",
        "amount_range": "$100,000 - $500,000",
        "deadline": "2025-12-31",
        "semantic_fit": 94,
        "match_badges": "Quantum",
        "description": "IBM fellowship program for novel quantum software development, noise cancellation techniques, and pulse-level superconducting qubit optimization.",
        "research_domains": "Quantum Computing, Software Engineering",
        "technology_areas": "Qubit Control, Quantum Error Correction, Qiskit",
        "keywords": "Quantum, Qubit, Superconducting Qubits, Quantum Software, Noise Reduction",
        "eligibility": "Early-career researchers and PhD candidates",
        "research_stage": "Basic Research",
        "geographic_scope": "Global",
        "funding_type": "Fellowship",
        "status": "closed"
    },
    {
        "id": 11,
        "title": "Natural Language Processing for Low-Resource Languages",
        "funder": "Google Research Initiative",
        "amount_range": "$80,000 - $250,000",
        "deadline": "2026-11-15",
        "semantic_fit": 93,
        "match_badges": "NLP,AI",
        "description": "Research support for multilingual transformer models, low-resource speech synthesis, cross-lingual representation learning, and translation benchmarks.",
        "research_domains": "Natural Language Processing, Artificial Intelligence",
        "technology_areas": "NLP, Transformers, Multilingual LLMs, Speech Processing",
        "keywords": "NLP, Language Models, Transformers, Low-Resource Languages, Speech Synthesis",
        "eligibility": "Academic researchers and non-profit computational linguistics groups",
        "research_stage": "Applied Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 12,
        "title": "Clean Energy Storage & Solid-State Battery Challenge",
        "funder": "European Research Council (ERC)",
        "amount_range": "$400,000 - $1,000,000",
        "deadline": "2026-12-15",
        "semantic_fit": 86,
        "match_badges": "CleanEnergy",
        "description": "Breakthrough research challenge funding next-generation solid-state lithium battery electrolytes, grid-scale thermal storage, and electrochemical efficiency.",
        "research_domains": "Energy & Sustainability, Chemistry",
        "technology_areas": "Solid-State Batteries, Energy Storage, Electrochemistry",
        "keywords": "Battery, Clean Energy, Energy Storage, Electrochemistry, Electrolytes",
        "eligibility": "European Union and international associated research institutions",
        "research_stage": "Experimental Development",
        "geographic_scope": "European Union",
        "funding_type": "Challenge Grant",
        "status": "active"
    },
    {
        "id": 13,
        "title": "Climate Change Modeling & Satellite Earth Observation",
        "funder": "NASA Earth Science Division",
        "amount_range": "$200,000 - $650,000",
        "deadline": "2026-10-30",
        "semantic_fit": 87,
        "match_badges": "Climate,DataScience",
        "description": "Geospatial data analysis using hyperspectral satellite images to model deforestation, ocean temperature anomalies, and global ice sheet retreat.",
        "research_domains": "Environmental Science, Data Science",
        "technology_areas": "Remote Sensing, Geospatial Analytics, Climate Modeling, GIS",
        "keywords": "Climate Modeling, Remote Sensing, Geospatial, Satellite Imagery, GIS",
        "eligibility": "Earth science researchers and university remote sensing units",
        "research_stage": "Applied Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 14,
        "title": "Autonomous Drone Systems & Vision Navigation Grant",
        "funder": "Air Force Office of Scientific Research (AFOSR)",
        "amount_range": "$150,000 - $450,000",
        "deadline": "2026-09-10",
        "semantic_fit": 84,
        "match_badges": "Robotics,Vision",
        "description": "Vision-based autonomous flight control for unmanned aerial vehicles operating in GPS-denied environments using edge computer vision algorithms.",
        "research_domains": "Autonomous Systems, Computer Vision, Robotics",
        "technology_areas": "Computer Vision, Autonomous Flight, Edge Computing, Visual Odometry",
        "keywords": "Drones, Autonomous Navigation, Computer Vision, GPS-Denied, Edge Computing",
        "eligibility": "Accredited aerospace engineering departments and research units",
        "research_stage": "Applied Research",
        "geographic_scope": "United States",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 15,
        "title": "Edge Computing Security & Industrial IoT Vulnerability",
        "funder": "Intel University Research Office",
        "amount_range": "$60,000 - $180,000",
        "deadline": "2026-11-01",
        "semantic_fit": 85,
        "match_badges": "Cybersecurity,IoT",
        "description": "Hardware-enforced trusted execution environments, side-channel attack mitigation, and firmware integrity verification for edge IoT gateways.",
        "research_domains": "Cybersecurity, Embedded Systems",
        "technology_areas": "Edge Computing, Hardware Security, Trusted Execution Environment, IoT",
        "keywords": "Edge Security, Hardware Security, IoT, Firmware, Trusted Execution",
        "eligibility": "University faculty and security research labs",
        "research_stage": "Applied Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 16,
        "title": "Generative AI & Knowledge Graph Integration Seed Fund",
        "funder": "Microsoft Research Outreach",
        "amount_range": "$70,000 - $150,000",
        "deadline": "2026-12-20",
        "semantic_fit": 96,
        "match_badges": "AI,LLM,Graph",
        "description": "Investigating the fusion of structured Knowledge Graphs with generative Large Language Models to improve reasoning accuracy and reduce hallucinations.",
        "research_domains": "Artificial Intelligence, Knowledge Representation",
        "technology_areas": "Knowledge Graphs, LLMs, RAG, Generative AI, Graph Neural Networks",
        "keywords": "Knowledge Graphs, Generative AI, LLM, RAG, Graph Neural Networks, Semantic Web",
        "eligibility": "Computer science faculty and AI doctoral labs",
        "research_stage": "Basic Research",
        "geographic_scope": "Global",
        "funding_type": "Seed Funding",
        "status": "active"
    },
    {
        "id": 17,
        "title": "Bio-Innovation & CRISPR Gene Editing Safety Accelerator",
        "funder": "Bill & Melinda Gates Foundation",
        "amount_range": "$300,000 - $900,000",
        "deadline": "2026-10-01",
        "semantic_fit": 80,
        "match_badges": "BioTech",
        "description": "Precision CRISPR cas off-target monitoring, viral vector delivery optimization, and therapeutic safety evaluation for infectious disease intervention.",
        "research_domains": "Biotechnology, Genomics",
        "technology_areas": "CRISPR Gene Editing, Genomic Sequencing, Vector Delivery",
        "keywords": "CRISPR, Biotechnology, Gene Editing, Genomics, Disease Therapy",
        "eligibility": "Global biotechnology institutes and university bioengineering labs",
        "research_stage": "Translational Research",
        "geographic_scope": "Global",
        "funding_type": "Accelerator",
        "status": "active"
    },
    {
        "id": 18,
        "title": "Smart Cities & Intelligent Urban Transportation Systems",
        "funder": "Department of Transportation (DOT)",
        "amount_range": "$100,000 - $350,000",
        "deadline": "2026-09-25",
        "semantic_fit": 78,
        "match_badges": "SmartCities",
        "description": "Traffic flow optimization using connected vehicle V2X communications, urban congestion predictive modeling, and micro-mobility integration.",
        "research_domains": "Urban Planning, Data Science",
        "technology_areas": "Intelligent Transportation Systems, V2X, Traffic Analytics, IoT",
        "keywords": "Smart Cities, Transportation, V2X, Traffic Optimization, Urban Analytics",
        "eligibility": "Municipal research consortia and civil engineering faculties",
        "research_stage": "Development",
        "geographic_scope": "United States",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 19,
        "title": "Educational Technology & Adaptive Learning AI Grant",
        "funder": "Department of Education Innovation Fund",
        "amount_range": "$40,000 - $120,000",
        "deadline": "2026-11-20",
        "semantic_fit": 81,
        "match_badges": "EdTech,AI",
        "description": "Personalized learning systems using adaptive pedagogical AI tutors, student engagement telemetry analysis, and automated rubric scoring tools.",
        "research_domains": "Educational Technology, Artificial Intelligence",
        "technology_areas": "Adaptive Learning, AI Tutoring, Learning Analytics, NLP",
        "keywords": "EdTech, Adaptive Learning, AI Tutor, Automated Assessment, Learning Analytics",
        "eligibility": "Educational researchers and K-12 innovation centers",
        "research_stage": "Applied Research",
        "geographic_scope": "United States",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 20,
        "title": "Patent Commercialization & University Technology Transfer",
        "funder": "National Innovation & Technology Transfer Board",
        "amount_range": "$50,000 - $150,000",
        "deadline": "2026-10-31",
        "semantic_fit": 83,
        "match_badges": "Patents,Innovation",
        "description": "Proof-of-concept validation, prototype maturation, and commercial licensing readiness for high-impact patented inventions in academic labs.",
        "research_domains": "Technology Transfer, Innovation Management",
        "technology_areas": "Prototyping, Patent Licensing, Commercialization Strategy",
        "keywords": "Technology Transfer, Patents, Commercialization, Proof of Concept, Licensing",
        "eligibility": "University IP holders and spin-off technology founders",
        "research_stage": "Commercialization",
        "geographic_scope": "Global",
        "funding_type": "Innovation Grant",
        "status": "active"
    },
    {
        "id": 21,
        "title": "Deep Learning for Protein Folding & Drug Discovery",
        "funder": "Wellcome Trust",
        "amount_range": "$350,000 - $850,000",
        "deadline": "2026-12-05",
        "semantic_fit": 92,
        "match_badges": "Bio,DL",
        "description": "Machine learning computational frameworks predicting 3D macromolecular structures, ligand binding affinities, and target molecule synthesis routes.",
        "research_domains": "Computational Biology, Machine Learning",
        "technology_areas": "Molecular Modeling, Deep Learning, Protein Folding, AlphaFold",
        "keywords": "Protein Folding, Drug Discovery, Computational Biology, Deep Learning, Molecular Structure",
        "eligibility": "Postdoctoral researchers and structural biology groups",
        "research_stage": "Basic Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 22,
        "title": "Renewable Offshore Wind Energy Hydrodynamics",
        "funder": "Ocean Energy Agency",
        "amount_range": "$200,000 - $550,000",
        "deadline": "2025-06-30",
        "semantic_fit": 70,
        "match_badges": "Energy",
        "description": "Numerical modeling of floating offshore wind turbine moorings, wave interaction fatigue analysis, and seabed cable degradation.",
        "research_domains": "Marine Engineering, Renewable Energy",
        "technology_areas": "Offshore Wind, Fluid Dynamics, Marine Turbines",
        "keywords": "Offshore Wind, Renewable Energy, Hydrodynamics, Marine Engineering, Turbines",
        "eligibility": "Marine engineering institutes",
        "research_stage": "Applied Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "closed"
    },
    {
        "id": 23,
        "title": "Marine Biology & Coral Reef Conservation Sensing",
        "funder": "National Oceanic and Atmospheric Administration (NOAA)",
        "amount_range": "$45,000 - $110,000",
        "deadline": "2026-11-10",
        "semantic_fit": 72,
        "match_badges": "MarineBio",
        "description": "Autonomous underwater vehicle micro-sensor payloads measuring coral acidification, thermal stress indicators, and marine biodiversity soundscapes.",
        "research_domains": "Marine Biology, Environmental Science",
        "technology_areas": "Underwater Autonomous Sensors, Acoustic Monitoring, eDNA",
        "keywords": "Marine Biology, Oceanography, Coral Reefs, Conservation, Underwater Sensors",
        "eligibility": "Marine biology researchers and conservation foundations",
        "research_stage": "Applied Research",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 24,
        "title": "Next-Gen Semiconductor Fabrication & Lithography",
        "funder": "Semiconductor Research Corporation (SRC)",
        "amount_range": "$250,000 - $700,000",
        "deadline": "2026-12-10",
        "semantic_fit": 89,
        "match_badges": "Hardware,Semiconductors",
        "description": "Sub-2nm extreme ultraviolet (EUV) lithography resist chemistry, gate-all-around transistor defect inspection, and interconnect RC delay reduction.",
        "research_domains": "Semiconductor Engineering, Physics",
        "technology_areas": "EUV Lithography, GAA Transistors, Sub-2nm Lithography",
        "keywords": "Semiconductors, Lithography, Microchips, GAAFET, EUV, Silicon Fabrication",
        "eligibility": "Microelectronics research departments",
        "research_stage": "Experimental Development",
        "geographic_scope": "Global",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 25,
        "title": "Privacy-Preserving Federated Learning in Finance",
        "funder": "FinTech Innovation Council",
        "amount_range": "$85,000 - $220,000",
        "deadline": "2026-10-20",
        "semantic_fit": 90,
        "match_badges": "FinTech,ML",
        "description": "Distributed federated machine learning models using homomorphic encryption and differential privacy for multi-bank anti-money laundering detection.",
        "research_domains": "Data Science, Cybersecurity, Financial Tech",
        "technology_areas": "Federated Learning, Differential Privacy, Homomorphic Encryption, Machine Learning",
        "keywords": "Federated Learning, Differential Privacy, FinTech, Encryption, Fraud Detection",
        "eligibility": "Financial computing labs and computer science researchers",
        "research_stage": "Applied Research",
        "geographic_scope": "Global",
        "funding_type": "Innovation Grant",
        "status": "active"
    },
    {
        "id": 26,
        "title": "Explainable AI (XAI) for High-Stakes Decision Making",
        "funder": "Defense Advanced Research Projects Agency (DARPA)",
        "amount_range": "$200,000 - $600,000",
        "deadline": "2026-11-25",
        "semantic_fit": 94,
        "match_badges": "XAI,AI",
        "description": "Human-understandable model attribution methods, counterfactual explanations, and trustworthy AI verification frameworks for critical systems.",
        "research_domains": "Artificial Intelligence, Human-Computer Interaction",
        "technology_areas": "Explainable AI, Model Attribution, Counterfactual Reasoning, Interpretability",
        "keywords": "Explainable AI, XAI, Trustworthy AI, Interpretability, Decision Support, Model Attribution",
        "eligibility": "AI ethics and machine learning research groups",
        "research_stage": "Basic Research",
        "geographic_scope": "United States",
        "funding_type": "Contract",
        "status": "active"
    },
    {
        "id": 27,
        "title": "Space Weather Forecasting & Magnetosphere Data Fusion",
        "funder": "European Space Agency (ESA)",
        "amount_range": "$180,000 - $480,000",
        "deadline": "2026-12-28",
        "semantic_fit": 79,
        "match_badges": "Space,Astrophysics",
        "description": "Real-time solar flare trajectory modeling, coronal mass ejection shockwave prediction, and satellite radiation hazard warning systems.",
        "research_domains": "Astrophysics, Data Science",
        "technology_areas": "Solar Magnetometry, Space Weather Analytics, Predictive Modeling",
        "keywords": "Space Weather, Solar Flares, ESA, Magnetosphere, Astrophysics, Radiation Protection",
        "eligibility": "Astrophysics research institutes and space science laboratories",
        "research_stage": "Applied Research",
        "geographic_scope": "European Union",
        "funding_type": "Research Grant",
        "status": "active"
    },
    {
        "id": 28,
        "title": "India National AI for Agriculture & Water Security",
        "funder": "NITI Aayog Innovation Mission (India)",
        "amount_range": "₹2,500,000 - ₹7,500,000 ($30,000 - $90,000)",
        "deadline": "2026-10-10",
        "semantic_fit": 88,
        "match_badges": "India,AgTech,AI",
        "description": "AI-driven monsoon rainfall forecasting, ground-water table extraction monitoring, and regional crop yield risk insurance assessment across Indian agricultural belts.",
        "research_domains": "Smart Agriculture, Artificial Intelligence, Water Resources",
        "technology_areas": "Computer Vision, Remote Sensing, AI Weather Prediction, GIS",
        "keywords": "Agriculture, India, Monsoon Forecasting, Water Security, Crop Insurance, AI",
        "eligibility": "Indian academic institutions, ICAR labs, and approved AgTech incubators",
        "research_stage": "Applied Research",
        "geographic_scope": "India",
        "funding_type": "Seed Funding",
        "status": "active"
    },
    {
        "id": 29,
        "title": "Swarm Robotics for Search & Rescue in Disaster Zones",
        "funder": "Red Cross Humanitarian Technology Fund",
        "amount_range": "$50,000 - $160,000",
        "deadline": "2026-09-05",
        "semantic_fit": 87,
        "match_badges": "Robotics,Humanitarian",
        "description": "Distributed multi-robot coordination algorithms, mesh communication networks, and thermal victim detection for urban search and rescue operations.",
        "research_domains": "Robotics, Autonomous Systems",
        "technology_areas": "Swarm Robotics, Mesh Networking, Thermal Sensing, Multi-Agent Systems",
        "keywords": "Swarm Robotics, Search and Rescue, Disaster Relief, Multi-Agent Systems, Autonomous Swarms",
        "eligibility": "Robotics research laboratories and disaster response tech groups",
        "research_stage": "Prototyping",
        "geographic_scope": "Global",
        "funding_type": "Challenge Grant",
        "status": "active"
    },
    {
        "id": 30,
        "title": "Circular Economy & Plastic Recycling Catalyst Chemistry",
        "funder": "Global Environmental Facility (GEF)",
        "amount_range": "$120,000 - $380,000",
        "deadline": "2026-11-05",
        "semantic_fit": 76,
        "match_badges": "Chemistry,Environment",
        "description": "Enzymatic plastic depolymerization, catalytic chemical recycling of mixed post-consumer polymers, and closed-loop material lifecycle design.",
        "research_domains": "Chemistry, Environmental Science",
        "technology_areas": "Enzymatic Recycling, Catalysts, Polymer Chemistry, Circular Economy",
        "keywords": "Plastic Recycling, Circular Economy, Polymer Chemistry, Catalysis, Waste Reduction",
        "eligibility": "University chemistry departments and environmental research institutes",
        "research_stage": "Experimental Development",
        "geographic_scope": "Global",
        "funding_type": "Innovation Grant",
        "status": "active"
    }
]

def seed_database():
    sql_statements = []
    
    with engine.connect() as conn:
        for rec in SEED_DATA:
            # Check if record exists by ID
            existing = conn.execute(text("SELECT id FROM funding_opportunities WHERE id = :id"), {"id": rec["id"]}).first()
            if existing:
                update_sql = """
                UPDATE funding_opportunities SET
                    title = :title,
                    funder = :funder,
                    amount_range = :amount_range,
                    deadline = :deadline,
                    semantic_fit = :semantic_fit,
                    match_badges = :match_badges,
                    description = :description,
                    research_domains = :research_domains,
                    technology_areas = :technology_areas,
                    keywords = :keywords,
                    eligibility = :eligibility,
                    research_stage = :research_stage,
                    geographic_scope = :geographic_scope,
                    funding_type = :funding_type,
                    status = :status
                WHERE id = :id;
                """
                conn.execute(text(update_sql), rec)
                print(f"Updated record ID {rec['id']}: {rec['title']}")
            else:
                insert_sql = """
                INSERT INTO funding_opportunities (
                    id, title, funder, amount_range, deadline, semantic_fit, match_badges,
                    description, research_domains, technology_areas, keywords, eligibility,
                    research_stage, geographic_scope, funding_type, status
                ) VALUES (
                    :id, :title, :funder, :amount_range, :deadline, :semantic_fit, :match_badges,
                    :description, :research_domains, :technology_areas, :keywords, :eligibility,
                    :research_stage, :geographic_scope, :funding_type, :status
                );
                """
                conn.execute(text(insert_sql), rec)
                print(f"Inserted new record ID {rec['id']}: {rec['title']}")
        conn.commit()
    print("\nDatabase seeding completed successfully! Total records upserted: 30")

def generate_sql_file():
    sql_lines = [
        "-- backend/database/seed_funding_data.sql",
        "-- Synthetic seed script for 30 normalized funding opportunities",
        "USE research_platform;\n"
    ]
    for r in SEED_DATA:
        # Escape single quotes for SQL string literals
        def esc(val):
            if val is None:
                return "NULL"
            return "'" + str(val).replace("'", "''") + "'"

        sql = f"""INSERT INTO funding_opportunities (id, title, funder, amount_range, deadline, semantic_fit, match_badges, description, research_domains, technology_areas, keywords, eligibility, research_stage, geographic_scope, funding_type, status)
VALUES ({r['id']}, {esc(r['title'])}, {esc(r['funder'])}, {esc(r['amount_range'])}, {esc(r['deadline'])}, {r['semantic_fit']}, {esc(r['match_badges'])}, {esc(r['description'])}, {esc(r['research_domains'])}, {esc(r['technology_areas'])}, {esc(r['keywords'])}, {esc(r['eligibility'])}, {esc(r['research_stage'])}, {esc(r['geographic_scope'])}, {esc(r['funding_type'])}, {esc(r['status'])})
ON DUPLICATE KEY UPDATE
title=VALUES(title), funder=VALUES(funder), amount_range=VALUES(amount_range), deadline=VALUES(deadline), semantic_fit=VALUES(semantic_fit), match_badges=VALUES(match_badges), description=VALUES(description), research_domains=VALUES(research_domains), technology_areas=VALUES(technology_areas), keywords=VALUES(keywords), eligibility=VALUES(eligibility), research_stage=VALUES(research_stage), geographic_scope=VALUES(geographic_scope), funding_type=VALUES(funding_type), status=VALUES(status);
"""
        sql_lines.append(sql)

    sql_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "seed_funding_data.sql"))
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines))
    print(f"Generated SQL seed file at: {sql_path}")

if __name__ == "__main__":
    generate_sql_file()
    seed_database()
