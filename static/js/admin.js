let utilizationChart = null;

function showMessage(message, type = 'info') {
    const messageArea = document.getElementById('messageArea');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    messageArea.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function uploadStudents() {
    const fileInput = document.getElementById('studentFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('Please select a file', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showMessage('Uploading students...', 'info');
    
    fetch('/api/upload_students', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            fileInput.value = '';
            setTimeout(() => location.reload(), 1500);
        } else {
            showMessage(data.message, 'danger');
        }
    })
    .catch(error => {
        showMessage('Error uploading file: ' + error.message, 'danger');
    });
}

function uploadRooms() {
    const fileInput = document.getElementById('roomFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('Please select a file', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showMessage('Uploading rooms...', 'info');
    
    fetch('/api/upload_rooms', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            fileInput.value = '';
            setTimeout(() => location.reload(), 1500);
        } else {
            showMessage(data.message, 'danger');
        }
    })
    .catch(error => {
        showMessage('Error uploading file: ' + error.message, 'danger');
    });
}

function generateAllocation() {
    const method = document.getElementById('allocationMethod').value;
    
    if (!confirm(`Generate seating plan using ${method} method? This will clear existing allocations.`)) {
        return;
    }
    
    showMessage('Generating seating plan...', 'info');
    
    fetch('/api/allocate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ method: method })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showMessage(data.message, 'danger');
        }
    })
    .catch(error => {
        showMessage('Error generating allocation: ' + error.message, 'danger');
    });
}

function generateAdmitCards() {
    showMessage('Generating admit cards...', 'info');
    
    fetch('/api/generate_admit_cards', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
        } else {
            showMessage(data.message, 'danger');
        }
    })
    .catch(error => {
        showMessage('Error generating admit cards: ' + error.message, 'danger');
    });
}

function exportExcel() {
    window.location.href = '/api/export_excel';
}

function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const stats = data.stats;
                
                if (stats.total_capacity > 0) {
                    const utilization = Math.round((stats.allocations / stats.total_capacity) * 100);
                    document.getElementById('utilization').textContent = utilization + '%';
                }
                
                if (stats.room_utilization && stats.room_utilization.length > 0) {
                    drawUtilizationChart(stats.room_utilization);
                }
            }
        })
        .catch(error => {
            console.error('Error loading stats:', error);
        });
}

function drawUtilizationChart(roomData) {
    const ctx = document.getElementById('utilizationChart');
    
    if (!ctx) return;
    
    if (utilizationChart) {
        utilizationChart.destroy();
    }
    
    const labels = roomData.map(r => r.room_no);
    const percentages = roomData.map(r => r.percentage);
    
    utilizationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Utilization %',
                data: percentages,
                backgroundColor: 'rgba(13, 110, 253, 0.7)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    loadStats();
});
