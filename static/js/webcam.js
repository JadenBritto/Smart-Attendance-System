/**
 * Webcam capture and photo upload for student face registration.
 */
(function () {
    const video = document.getElementById('webcam');
    const overlay = document.getElementById('overlay');
    const startBtn = document.getElementById('startCamera');
    const captureBtn = document.getElementById('captureBtn');
    const statusEl = document.getElementById('capture-status');
    const previewEl = document.getElementById('captured-preview');
    const previewImg = document.getElementById('previewImg');
    const photoInput = document.getElementById('photo_data');
    const encodingInput = document.getElementById('encoding_data');

    // Mode toggle elements
    const modeWebcamBtn = document.getElementById('modeWebcam');
    const modeUploadBtn = document.getElementById('modeUpload');
    const webcamSection = document.getElementById('webcam-section');
    const uploadSection = document.getElementById('upload-section');

    // Upload elements
    const photoUpload = document.getElementById('photoUpload');
    const dropZone = document.getElementById('dropZone');
    const uploadPreview = document.getElementById('upload-preview');
    const uploadPreviewImg = document.getElementById('uploadPreviewImg');
    const detectUploadBtn = document.getElementById('detectUploadBtn');

    if (!statusEl) return;

    let stream = null;
    let uploadedImageData = null;

    // --- Mode Switching ---
    if (modeWebcamBtn && modeUploadBtn) {
        modeWebcamBtn.addEventListener('click', () => {
            modeWebcamBtn.className = 'flex-1 px-4 py-2 text-sm font-medium bg-blue-600 text-white transition';
            modeUploadBtn.className = 'flex-1 px-4 py-2 text-sm font-medium bg-white text-gray-700 hover:bg-gray-50 transition';
            webcamSection.classList.remove('hidden');
            uploadSection.classList.add('hidden');
        });

        modeUploadBtn.addEventListener('click', () => {
            modeUploadBtn.className = 'flex-1 px-4 py-2 text-sm font-medium bg-blue-600 text-white transition';
            modeWebcamBtn.className = 'flex-1 px-4 py-2 text-sm font-medium bg-white text-gray-700 hover:bg-gray-50 transition';
            uploadSection.classList.remove('hidden');
            webcamSection.classList.add('hidden');
        });
    }

    // --- Webcam ---
    if (startBtn) {
        startBtn.addEventListener('click', async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 640, height: 480, facingMode: 'user' }
                });
                video.srcObject = stream;
                startBtn.classList.add('hidden');
                captureBtn.classList.remove('hidden');
                statusEl.textContent = 'Camera active. Position your face and click "Capture Face".';
                statusEl.className = 'mt-3 text-sm text-green-600';
            } catch (err) {
                statusEl.textContent = 'Could not access camera: ' + err.message;
                statusEl.className = 'mt-3 text-sm text-red-600';
            }
        });
    }

    if (captureBtn) {
        captureBtn.addEventListener('click', async () => {
            if (!stream) return;
            await detectAndSave(captureWebcamFrame());
        });
    }

    function captureWebcamFrame() {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        return canvas.toDataURL('image/jpeg', 0.9);
    }

    // --- File Upload ---
    if (photoUpload) {
        photoUpload.addEventListener('change', (e) => {
            handleFile(e.target.files[0]);
        });
    }

    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-blue-500', 'bg-blue-50');
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-blue-500', 'bg-blue-50');
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-blue-500', 'bg-blue-50');
            if (e.dataTransfer.files.length) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    function handleFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            statusEl.textContent = 'Please select a valid image file.';
            statusEl.className = 'mt-3 text-sm text-red-600';
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            statusEl.textContent = 'File too large. Max 5MB.';
            statusEl.className = 'mt-3 text-sm text-red-600';
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedImageData = e.target.result;
            uploadPreviewImg.src = uploadedImageData;
            uploadPreview.classList.remove('hidden');
            detectUploadBtn.classList.remove('hidden');
            statusEl.textContent = 'Photo loaded. Click "Detect Face in Photo" to process.';
            statusEl.className = 'mt-3 text-sm text-blue-600';
        };
        reader.readAsDataURL(file);
    }

    if (detectUploadBtn) {
        detectUploadBtn.addEventListener('click', async () => {
            if (!uploadedImageData) return;
            await detectAndSave(uploadedImageData);
        });
    }

    // --- Shared face detection logic ---
    async function detectAndSave(imageData) {
        statusEl.textContent = 'Detecting face...';
        statusEl.className = 'mt-3 text-sm text-blue-600';

        if (captureBtn) {
            captureBtn.disabled = true;
            captureBtn.textContent = 'Processing...';
        }
        if (detectUploadBtn) {
            detectUploadBtn.disabled = true;
            detectUploadBtn.textContent = 'Processing...';
        }

        try {
            const response = await fetch('/students/api/detect-face/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ image: imageData }),
            });

            const result = await response.json();

            if (result.detected) {
                photoInput.value = imageData;
                encodingInput.value = JSON.stringify(result.encoding);

                // Show preview
                previewImg.src = imageData;
                previewEl.classList.remove('hidden');

                // Draw face box on webcam overlay if in webcam mode
                if (overlay && stream) {
                    const octx = overlay.getContext('2d');
                    overlay.width = video.videoWidth;
                    overlay.height = video.videoHeight;
                    octx.clearRect(0, 0, overlay.width, overlay.height);
                    const loc = result.location;
                    octx.strokeStyle = '#22c55e';
                    octx.lineWidth = 3;
                    octx.strokeRect(loc.left, loc.top, loc.right - loc.left, loc.bottom - loc.top);
                }

                statusEl.textContent = 'Face captured successfully! You can submit the form.';
                statusEl.className = 'mt-3 text-sm text-green-600 font-medium';
            } else {
                statusEl.textContent = result.message || 'No face detected. Please try again.';
                statusEl.className = 'mt-3 text-sm text-yellow-600';
            }
        } catch (err) {
            statusEl.textContent = 'Error: ' + err.message;
            statusEl.className = 'mt-3 text-sm text-red-600';
        }

        if (captureBtn) {
            captureBtn.disabled = false;
            captureBtn.textContent = 'Capture Face';
        }
        if (detectUploadBtn) {
            detectUploadBtn.disabled = false;
            detectUploadBtn.textContent = 'Detect Face in Photo';
        }
    }
})();
