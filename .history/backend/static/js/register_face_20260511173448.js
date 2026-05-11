const video = document.getElementById("video");

navigator.mediaDevices
.getUserMedia({

    video:{

        width:1280,
        height:720

    }

})

.then(function(stream){

    video.srcObject = stream;

})

.catch(function(error){

    console.log(error);

});

<script>

let capturedImages = [];

const video = document.getElementById("video");

navigator.mediaDevices.getUserMedia({
    video: true
})
.then(stream => {
    video.srcObject = stream;
});

function captureFace() {

    if (capturedImages.length >= 5) {
        alert("5 Images Already Captured");
        return;
    }

    const canvas = document.createElement("canvas");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    const imageData = canvas.toDataURL("image/jpeg");

    capturedImages.push(imageData);

    document.getElementById(
        "capture-count"
    ).innerText =
        capturedImages.length + "/5 Images Captured";
}

async function registerStudent() {

    const studentName =
        document.getElementById("student_name").value;

    const rollNumber =
        document.getElementById("roll_number").value;

    const course =
        document.getElementById("course").value;

    if (capturedImages.length < 5) {

        alert("Capture 5 Images First");
        return;
    }

    const formData = new FormData();

    formData.append(
        "student_name",
        studentName
    );

    formData.append(
        "roll_number",
        rollNumber
    );

    formData.append(
        "course",
        course
    );

    capturedImages.forEach(img => {
        formData.append("images[]", img);
    });

    const response = await fetch(
        "/register-face/",
        {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken":
                    "{{ csrf_token }}"
            }
        }
    );

    const data = await response.json();

    alert(data.message);

    location.reload();
}

</script>