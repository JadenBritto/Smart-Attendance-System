/**
 * Attendance taking with periodic face recognition.
 */
(function () {
    const video = document.getElementById('webcam');
    const overlay = document.getElementById('overlay');
    const startBtn = document.getElementById('startCamera');
    const toggleBtn = document.getElementById('toggleScanning');
    const statusEl = document.getElementById('scan-status');
    const studentListEl = document.getElementById('studentList');
    const presentCountEl = document.getElementById('presentCount');
    const totalCountEl = document.getElementById('totalCount');
    const progressBar = document.getElementById('progressBar');

    if (!video || !startBtn || typeof sessionId === 'undefined') return;

    let stream = null;
    let scanning = false;
    let scanInterval = null;
    let students = studentsData || [];

    // Initial render
    renderStudents();
    updateCounts();

    startBtn.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: 'user' }
            });
            video.srcObject = stream;
            startBtn.classList.add('hidden');
            toggleBtn.classList.remove('hidden');
            statusEl.textContent = 'Camera ready. Click "Start Scanning" to begin.';
        } catch (err) {
            statusEl.textContent = 'Could not access camera: ' + err.message;
            statusEl.className = 'text-sm text-red-600';
        }
    });

    toggleBtn.addEventListener('click', () => {
        if (scanning) {
            stopScanning();
        } else {
            startScanning();
        }
    });

    function startScanning() {
        scanning = true;
        toggleBtn.textContent = 'Stop Scanning';
        toggleBtn.className = 'bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition text-sm';
        statusEl.textContent = 'Scanning...';
        statusEl.className = 'text-sm text-green-600';
        scanFrame();
        scanInterval = setInterval(scanFrame, 3000);
    }

    function stopScanning() {
        scanning = false;
        clearInterval(scanInterval);
        toggleBtn.textContent = 'Start Scanning';
        toggleBtn.className = 'bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition text-sm';
        statusEl.textContent = 'Scanning paused.';
        statusEl.className = 'text-sm text-gray-500';

        // Clear overlay
        if (overlay) {
            const ctx = overlay.getContext('2d');
            ctx.clearRect(0, 0, overlay.width, overlay.height);
        }
    }

    async function scanFrame() {
        if (!scanning || !stream) return;

        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg', 0.8);

        try {
            const response = await fetch('/attendance/api/recognize/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ session_id: sessionId, image: imageData }),
            });

            const result = await response.json();

            if (result.error) {
                statusEl.textContent = 'Error: ' + result.error;
                statusEl.className = 'text-sm text-red-600';
                return;
            }

            // Draw face boxes
            drawFaceBoxes(result.recognized || []);

            // Update student list
            if (result.students) {
                students = result.students;
                renderStudents();
                updateCounts();
            }

            statusEl.textContent = `Scanning... (${result.face_count || 0} face${result.face_count !== 1 ? 's' : ''} detected)`;
            statusEl.className = 'text-sm text-green-600';

        } catch (err) {
            statusEl.textContent = 'Connection error. Retrying...';
            statusEl.className = 'text-sm text-yellow-600';
        }
    }

    function drawFaceBoxes(faces) {
        if (!overlay) return;
        const ctx = overlay.getContext('2d');
        overlay.width = video.videoWidth;
        overlay.height = video.videoHeight;
        ctx.clearRect(0, 0, overlay.width, overlay.height);

        faces.forEach(face => {
            const loc = face.location;
            if (!loc) return;

            const isKnown = face.name && face.name !== 'Unknown';
            ctx.strokeStyle = isKnown ? '#22c55e' : '#ef4444';
            ctx.lineWidth = 3;
            ctx.strokeRect(loc.left, loc.top, loc.right - loc.left, loc.bottom - loc.top);

            // Name label
            const label = face.name || 'Unknown';
            ctx.font = '14px sans-serif';
            const textWidth = ctx.measureText(label).width;
            ctx.fillStyle = isKnown ? '#22c55e' : '#ef4444';
            ctx.fillRect(loc.left, loc.top - 22, textWidth + 10, 22);
            ctx.fillStyle = '#ffffff';
            ctx.fillText(label, loc.left + 5, loc.top - 6);
        });
    }

    function renderStudents() {
        if (!studentListEl) return;
        studentListEl.innerHTML = '';

        // Sort: present first, then by roll number
        const sorted = [...students].sort((a, b) => {
            if (a.status === 'present' && b.status !== 'present') return -1;
            if (a.status !== 'present' && b.status === 'present') return 1;
            return a.roll_number.localeCompare(b.roll_number);
        });

        sorted.forEach(s => {
            const isPresent = s.status === 'present';
            const div = document.createElement('div');
            div.className = `flex items-center justify-between p-2 rounded-lg text-sm ${isPresent ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'}`;
            div.innerHTML = `
                <div class="flex items-center space-x-2">
                    <div class="w-2 h-2 rounded-full ${isPresent ? 'bg-green-500' : 'bg-gray-400'}"></div>
                    <span class="font-medium ${isPresent ? 'text-green-800' : 'text-gray-600'}">${s.roll_number}</span>
                    <span class="${isPresent ? 'text-green-700' : 'text-gray-500'}">${s.name}</span>
                </div>
                <span class="text-xs font-medium ${isPresent ? 'text-green-600' : 'text-gray-400'}">${isPresent ? 'Present' : 'Absent'}</span>
            `;
            studentListEl.appendChild(div);
        });
    }

    function updateCounts() {
        const present = students.filter(s => s.status === 'present').length;
        const total = students.length;
        if (presentCountEl) presentCountEl.textContent = present;
        if (totalCountEl) totalCountEl.textContent = total;
        if (progressBar) {
            const pct = total > 0 ? (present / total * 100) : 0;
            progressBar.style.width = pct + '%';
        }
    }
})();
