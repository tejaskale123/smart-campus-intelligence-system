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