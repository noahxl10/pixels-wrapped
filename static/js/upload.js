document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('media-files');
    const progressBar = document.getElementById('upload-progress');
    const progressBarInner = progressBar.querySelector('.progress-bar');
    const previewGrid = document.getElementById('preview-grid');

    fileInput.addEventListener('change', function(e) {
        previewGrid.innerHTML = '';
        const files = Array.from(e.target.files);

        files.forEach(file => {
            const reader = new FileReader();
            const previewCol = document.createElement('div');
            previewCol.className = 'col-md-4 col-sm-6';

            const previewCard = document.createElement('div');
            previewCard.className = 'card h-100';

            if (file.type.startsWith('image/')) {
                reader.onload = function(e) {
                    previewCard.innerHTML = `
                        <img src="${e.target.result}" class="card-img-top" alt="Preview">
                        <div class="card-body">
                            <p class="card-text">${file.name}</p>
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            } else if (file.type.startsWith('video/')) {
                previewCard.innerHTML = `
                    <div class="card-body">
                        <i data-feather="video" class="w-100 h-100"></i>
                        <p class="card-text">${file.name}</p>
                    </div>
                `;
                feather.replace();
            }

            previewCol.appendChild(previewCard);
            previewGrid.appendChild(previewCol);
        });
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        progressBar.classList.remove('d-none');
        
        fetch('/upload', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect;
            } else {
                alert('Upload failed: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during upload');
        })
        .finally(() => {
            progressBar.classList.add('d-none');
            progressBarInner.style.width = '0%';
        });
    });
});
