/**
 * JobBoost Main JavaScript
 * Resume upload, analysis, and interview functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const optionsSection = document.getElementById('options-section');
    const analyzeBtn = document.getElementById('analyze-btn');
    const targetPosition = document.getElementById('target-position');
    const jobDescription = document.getElementById('job-description');

    if (!dropzone) return; // Not on the upload page

    let uploadedFile = null;
    let fileData = null;

    // ─── Drag & Drop ───
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFile(files[0]);
    });

    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    // ─── File Handler ───
    async function handleFile(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'docx'].includes(ext)) {
            alert('仅支持 PDF 和 DOCX 格式');
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            alert('文件过大，最大支持 5MB');
            return;
        }

        uploadedFile = file;
        fileName.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        fileName.classList.remove('hidden');
        dropzone.querySelector('p:first-of-type').textContent = '文件已选择';
        optionsSection.classList.remove('hidden');
        checkReady();
    }

    // ─── Check Ready ───
    function checkReady() {
        analyzeBtn.disabled = !uploadedFile;
    }

    // ─── Upload & Analyze ───
    analyzeBtn.addEventListener('click', async () => {
        if (!uploadedFile) return;

        // Show loading
        document.getElementById('btn-text').classList.add('hidden');
        document.getElementById('btn-loading').classList.remove('hidden');
        analyzeBtn.disabled = true;

        try {
            // Step 1: Upload
            const uploadFormData = new FormData();
            uploadFormData.append('file', uploadedFile);

            const uploadRes = await fetch('/api/resume/upload', {
                method: 'POST',
                body: uploadFormData
            });

            if (!uploadRes.ok) {
                const err = await uploadRes.json();
                throw new Error(err.detail || '上传失败');
            }

            fileData = await uploadRes.json();

            // Step 2: Analyze
            const pos = targetPosition?.value || '';
            const jd = jobDescription?.value || '';

            const analyzeRes = await fetch('/api/resume/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    resume_text: fileData.raw_text,
                    job_description: jd,
                    target_position: pos,
                    language: '中文'
                })
            });

            if (!analyzeRes.ok) {
                const err = await analyzeRes.json();
                throw new Error(err.detail || '分析失败');
            }

            const analysisData = await analyzeRes.json();
            analysisData.raw_text = fileData.raw_text;

            // Save to sessionStorage and navigate
            sessionStorage.setItem('jobboost_analysis', JSON.stringify(analysisData));
            sessionStorage.setItem('jobboost_resume_text', fileData.raw_text);
            window.location.href = '/result';

        } catch (error) {
            alert('分析失败：' + error.message);
            document.getElementById('btn-text').classList.remove('hidden');
            document.getElementById('btn-loading').classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });
});
