from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import re
from pdfplumber import PDF
import pdfplumber
from docx import Document
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

class ResumeAnalyzer:
    def __init__(self):
        self.technical_skills = [
            'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask', 'spring',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'html', 'css', 'sass', 'bootstrap', 'tailwind', 'webpack', 'npm', 'yarn',
            'git', 'rest', 'graphql', 'microservices', 'ci/cd', 'devops', 'machine learning',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'agile', 'scrum', 'jira', 'confluence', 'slack', 'trello'
        ]

        self.soft_skills = [
            'leadership', 'communication', 'teamwork', 'collaboration', 'problem solving',
            'critical thinking', 'time management', 'project management', 'negotiation',
            'presentation', 'adaptability', 'creativity', 'analytical', 'attention to detail'
        ]

        self.action_verbs = [
            'managed', 'developed', 'implemented', 'led', 'designed', 'created', 'improved',
            'optimized', 'automated', 'enhanced', 'established', 'coordinated', 'directed',
            'spearheaded', 'pioneered', 'architected', 'engineered', 'orchestrated',
            'transformed', 'streamlined', 'accelerated', 'boosted', 'elevated', 'expanded'
        ]

        self.certifications = [
            'aws', 'azure', 'google cloud', 'certified', 'certification', 'scrum master',
            'ciscp', 'comptia', 'pmp', 'cissp', 'ccna', 'bachelor', 'master', 'phd'
        ]

    def extract_text_from_file(self, file_path):
        """Extract text from PDF, DOCX, or TXT files"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        try:
            if ext == '.pdf':
                return self.extract_from_pdf(file_path)
            elif ext in ['.docx', '.doc']:
                return self.extract_from_docx(file_path)
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")

    def extract_from_pdf(self, file_path):
        """Extract text from PDF"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text

    def extract_from_docx(self, file_path):
        """Extract text from DOCX"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        return text

    def analyze(self, resume_text):
        """Perform comprehensive resume analysis"""
        text_lower = resume_text.lower()
        
        analysis = {
            'overall_score': 50,
            'strengths': [],
            'improvements': [],
            'recommendations': [],
            'statistics': {},
            'sections': {},
            'keyword_analysis': {}
        }

        # 1. Check for essential sections
        analysis['sections'] = self.analyze_sections(resume_text, text_lower)
        
        # 2. Check for contact information
        contact_info = self.extract_contact_info(resume_text)
        if contact_info['email'] or contact_info['phone']:
            analysis['strengths'].append('Clear contact information provided')
            analysis['overall_score'] += 5
        else:
            analysis['improvements'].append('Missing contact information (email or phone)')
            analysis['recommendations'].append('Add your email address and phone number at the top of the resume')

        # 3. Analyze keywords
        analysis['keyword_analysis'] = self.analyze_keywords(text_lower)
        
        technical_count = len(analysis['keyword_analysis']['technical_skills_found'])
        if technical_count >= 5:
            analysis['strengths'].append(f'Strong technical skills section with {technical_count} skills identified')
            analysis['overall_score'] += 12
        else:
            analysis['improvements'].append('Limited technical skills listed')
            analysis['recommendations'].append('Add more specific technical skills and technologies you are proficient in')
            analysis['overall_score'] -= 3

        # 4. Analyze action verbs
        action_verbs_found = self.find_action_verbs(text_lower)
        if len(action_verbs_found) >= 8:
            analysis['strengths'].append(f'Excellent use of action verbs ({len(action_verbs_found)} found)')
            analysis['overall_score'] += 10
        elif len(action_verbs_found) >= 4:
            analysis['strengths'].append(f'Good use of action verbs ({len(action_verbs_found)} found)')
            analysis['overall_score'] += 5
        else:
            analysis['improvements'].append('Few action verbs used to describe achievements')
            analysis['recommendations'].append('Start each bullet point with strong action verbs like: managed, developed, implemented, led')

        # 5. Check for quantifiable achievements
        metrics = self.extract_metrics(text_lower)
        if len(metrics) >= 3:
            analysis['strengths'].append(f'Strong use of quantifiable metrics and achievements')
            analysis['overall_score'] += 12
        else:
            analysis['improvements'].append('Lacks specific numbers and metrics')
            analysis['recommendations'].append('Add quantifiable achievements with percentages, dollar amounts, or timeframes')

        # 6. Check for soft skills
        soft_skills_found = self.find_soft_skills(text_lower)
        if len(soft_skills_found) >= 3:
            analysis['strengths'].append(f'Demonstrates soft skills ({len(soft_skills_found)} identified)')
            analysis['overall_score'] += 5
        else:
            analysis['recommendations'].append('Consider highlighting relevant soft skills like leadership and communication')

        # 7. Check for certifications
        certs_found = self.find_certifications(text_lower)
        if len(certs_found) > 0:
            analysis['strengths'].append(f'Includes professional certifications/education')
            analysis['overall_score'] += 5

        # 8. Analyze structure and formatting
        structure_score = self.analyze_structure(resume_text, text_lower)
        analysis['overall_score'] += structure_score['score']
        analysis['strengths'].extend(structure_score['strengths'])
        analysis['improvements'].extend(structure_score['improvements'])
        analysis['recommendations'].extend(structure_score['recommendations'])

        # 9. Check word count
        word_count = len(resume_text.split())
        analysis['statistics']['word_count'] = word_count
        analysis['statistics']['line_count'] = len(resume_text.split('\n'))
        analysis['statistics']['character_count'] = len(resume_text)

        if word_count < 200:
            analysis['improvements'].append('Resume is too brief')
            analysis['recommendations'].append('Expand your resume with more details about your achievements')
            analysis['overall_score'] -= 5
        elif word_count > 600:
            analysis['improvements'].append('Resume might be too lengthy')
            analysis['recommendations'].append('Try to keep your resume concise, ideally between 200-600 words')
            analysis['overall_score'] -= 3

        analysis['statistics']['technical_skills_count'] = technical_count
        analysis['statistics']['action_verbs_count'] = len(action_verbs_found)
        analysis['statistics']['metrics_count'] = len(metrics)
        analysis['statistics']['soft_skills_count'] = len(soft_skills_found)
        analysis['statistics']['certifications_count'] = len(certs_found)

        # Ensure score is between 0 and 100
        analysis['overall_score'] = max(0, min(100, analysis['overall_score']))

        # Generate final recommendations
        if analysis['overall_score'] < 50:
            analysis['recommendations'].insert(0, 'Focus on adding more quantifiable achievements and specific skills')
        elif analysis['overall_score'] < 70:
            analysis['recommendations'].insert(0, 'Your resume is solid. Consider the suggestions above for further improvement')
        else:
            analysis['recommendations'].insert(0, 'Excellent resume! Minor refinements can push it to the next level')

        return analysis

    def analyze_sections(self, resume_text, text_lower):
        """Check for essential resume sections"""
        sections = {}
        section_keywords = {
            'contact': ['email', 'phone', 'linkedin'],
            'summary': ['summary', 'objective', 'profile'],
            'experience': ['experience', 'employment', 'work history'],
            'education': ['education', 'degree', 'university', 'college'],
            'skills': ['skills', 'technical skills', 'core competencies'],
            'projects': ['projects', 'portfolio'],
            'certifications': ['certifications', 'licenses', 'awards'],
            'languages': ['languages', 'language skills']
        }

        for section, keywords in section_keywords.items():
            sections[section] = any(keyword in text_lower for keyword in keywords)

        return sections

    def extract_contact_info(self, resume_text):
        """Extract contact information"""
        contact = {'email': None, 'phone': None, 'linkedin': None}
        
        # Email regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, resume_text)
        if email_match:
            contact['email'] = email_match.group(0)

        # Phone regex (various formats)
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, resume_text)
        if phone_match:
            contact['phone'] = phone_match.group(0)

        # LinkedIn regex
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, resume_text, re.IGNORECASE)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group(0)

        return contact

    def analyze_keywords(self, text_lower):
        """Analyze technical and soft skills"""
        result = {
            'technical_skills_found': [],
            'soft_skills_found': [],
            'missing_popular_skills': []
        }

        for skill in self.technical_skills:
            if skill in text_lower:
                result['technical_skills_found'].append(skill)

        for skill in self.soft_skills:
            if skill in text_lower:
                result['soft_skills_found'].append(skill)

        popular_skills = ['python', 'javascript', 'aws', 'docker', 'sql']
        for skill in popular_skills:
            if skill not in text_lower:
                result['missing_popular_skills'].append(skill)

        return result

    def find_action_verbs(self, text_lower):
        """Find action verbs used in resume"""
        found_verbs = []
        for verb in self.action_verbs:
            if verb in text_lower:
                found_verbs.append(verb)
        return found_verbs

    def find_soft_skills(self, text_lower):
        """Find soft skills mentioned"""
        found_skills = []
        for skill in self.soft_skills:
            if skill in text_lower:
                found_skills.append(skill)
        return found_skills

    def find_certifications(self, text_lower):
        """Find certifications and education"""
        found_certs = []
        for cert in self.certifications:
            if cert in text_lower:
                found_certs.append(cert)
        return found_certs

    def extract_metrics(self, text_lower):
        """Extract quantifiable metrics"""
        metrics = []
        
        # Find percentages
        percent_pattern = r'\d+\s*%'
        metrics.extend(re.findall(percent_pattern, text_lower))

        # Find dollar amounts
        dollar_pattern = r'\$\d+[KMB]?'
        metrics.extend(re.findall(dollar_pattern, text_lower))

        # Find numbers followed by multipliers
        number_pattern = r'\d+[XxK]'
        metrics.extend(re.findall(number_pattern, text_lower))

        # Find time periods
        time_pattern = r'\d+\s*(year|month|week|day)s?'
        metrics.extend(re.findall(time_pattern, text_lower))

        return list(set(metrics))

    def analyze_structure(self, resume_text, text_lower):
        """Analyze resume structure and formatting"""
        result = {'score': 0, 'strengths': [], 'improvements': [], 'recommendations': []}

        # Check for clear structure
        lines = resume_text.split('\n')
        if len(lines) > 5:
            result['strengths'].append('Well-structured document with clear sections')
            result['score'] += 3

        # Check for consistency
        if resume_text.count('\n\n') >= 3:
            result['strengths'].append('Good use of spacing and formatting')
            result['score'] += 2

        # Check for professional language (avoid certain casual words)
        casual_words = ['hey', 'cool', 'awesome', 'nice', 'stuff', 'thing']
        casual_count = sum(1 for word in casual_words if f' {word} ' in text_lower)
        if casual_count == 0:
            result['strengths'].append('Professional language throughout')
            result['score'] += 3
        else:
            result['improvements'].append('Uses some informal language')
            result['recommendations'].append('Replace casual language with professional terminology')

        return result


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    """API endpoint for resume analysis"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PDF, DOCX, DOC, TXT'}), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Extract text from file
            analyzer = ResumeAnalyzer()
            resume_text = analyzer.extract_text_from_file(filepath)

            if not resume_text.strip():
                return jsonify({'error': 'Could not extract text from file'}), 400

            # Analyze resume
            analysis = analyzer.analyze(resume_text)

            # Clean up temporary file
            os.remove(filepath)

            return jsonify(analysis), 200

        except Exception as e:
            # Clean up file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sample-analysis', methods=['GET'])
