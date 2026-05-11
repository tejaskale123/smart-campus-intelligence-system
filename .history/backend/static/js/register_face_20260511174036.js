// ================================
// SMART AI FACE REGISTER JS
// ================================

const video =
document.getElementById("video");

const captureBtn =
document.getElementById("captureBtn");

const registerBtn =
document.getElementById("registerBtn");

const imageCount =
document.getElementById("imageCount");

const progressFill =
document.getElementById("progressFill");

const previewContainer =
document.getElementById("previewContainer");

const statusBox =
document.getElementById("statusBox");

const studentName =
document.getElementById("student_name");

const rollNumber =
document.getElementById("roll_number");

const course =
document.getElementById("course");


// ========================================
// IMAGE STORAGE
// ========================================

let capturedImages = [];


// ========================================
// START CAMERA
// ========================================

navigator.mediaDevices
.getUserMedia({

    video:{

        width:1280,
        height:720,
        facingMode:"user"

    },

    audio:false

})

.then(function(stream){

    video.srcObject = stream;

})

.catch(function(error){

    console.log(error);

    alert(
        "Camera Access Failed"
    );

});



// ========================================
// CAPTURE IMAGE
// ========================================

function captureFace(){

    if(capturedImages.length >= 5){

        alert(
            "Only 5 Images Allowed"
        );

        return;
    }

    const canvas =
    document.createElement("canvas");

    canvas.width =
    video.videoWidth;

    canvas.height =
    video.videoHeight;

    const ctx =
    canvas.getContext("2d");

    ctx.drawImage(

        video,
        0,
        0,
        canvas.width,
        canvas.height

    );

    const imageData =
    canvas.toDataURL(
        "image/jpeg",
        0.9
    );



    // SAVE IMAGE
    capturedImages.push(imageData);



    // ========================================
    // UPDATE COUNT
    // ========================================

    imageCount.innerText =
    capturedImages.length +
    " / 5 Images Captured";



    // ========================================
    // UPDATE PROGRESS BAR
    // ========================================

    progressFill.style.width =
    (capturedImages.length * 20) + "%";



    // ========================================
    // IMAGE PREVIEW
    // ========================================

    const img =
    document.createElement("img");

    img.src = imageData;

    img.style.width = "90px";

    img.style.height = "90px";

    img.style.objectFit = "cover";

    img.style.borderRadius = "12px";

    img.style.margin = "6px";

    img.style.border =
    "2px solid #22d3ee";

    previewContainer.appendChild(img);




    // ========================================
    // STATUS MESSAGE
    // ========================================

    statusBox.innerHTML =
    "✅ Image " +
    capturedImages.length +
    " Captured";



    if(capturedImages.length === 5){

        statusBox.innerHTML =
        "🚀 All 5 Images Captured Successfully";

    }

}



// ========================================
// REGISTER STUDENT
// ========================================

async function registerStudent(){


    // ========================================
    // VALIDATION
    // ========================================

    if(studentName.value.trim() === ""){

        alert(
            "Enter Student Name"
        );

        return;
    }


    if(rollNumber.value.trim() === ""){

        alert(
            "Enter Roll Number"
        );

        return;
    }


    if(course.value.trim() === ""){

        alert(
            "Enter Course"
        );

        return;
    }



    if(capturedImages.length < 5){

        alert(
            "Capture 5 Images First"
        );

        return;
    }



    // ========================================
    // FORM DATA
    // ========================================

    const formData =
    new FormData();

    formData.append(
        "student_name",
        studentName.value
    );

    formData.append(
        "roll_number",
        rollNumber.value
    );

    formData.append(
        "course",
        course.value
    );



    // ========================================
    // APPEND IMAGES
    // ========================================

    capturedImages.forEach(function(img){

        formData.append(
            "images[]",
            img
        );

    });




    // ========================================
    // SEND DATA TO DJANGO
    // ========================================

    try{

        const response =
        await fetch(

            "/register-face/",

            {

                method:"POST",

                body:formData,

                headers:{

                    "X-CSRFToken":
                    getCookie("csrftoken")

                }

            }

        );



        const data =
        await response.json();




        // ========================================
        // SUCCESS
        // ========================================

        if(data.status === "success"){

            alert(
                "Student Registered Successfully"
            );

            statusBox.innerHTML =
            "✅ Registration Completed";



            // RESET ALL
            capturedImages = [];

            imageCount.innerText =
            "0 / 5 Images Captured";

            progressFill.style.width =
            "0%";

            previewContainer.innerHTML =
            "";

            studentName.value = "";

            rollNumber.value = "";

            course.value = "";

        }

        else{

            alert(data.message);

        }

    }

    catch(error){

        console.log(error);

        alert(
            "Registration Failed"
        );

    }

}



// ========================================
// GET CSRF TOKEN
// ========================================

function getCookie(name){

    let cookieValue = null;

    if(document.cookie &&
       document.cookie !== ""){

        const cookies =
        document.cookie.split(";");

        for(let i = 0;
            i < cookies.length;
            i++){

            const cookie =
            cookies[i].trim();

            if(

                cookie.substring(
                    0,
                    name.length + 1

                ) === (name + "=")

            ){

                cookieValue =
                decodeURIComponent(

                    cookie.substring(
                        name.length + 1
                    )

                );

                break;
            }

        }

    }

    return cookieValue;

}



// ========================================
// BUTTON EVENTS
// ========================================

captureBtn.addEventListener(

    "click",

    captureFace

);


registerBtn.addEventListener(

    "click",

    registerStudent

);