// Configurazione API
const API_URL = 'http://localhost:8000';

// Elementi DOM
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadBox = document.getElementById('uploadBox');
const uploadSection = document.getElementById('uploadSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const newUploadBtn = document.getElementById('newUploadBtn');
const summaryBox = document.getElementById('summaryBox');
const extractedText = document.getElementById('extractedText');
const fileName = document.getElementById('fileName');
const textLength = document.getElementById('textLength');

// Event Listeners
uploadBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
newUploadBtn.addEventListener('click', resetUpload);

// Drag & Drop
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('dragover');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('dragover');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

uploadBox.addEventListener('click', (e) => {
    if (e.target !== uploadBtn) {
        fileInput.click();
    }
});

// Funzioni
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // Validazione file
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Per favore seleziona un file PDF valido');
        return;
    }

    const maxSize = 10 * 1024 * 1024; // 10 MB
    if (file.size > maxSize) {
        showError('Il file supera la dimensione massima di 10 MB');
        return;
    }

    uploadPDF(file);
}

async function uploadPDF(file) {
    // Mostra loading
    uploadSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_URL}/api/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Errore durante l\'upload');
        }

        // Mostra risultati
        displayResults(data);
    } catch (error) {
        console.error('Errore:', error);
        showError(error.message || 'Si è verificato un errore. Riprova.');
        resetUpload();
    }
}

function displayResults(data) {
    loadingSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    fileName.textContent = data.filename;
    summaryBox.textContent = data.summary;
    extractedText.textContent = data.extracted_text;
    textLength.textContent = `${data.text_length.toLocaleString()} caratteri`;
}

function resetUpload() {
    fileInput.value = '';
    uploadSection.classList.remove('hidden');
    loadingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
}

function showError(message) {
    alert(message);
}