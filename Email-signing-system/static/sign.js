let canvas = document.getElementById("sig");
let ctx = canvas.getContext("2d");
let drawing = false;

canvas.onmousedown = (e) => {
    drawing = true;
    ctx.beginPath();                     // ← start a new stroke
    ctx.moveTo(e.offsetX, e.offsetY);    // ← move to the starting point
};

canvas.onmouseup = () => drawing = false;

canvas.onmousemove = draw;

function draw(e) {
    if (!drawing) return;

    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.strokeStyle = "black";

    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.stroke();
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function submitSignature() {
    document.getElementById("loadingSpinner").style.display = "flex";

    let dataURL = canvas.toDataURL("image/png");
    document.getElementById("signatureInput").value = dataURL;
    document.getElementById("sigForm").submit();
}