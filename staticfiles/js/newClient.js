// JavaScript code for capturing picture
    const camera = document.getElementById('camera');
    const captureBtn = document.getElementById('captureBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const pictureInput = document.getElementById('pictureInput');
    const pictureContainer = document.getElementById('pictureContainer');
    const displayPicture = document.getElementById('displayPicture');
    const capturedImage = document.getElementById('capturedImage');

    // Check if camera is supported
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                camera.srcObject = stream;
            })
            .catch(function (error) {
                console.error('Error accessing camera:', error);
            });
    }

    // Capture picture from camera
    captureBtn.addEventListener('click', function () {
        const canvas = document.createElement('canvas');
        canvas.width = camera.videoWidth;
        canvas.height = camera.videoHeight;
        canvas.getContext('2d').drawImage(camera, 0, 0, canvas.width, canvas.height);
        const picture = canvas.toDataURL('image/jpeg');  // Convert image to JPEG format
        pictureInput.value = picture;
        capturedImage.src = picture;
        pictureContainer.style.display = 'none';
        displayPicture.style.display = 'block';
        canvas.remove();
    });


    // Cancel captured picture
    cancelBtn.addEventListener('click', function () {
        pictureInput.value = '';
        capturedImage.src = '';
        pictureContainer.style.display = 'block';
        displayPicture.style.display = 'none';
    });