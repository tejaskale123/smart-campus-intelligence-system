let video = document.getElementById("video");
let canvas = document.getElementById("canvas");
let captureBtn = document.getElementById("captureBtn");
let imageCount = document.getElementById("imageCount");

let capturedImages = 0;

navigator.mediaDevices.getUserMedia({
    video: true
})
.then(function(stream){

    video.srcObject = stream;

})
.catch(function(error){

    alert("Camera access denied");

});

captureBtn.addEventListener("click", function(){

    if(capturedImages >= 5){

        alert("5 Images Already Captured");
        return;
    }

    let context = canvas.getContext("2d");

    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    capturedImages++;

    imageCount.innerText =
        capturedImages + " / 5 Images Captured";

    if(capturedImages === 5){

        alert("Registration Images Completed");

    }

});