lass ResumeAnalyzerApp {
    constructor() {
        this.uploadBox = document.getElementById('uploadBox');
        this.fileInput = document.getElementById('fileInput');
        this.resultsSection = document.getElementById('resultsSection');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.resetBtn = document.getElementById('resetBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.tryDemoBtn = document.getElementById('tryDemoBtn');
        this.currentAnalysis = null;

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Upload box
        this.uploadBox.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag and drop
        this.uploadBox.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadBox.addEventListener('dragleave', () => this.handleDragLeave());
        this.uploadBox.addEventListener('drop', (e) => this.handleDrop(e));

        // Action buttons
        this.resetBtn.addEventListener('click', () => this.reset());
        this.downloadBtn.addEventListener('click', () => this.downloadReport());
        this.tryDemoBtn.addEventListener('click', () => this.loadDemo());
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadBox.classList.add('dragover');
    }

    handleDragLeave() {
        this.uploadBox.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
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
        const validTypes = ['application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];

        if (!validTypes.includes(file.type)) {
            alert('Please upload a valid file (PDF, DOCX, DOC, or TXT)');
            return;
        }

        this.analyzeResume(file);
    }

    analyzeResume(file) {
        const formData = new FormData();
        formData.append('file', file);

        this.loadingSpinner.style.display = 'flex';

        fetch('/api/analyze', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
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
                alert('Error analyzing resume: ' + error);
            });
    }

    loadDemo() {
        this.loadingSpinner.style.display = 'flex';

        fetch('/api/sample-analysis')
            .then(response => response.json())
            .then(data => {
                this.loadingSpinner.style.display = 'none';
                this.displayResults(data);
            })
            .catch(error => {
                this.loadingSpinner.style.display = 'none';
                alert('Error loading demo: ' + error);
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

    updateList(elementId, items) {
        const list = document.getElementById(elementId);
        list.innerHTML = items.map(item => `<li>${item}</li>`).join('');
    }

    updateStatistics(stats) {
        const grid = document.getElementById('statisticsGrid');
        const statCards = [
            { label: 'Word Count', value: stats.word_count },
            { label: 'Character Count', value: stats.character_count },
            { label: 'Technical Skills', value: stats.technical_skills_count },
            { label: 'Action Verbs', value: stats.action_verbs_count },
            { label: 'Metrics Found', value: stats.metrics_count },
            { label: 'Soft Skills', value: stats.soft_skills_count },
            { label: 'Certifications', value: stats.certifications_count },
            { label: 'Line Count', value: stats.line_count }
        ];

        grid.innerHTML = statCards.map(stat => `
            <div class="stat-card">
                <div class="stat-label">${stat.label}</div>
                <div class="stat-value">${stat.value}</div>
            </div>
        `).join('');
    }

    updateSections(sections) {
        const grid = document.getElementById('sectionsGrid');
        grid.innerHTML = Object.entries(sections).map(([name, found]) => `
            <div class="section-item ${found ? 'found' : 'not-found'}">
                ${found ? '✓' : '✗'} ${this.formatSectionName(name)}
            </div>
        `).join('');
    }

    formatSectionName(name) {
        return name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    downloadReport() {
        const analysis = this.currentAnalysis;
        let report = `RESUME ANALYSIS REPORT\n`;
        report += `${'='.repeat(60)}\n\n`;
        report += `Overall Score: ${analysis.overall_score}/100\n`;
        report += `${this.getScoreDescription(analysis.overall_score)}\n\n`;

        report += `STRENGTHS\n${'-'.repeat(60)}\n`;
        analysis.strengths.forEach(s => report += `✓ ${s}\n`);

        report += `\nAREAS FOR IMPROVEMENT\n${'-'.repeat(60)}\n`;
        analysis.improvements.forEach(i => report += `⚠ ${i}\n`);

        report += `\nRECOMMENDATIONS\n${'-'.repeat(60)}\n`;
        analysis.recommendations.forEach(r => report += `💡 ${r}\n`);

        report += `\nSTATISTICS\n${'-'.repeat(60)}\n`;
        report += `Word Count: ${analysis.statistics.word_count}\n`;
        report += `Character Count: ${analysis.statistics.character_count}\n`;
        report += `Technical Skills: ${analysis.statistics.technical_skills_count}\n`;
        report += `Action Verbs: ${analysis.statistics.action_verbs_count}\n`;
        report += `Metrics Found: ${analysis.statistics.metrics_count}\n`;
        report += `Soft Skills: ${analysis.statistics.soft_skills_count}\n`;
        report += `Certifications: ${analysis.statistics.certifications_count}\n`;

        report += `\nRESUME SECTIONS FOUND\n${'-'.repeat(60)}\n`;
        Object.entries(analysis.sections).forEach(([section, found]) => {
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
        this.resultsSection.style.display = 'none';
        document.querySelector('.hero-section').scrollIntoView({ behavior: 'smooth' });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ResumeAnalyzerApp();
});