def get_sample_analysis():
    """Get a sample analysis for demo purposes"""
    sample_resume = """
    John Doe
    Email: john.doe@email.com | Phone: (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe

    PROFESSIONAL SUMMARY
    Senior Software Engineer with 8 years of experience in full-stack development. Proficient in Python, JavaScript, and cloud technologies.
    Strong leadership skills and proven track record of delivering complex projects on time.

    TECHNICAL SKILLS
    Languages: Python, JavaScript, Java, C++, SQL
    Frameworks: React, Node.js, Django, Flask, Spring Boot
    Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Jenkins
    Databases: PostgreSQL, MongoDB, Redis, Elasticsearch
    Tools: Git, JIRA, Confluence, Linux

    PROFESSIONAL EXPERIENCE

    Senior Software Engineer - Tech Company (2020-Present)
    - Led a team of 5 engineers in developing microservices architecture, improving system performance by 40%
    - Implemented CI/CD pipelines using Jenkins and Docker, reducing deployment time by 60%
    - Architected and developed RESTful APIs serving 2M+ requests daily
    - Mentored 3 junior developers, resulting in 2 promotions

    Software Engineer - StartUp Inc (2018-2020)
    - Developed and maintained 15+ production applications using React and Node.js
    - Optimized database queries, improving application response time by 50%
    - Implemented automated testing framework, increasing code coverage from 40% to 85%
    - Collaborated with product team to deliver 10+ features quarterly

    Junior Developer - Tech Solutions (2016-2018)
    - Created web applications using HTML, CSS, JavaScript, and Python
    - Participated in agile development and daily standups
    - Fixed 200+ bugs in production environment

    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology, 2016
    GPA: 3.8/4.0

    CERTIFICATIONS
    - AWS Certified Solutions Architect - Professional
    - Certified Scrum Master (CSM)
    - Docker Certified Associate

    PROJECTS
    - Open Source Contributor: Contributed to Django and React projects with 50+ merged PRs
    - Personal Project: Built a real-time analytics dashboard processing 1M+ events per day

    LANGUAGES
    - English (Fluent)
    - Spanish (Intermediate)
    """

    analyzer = ResumeAnalyzer()
    analysis = analyzer.analyze(sample_resume)
    return jsonify(analysis), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
