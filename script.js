class ResumeAnalyzerApp {
    constructor() {
        this.uploadBox = document.getElementById('uploadBox');
        this.fileInput = document.getElementById('fileInput');
        this.jobDescription = document.getElementById('jobDescription');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.resultsSection = document.getElementById('resultsSection');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.resetBtn = document.getElementById('resetBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.tryDemoBtn = document.getElementById('tryDemoBtn');
        this.currentAnalysis = null;
        this.resumeFile = null;

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        if (!this.uploadBox || !this.fileInput) {
            console.error('Required DOM elements not found');
            return;
        }

        // Upload box
        this.uploadBox.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag and drop
        this.uploadBox.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadBox.addEventListener('dragleave', () => this.handleDragLeave());
        this.uploadBox.addEventListener('drop', (e) => this.handleDrop(e));

        // Action buttons
        this.analyzeBtn.addEventListener('click', () => this.analyzeResume());
        this.resetBtn.addEventListener('click', () => this.reset());
        this.downloadBtn.addEventListener('click', () => this.downloadReport());
        this.tryDemoBtn.addEventListener('click', () => this.loadDemo());
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadBox.classList.add('dragover');
    }

    handleDragLeave() {
        this.uploadBox.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadBox.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.fileInput.files = files;
            this.handleFileSelect({ target: { files } });
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length === 0) return;

        const file = files[0];
        const validTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ];

        if (!validTypes.includes(file.type)) {
            alert('Please upload a valid file (PDF, DOCX, DOC, or TXT)');
            this.fileInput.value = '';
            return;
        }

        if (file.size > 16 * 1024 * 1024) {
            alert('File is too large. Maximum size is 16MB');
            this.fileInput.value = '';
            return;
        }

        this.resumeFile = file;
        this.uploadBox.innerHTML = `
            <i class="fas fa-check-circle text-success" style="font-size: 2rem;"></i>
            <p style="margin-top: 1rem;"><strong>File Selected:</strong> ${file.name}</p>
        `;
        this.analyzeBtn.disabled = false;
    }

    analyzeResume() {
        if (!this.resumeFile) {
            alert('Please select a resume file first');
            return;
        }

        const formData = new FormData();
        formData.append('file', this.resumeFile);
        
        // Add job description if provided
        if (this.jobDescription.value && this.jobDescription.value.trim()) {
            formData.append('job_description', this.jobDescription.value.trim());
        }

        this.loadingSpinner.style.display = 'flex';

        fetch('/api/analyze', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                this.loadingSpinner.style.display = 'none';
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    this.displayResults(data);
                }
            })
            .catch(error => {
                this.loadingSpinner.style.display = 'none';
                console.error('Error:', error);
                alert('Error analyzing resume: ' + error.message);
            });
    }

    loadDemo() {
        this.loadingSpinner.style.display = 'flex';

        fetch('/api/sample-analysis')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                this.loadingSpinner.style.display = 'none';
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    this.displayResults(data);
                }
            })
            .catch(error => {
                this.loadingSpinner.style.display = 'none';
                console.error('Error:', error);
                alert('Error loading demo: ' + error.message);
            });
    }

    getScoreDescription(score) {
        if (score >= 80) return "Excellent! Your resume is well-structured, professional, and compelling. You're ready to submit!";
        if (score >= 60) return "Good! Your resume has solid fundamentals. Follow the recommendations above to push it to the next level.";
        if (score >= 40) return "Fair. Your resume needs improvements. Focus on the suggestions to make it more impactful and professional.";
        return "Needs work. Follow the recommendations carefully to significantly enhance your resume's effectiveness.";
    }

    displayResults(analysis) {
        this.currentAnalysis = analysis;

        // Update score with animation
        const score = analysis.overall_score;
        const scoreNumber = document.getElementById('scoreNumber');
        const scoreProgress = document.getElementById('scoreProgress');
        const scoreTitle = document.getElementById('scoreTitle');
        const scoreDescription = document.getElementById('scoreDescription');

        scoreNumber.textContent = score;
        scoreDescription.textContent = this.getScoreDescription(score);

        // Animate progress circle
        const offset = 282.7 * (1 - score / 100);
        setTimeout(() => {
            scoreProgress.style.strokeDashoffset = offset;
        }, 100);

        // Update score title based on score
        if (score >= 80) {
            scoreTitle.textContent = "Outstanding Resume!";
            scoreTitle.style.color = "#10b981";
        } else if (score >= 60) {
            scoreTitle.textContent = "Good Resume!";
            scoreTitle.style.color = "#3b82f6";
        } else if (score >= 40) {
            scoreTitle.textContent = "Needs Improvement";
            scoreTitle.style.color = "#f59e0b";
        } else {
            scoreTitle.textContent = "Significant Improvements Needed";
            scoreTitle.style.color = "#ef4444";
        }

        // Display job match if available
        if (analysis.job_match) {
            this.displayJobMatch(analysis.job_match);
        } else {
            document.getElementById('jobMatchCard').style.display = 'none';
        }

        // Update lists
        this.updateList('strengthsList', analysis.strengths);
        this.updateList('improvementsList', analysis.improvements);
        this.updateList('recommendationsList', analysis.recommendations);

        // Update statistics
        this.updateStatistics(analysis.statistics);

        // Update sections
        this.updateSections(analysis.sections);

        // Show results section
        document.querySelector('.hero-section').scrollIntoView({ behavior: 'smooth' });
        this.resultsSection.style.display = 'block';
    }

    displayJobMatch(jobMatch) {
        const card = document.getElementById('jobMatchCard');
        const matchPercentage = document.getElementById('matchPercentage');
        const matchedSkillsList = document.getElementById('matchedSkillsList');
        const missingSkillsList = document.getElementById('missingSkillsList');

        if (!card || !matchPercentage || !matchedSkillsList || !missingSkillsList) {
            console.error('Job match elements not found');
            return;
        }

        card.style.display = 'block';
        matchPercentage.textContent = jobMatch.match_percentage + '%';

        // Display matched skills
        const matchedSkills = [...(jobMatch.matched_tech_skills || []), ...(jobMatch.matched_skills || [])];
        if (matchedSkills.length > 0) {
            matchedSkillsList.innerHTML = matchedSkills.slice(0, 10).map(skill => 
                `<span class="skill-badge skill-matched">${this.escapeHtml(skill)}</span>`
            ).join('');
        } else {
            matchedSkillsList.innerHTML = '<p class="text-muted">No matching skills found</p>';
        }

        // Display missing skills
        const missingSkills = [...(jobMatch.missing_tech_skills || []), ...(jobMatch.missing_skills || [])];
        if (missingSkills.length > 0) {
            missingSkillsList.innerHTML = missingSkills.slice(0, 10).map(skill => 
                `<span class="skill-badge skill-missing">${this.escapeHtml(skill)}</span>`
            ).join('');
        } else {
            missingSkillsList.innerHTML = '<p class="text-success">All required skills present!</p>';
        }
    }

    updateList(elementId, items) {
        const list = document.getElementById(elementId);
        if (!list) return;

        if (!items || items.length === 0) {
            list.innerHTML = '<li class="text-muted">No items to display</li>';
            return;
        }

        list.innerHTML = items.map(item => `<li>${this.escapeHtml(item)}</li>`).join('');
    }

    updateStatistics(stats) {
        const grid = document.getElementById('statisticsGrid');
        if (!grid) return;

        const statCards = [
            { label: 'Word Count', value: stats.word_count || 0 },
            { label: 'Character Count', value: stats.character_count || 0 },
            { label: 'Technical Skills', value: stats.technical_skills_count || 0 },
            { label: 'Action Verbs', value: stats.action_verbs_count || 0 },
            { label: 'Metrics Found', value: stats.metrics_count || 0 },
            { label: 'Soft Skills', value: stats.soft_skills_count || 0 },
            { label: 'Certifications', value: stats.certifications_count || 0 },
            { label: 'Line Count', value: stats.line_count || 0 }
        ];

        grid.innerHTML = statCards.map(stat => `
            <div class="stat-card">
                <div class="stat-label">${this.escapeHtml(stat.label)}</div>
                <div class="stat-value">${stat.value}</div>
            </div>
        `).join('');
    }

    updateSections(sections) {
        const grid = document.getElementById('sectionsGrid');
        if (!grid) return;

        if (!sections || Object.keys(sections).length === 0) {
            grid.innerHTML = '<p class="text-muted">No sections found</p>';
            return;
        }

        grid.innerHTML = Object.entries(sections).map(([name, found]) => `
            <div class="section-item ${found ? 'found' : 'not-found'}">
                ${found ? '✓' : '✗'} ${this.formatSectionName(name)}
            </div>
        `).join('');
    }

    formatSectionName(name) {
        return name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    downloadReport() {
        if (!this.currentAnalysis) {
            alert('No analysis available to download');
            return;
        }

        const analysis = this.currentAnalysis;
        let report = `RESUME ANALYSIS REPORT\n`;
        report += `${'='.repeat(60)}\n\n`;
        report += `Overall Score: ${analysis.overall_score}/100\n`;
        report += `${this.getScoreDescription(analysis.overall_score)}\n\n`;

        // Job Match section
        if (analysis.job_match) {
            report += `JOB MATCH ANALYSIS\n${'-'.repeat(60)}\n`;
            report += `Match Score: ${analysis.job_match.match_percentage}%\n`;
            report += `Matched Skills: ${(analysis.job_match.matched_tech_skills || []).join(', ') || 'None'}\n`;
            report += `Missing Skills: ${(analysis.job_match.missing_tech_skills || []).join(', ') || 'None'}\n\n`;
        }

        report += `STRENGTHS\n${'-'.repeat(60)}\n`;
        (analysis.strengths || []).forEach(s => report += `✓ ${s}\n`);

        report += `\nAREAS FOR IMPROVEMENT\n${'-'.repeat(60)}\n`;
        (analysis.improvements || []).forEach(i => report += `⚠ ${i}\n`);

        report += `\nRECOMMENDATIONS\n${'-'.repeat(60)}\n`;
        (analysis.recommendations || []).forEach(r => report += `💡 ${r}\n`);

        report += `\nSTATISTICS\n${'-'.repeat(60)}\n`;
        report += `Word Count: ${analysis.statistics?.word_count || 0}\n`;
        report += `Character Count: ${analysis.statistics?.character_count || 0}\n`;
        report += `Technical Skills: ${analysis.statistics?.technical_skills_count || 0}\n`;
        report += `Action Verbs: ${analysis.statistics?.action_verbs_count || 0}\n`;
        report += `Metrics Found: ${analysis.statistics?.metrics_count || 0}\n`;
        report += `Soft Skills: ${analysis.statistics?.soft_skills_count || 0}\n`;
        report += `Certifications: ${analysis.statistics?.certifications_count || 0}\n`;

        report += `\nRESUME SECTIONS FOUND\n${'-'.repeat(60)}\n`;
        Object.entries(analysis.sections || {}).forEach(([section, found]) => {
            report += `${found ? '✓' : '✗'} ${this.formatSectionName(section)}\n`;
        });

        report += `\n${'='.repeat(60)}\n`;
        report += `Generated: ${new Date().toLocaleString()}\n`;

        // Download
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(report));
        element.setAttribute('download', `resume_analysis_${new Date().getTime()}.txt`);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    reset() {
        this.fileInput.value = '';
        this.jobDescription.value = '';
        this.resumeFile = null;
        this.analyzeBtn.disabled = true;
        this.uploadBox.innerHTML = `
            <i class="fas fa-cloud-upload-alt"></i>
            <h5>Upload Your Resume</h5>
            <p>Drag and drop or click to select</p>
            <small>Supports: PDF, DOCX, DOC, TXT</small>
        `;
        this.resultsSection.style.display = 'none';
        document.querySelector('.hero-section').scrollIntoView({ behavior: 'smooth' });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        new ResumeAnalyzerApp();
    } catch (error) {
        console.error('Failed to initialize app:', error);
        alert('Error initializing app. Please refresh the page.');
    }
});
