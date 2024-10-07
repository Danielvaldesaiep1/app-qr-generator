document.getElementById('generateBtn').addEventListener('click', function() {
    const qrText = document.getElementById('qrText').value;

    if (!qrText) {
        alert('Por favor, introduce algún texto o URL.');
        return;
    }

    fetch('/generate_qr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ data: qrText })
    })
    .then(response => response.json())
    .then(data => {
        const qrImage = document.getElementById('qrImage');
        qrImage.src = 'data:image/png;base64,' + data.img;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});