from flask import Flask, render_template_string, send_file
import qrcode
import io

app = Flask(__name__)

UPI_ID = "naqviimidhat@okaxis"
UPI_NAME = "Midhat Naqvi"
PRICE = "2.00"
UPI_LINK = f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={PRICE}&cu=INR&tn=Photo Booth Strip"

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Midhat's Photo Booth</title>
<style>
  :root { --ink: #28251f; --sage: #687866; --cream: #fbf7ef; }
    * { box-sizing: border-box; }
  body { margin: 0; min-height: 100vh; padding: 28px 16px 50px; color: var(--ink);
    background: radial-gradient(ellipse at 10% 8%, #f6e2e5 0, transparent 28%),
      radial-gradient(ellipse at 90% 80%, #e4eadf 0, transparent 28%), var(--cream);
    font-family: Georgia, "Times New Roman", serif; }
  main { width: min(100%, 980px); margin: auto; }
  header { text-align: center; margin-bottom: 24px; }
  .eyebrow { color: var(--sage); font: 700 12px/1.5 Arial, sans-serif; letter-spacing: .24em; text-transform: uppercase; }
  h1 { margin: 8px 0; font-size: clamp(30px, 6vw, 52px); }
  header p { color: #706b63; }
  .layout { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(260px, .85fr); gap: 22px; align-items: start; }
  .card { padding: 18px; background: #fffdf9; border: 1px solid #e9e1d6; border-radius: 20px; box-shadow: 0 12px 35px #473a2712; }
  .video-wrap { position: relative; border-radius: 14px; overflow: hidden; background: #26231f; }
  video { display: none; }
  #live { display: block; width: 100%; aspect-ratio: 4 / 3; object-fit: cover; background: #26231f; border-radius: 14px; }
  .controls { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px; }
  label { display: block; margin: 14px 0 6px; color: #625c53; font: 700 13px Arial, sans-serif; }
  select, button { width: 100%; padding: 12px; border: 1px solid #ded5ca; border-radius: 10px; background: white; color: var(--ink); font: 600 14px Arial, sans-serif; }
  button { cursor: pointer; }
  button.primary { border-color: var(--sage); background: var(--sage); color: white; }
  #status { min-height: 20px; margin: 12px 0 0; color: var(--sage); font: 13px Arial, sans-serif; }
  .pay-msg { margin: 0 0 12px; padding: 10px 12px; background: #fff3cd; border: 1px solid #f0d98c; border-radius: 10px; color: #7a5b00; font: 700 13px/1.4 Arial, sans-serif; text-align: center; }
  .strip-preview { display: flex; justify-content: center; padding: 15px; border-radius: 14px; background: #f0ece5; }
  #strip { width: min(100%, 230px); height: auto; border-radius: 3px; box-shadow: 0 8px 20px #0002; }
  .qr { margin-top: 18px; padding-top: 14px; border-top: 1px solid #e9e1d6; text-align: center; font: 13px Arial, sans-serif; }
  .qr img { display: block; width: 150px; height: 150px; margin: 10px auto; object-fit: contain; background: white; padding: 8px; border-radius: 12px; border: 1px solid #e9e1d6; }
  .upi-id { display: inline-block; margin-top: 6px; padding: 6px 12px; background: #f0ece5; border-radius: 8px; font-weight: 700; font-family: Arial, sans-serif; }
  .price { margin-top: 10px; font-size: 20px; font-weight: 800; font-family: Arial, sans-serif; }
  .pay-title { font-size: 16px; font-weight: 800; font-family: Arial, sans-serif; }
  @media (max-width: 700px) { .layout { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<main>
  <header>
    <div class="eyebrow">Virtual Photo Booth</div>
    <h1>Welcome to Midhat's Photo Booth</h1>
    <p>Pick a vintage look, pose, and make a keepsake photo strip.</p>
  </header>
  <div class="layout">
    <section class="card">
      <div class="video-wrap">
        <video id="video" autoplay playsinline muted></video>
        <canvas id="live" width="640" height="480"></canvas>
      </div>
      <div class="controls">
        <button id="start" class="primary">Start camera</button>
        <button id="capture">Take photo 1 of 4</button>
        <button id="retake">Retake last photo</button>
        <button id="download" class="primary">Download strip</button>
      </div>
      <label for="filter">Vintage filter</label>
      <select id="filter">
        <option value="normal">Normal Camera - No Filter</option>
        <option value="gold">1990s Golden Film</option>
        <option value="pastel">Dreamy Pastel Y2K</option>
        <option value="noir">Noir S01 - Classic B&W</option>
        <option value="vintage12">Vintage 12 - Warm Faded 70s</option>
        <option value="retro_brownish">Retro Brownish Red Black - Heavy Grain VHS</option>
      </select>
      <label for="border">Strip border</label>
      <select id="border">
        <option value="floral">Cream &amp; pastel floral</option>
        <option value="black">Classic black</option>
        <option value="white">Classic white</option>
      </select>
      <p id="status">Start the camera and allow camera access when asked.</p>
    </section>
    <section class="card">
      <h2 style="margin-top:0">Your photo strip</h2>
      <div class="strip-preview"><canvas id="strip" width="600" height="1800"></canvas></div>
      <div class="qr">
        <div class="pay-msg">📸 Please first Scan QR & Pay ₹2, then Download your Strip!</div>
        <div class="pay-title">Scan to Pay</div>
        <img src="/qr.png" alt="UPI QR code">
        <div>Pay to <b>Midhat Naqvi</b></div>
        <div class="upi-id">naqviimidhat@okaxis</div>
        <div class="price">Price: ₹2 per Strip</div>
        <small>Pay ₹2 on this QR, then click Download Strip<br>Use any UPI app - GPay, PhonePe, Paytm</small>
      </div>
    </section>
  </div>
</main>
<script>
  const video = document.querySelector("#video");
  const live = document.querySelector("#live");
  const liveCtx = live.getContext("2d");
  const canvas = document.querySelector("#strip");
  const ctx = canvas.getContext("2d");
  const status = document.querySelector("#status");
  const filterSelect = document.querySelector("#filter");
  const borderSelect = document.querySelector("#border");
  let photos = [];
  let cameraStarted = false;

  // --- SAB FILTERS AB YAHI SE - EK HI JAGAH ---
  // brightness, contrast, saturate, grayscale, sepia, tint, vignette, grain
  // Preview aur Capture dono isi ko use karenge, isliye kabhi alag nahi hoga
  const looks = {
    normal: { b: 1.0, c: 1.0, s: 1.0, gray: 0, sepia: 0, tint: [0,0,0,0], vig: 0, grain: 0 },
    gold: { b: 1.04, c: 0.94, s: 1.2, gray: 0, sepia: 0.27, tint: [255,175,82,0.10], vig: 0.18, grain: 10 },
    pastel: { b: 1.09, c: 0.88, s: 0.82, gray: 0, sepia: 0, tint: [255,190,210,0.13], vig: 0.10, grain: 6 },
    noir: { b: 1.02, c: 1.15, s: 1.0, gray: 1.0, sepia: 0, tint: [0,0,0,0], vig: 0.28, grain: 12 },
    vintage12: { b: 1.03, c: 0.92, s: 1.05, gray: 0, sepia: 0.38, tint: [255,200,130,0.12], vig: 0.22, grain: 10 },
    retro_brownish: { b: 0.92, c: 1.08, s: 1.0, gray: 0.45, sepia: 0.55, tint: [120,30,20,0.18], vig: 0.35, grain: 12 }
  };

  // Ye function pixel-by-pixel filter lagata hai - Safari me bhi 100% chalega
  function applyFilterToCanvas(srcCanvas, destCtx, w, h, filterName, addGrain) {
    const f = looks[filterName];
    destCtx.drawImage(srcCanvas, 0, 0, w, h);
    // Mirror fix ke liye hum video ko pehle se mirror karke draw karenge
    const img = destCtx.getImageData(0, 0, w, h);
    const d = img.data;
    for (let i = 0; i < d.length; i += 4) {
      let r = d[i], g = d[i+1], b = d[i+2];
      // 1. Brightness
      r *= f.b; g *= f.b; b *= f.b;
      // 2. Contrast
      r = (r - 128) * f.c + 128; g = (g - 128) * f.c + 128; b = (b - 128) * f.c + 128;
      // 3. Saturate
      const lum = 0.299 * r + 0.587 * g + 0.114 * b;
      r = lum + (r - lum) * f.s; g = lum + (g - lum) * f.s; b = lum + (b - lum) * f.s;
      // 4. Grayscale - Noir ke liye ye 100% B&W kar dega
      if (f.gray > 0) {
        const gray = 0.299 * r + 0.587 * g + 0.114 * b;
        r = r * (1 - f.gray) + gray * f.gray;
        g = g * (1 - f.gray) + gray * f.gray;
        b = b * (1 - f.gray) + gray * f.gray;
      }
      // 5. Sepia - Vintage / Gold / Retro ke liye
      if (f.sepia > 0) {
        const sr = r * 0.393 + g * 0.769 + b * 0.189;
        const sg = r * 0.349 + g * 0.686 + b * 0.168;
        const sb = r * 0.272 + g * 0.534 + b * 0.131;
        r = r * (1 - f.sepia) + sr * f.sepia;
        g = g * (1 - f.sepia) + sg * f.sepia;
        b = b * (1 - f.sepia) + sb * f.sepia;
      }
      // 6. Tint
      if (f.tint[3] > 0) {
        r = r * (1 - f.tint[3]) + f.tint[0] * f.tint[3];
        g = g * (1 - f.tint[3]) + f.tint[1] * f.tint[3];
        b = b * (1 - f.tint[3]) + f.tint[2] * f.tint[3];
      }
      // 7. Grain - ab halka hai, VHS wala heavy grain hata diya
      if (addGrain && f.grain > 0) {
        const n = (Math.random() - 0.5) * f.grain;
        r += n; g += n; b += n;
      }
      d[i] = Math.max(0, Math.min(255, r));
      d[i+1] = Math.max(0, Math.min(255, g));
      d[i+2] = Math.max(0, Math.min(255, b));
    }
    destCtx.putImageData(img, 0, 0);
    // 8. Vignette
    if (f.vig > 0) {
      const v = destCtx.createRadialGradient(w/2, h/2, w*0.15, w/2, h/2, w*0.72);
      v.addColorStop(0, "rgba(0,0,0,0)"); v.addColorStop(1, `rgba(0,0,0,${f.vig})`);
      destCtx.fillStyle = v; destCtx.fillRect(0, 0, w, h);
    }
  }

  // Live Preview - har frame me wahi filter lagta hai jo capture me lagega
  function drawLive() {
    requestAnimationFrame(drawLive);
    if (!cameraStarted || !video.videoWidth) {
      liveCtx.fillStyle = "#26231f"; liveCtx.fillRect(0, 0, 640, 480);
      liveCtx.fillStyle = "#fff"; liveCtx.font = "20px Arial"; liveCtx.textAlign = "center";
      liveCtx.fillText("Start Camera", 320, 240);
      return;
    }
    // Mirror
    liveCtx.save(); liveCtx.translate(640, 0); liveCtx.scale(-1, 1);
    liveCtx.drawImage(video, 0, 0, 640, 480); liveCtx.restore();
    // Ab usi live canvas pe filter lagao - bina grain ke taaki preview flicker na kare
    // Grain sirf capture me lagega, halka sa
    const temp = document.createElement("canvas"); temp.width = 640; temp.height = 480;
    const tctx = temp.getContext("2d"); tctx.drawImage(live, 0, 0);
    // Filter lagane ke liye hum live ko saaf karke dobara filter ke saath draw karte hai
    // Simpler: live pe hi pixel filter lagao
    const f = looks[filterSelect.value];
    const img = liveCtx.getImageData(0, 0, 640, 480);
    const d = img.data;
    for (let i = 0; i < d.length; i += 4) {
      let r = d[i], g = d[i+1], b = d[i+2];
      r *= f.b; g *= f.b; b *= f.b;
      r = (r - 128) * f.c + 128; g = (g - 128) * f.c + 128; b = (b - 128) * f.c + 128;
      const lum = 0.299 * r + 0.587 * g + 0.114 * b;
      r = lum + (r - lum) * f.s; g = lum + (g - lum) * f.s; b = lum + (b - lum) * f.s;
      if (f.gray > 0) { const gray = 0.299 * r + 0.587 * g + 0.114 * b; r = r*(1-f.gray)+gray*f.gray; g = g*(1-f.gray)+gray*f.gray; b = b*(1-f.gray)+gray*f.gray; }
      if (f.sepia > 0) { const sr = r*0.393+g*0.769+b*0.189; const sg = r*0.349+g*0.686+b*0.168; const sb = r*0.272+g*0.534+b*0.131; r = r*(1-f.sepia)+sr*f.sepia; g = g*(1-f.sepia)+sg*f.sepia; b = b*(1-f.sepia)+sb*f.sepia; }
      if (f.tint[3] > 0) { r = r*(1-f.tint[3])+f.tint[0]*f.tint[3]; g = g*(1-f.tint[3])+f.tint[1]*f.tint[3]; b = b*(1-f.tint[3])+f.tint[2]*f.tint[3]; }
      d[i] = Math.max(0, Math.min(255, r)); d[i+1] = Math.max(0, Math.min(255, g)); d[i+2] = Math.max(0, Math.min(255, b));
    }
    liveCtx.putImageData(img, 0, 0);
    if (f.vig > 0) { const v = liveCtx.createRadialGradient(320, 240, 96, 320, 240, 460); v.addColorStop(0, "rgba(0,0,0,0)"); v.addColorStop(1, `rgba(0,0,0,${f.vig})`); liveCtx.fillStyle = v; liveCtx.fillRect(0, 0, 640, 480); }
  }
  drawLive();

  function flower(x, y, scale = 1) {
    ctx.save(); ctx.translate(x, y); ctx.scale(scale, scale);
    ctx.fillStyle = "#82977b";
    ctx.beginPath(); ctx.ellipse(-11, 13, 6, 15, -.8, 0, Math.PI * 2); ctx.ellipse(11, 13, 6, 15, .8, 0, Math.PI * 2); ctx.fill();
    const colors = ["#e8aeb8", "#f1c7ca", "#fffaf2"];
    ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
    for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; ctx.beginPath(); ctx.ellipse(Math.cos(a) * 8, Math.sin(a) * 8, 6, 9, a, 0, Math.PI * 2); ctx.fill(); }
    ctx.fillStyle = "#d4ae6d"; ctx.beginPath(); ctx.arc(0, 0, 4, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  }

  function drawStrip() {
    const style = borderSelect.value;
    const bg = style === "black" ? "#181715" : style === "white" ? "#ffffff" : "#fbf6e9";
    ctx.fillStyle = bg; ctx.fillRect(0, 0, 600, 1800);
    if (style === "floral") {
      for (let i = 0; i < 8; i++) { flower(22 + (i % 2) * 20, 45 + i * 235, .72); flower(578 - (i % 2) * 20, 145 + i * 205, .72); }
      flower(55, 50, .85); flower(545, 50, .85); flower(55, 1745, .85); flower(545, 1745, .85);
    }
    ctx.textAlign = "center"; ctx.fillStyle = style === "black" ? "#fff" : "#687866"; ctx.font = "bold 36px Georgia"; ctx.fillText("Midhat's Photo Booth", 300, 85);
    const boxX = 62, boxW = 476, boxH = 330, startY = 130, gap = 15;
    for (let i = 0; i < 4; i++) {
      const y = startY + i * (boxH + gap);
      ctx.fillStyle = "#fff"; ctx.fillRect(boxX, y, boxW, boxH);
      ctx.strokeStyle = style === "black" ? "#d7d1c8" : "#ded8ce"; ctx.lineWidth = 2; ctx.strokeRect(boxX, y, boxW, boxH);
      if (photos[i]) {
        const img = new Image();
        img.onload = () => { ctx.drawImage(img, boxX + 7, y + 7, boxW - 14, boxH - 14); };
        img.src = photos[i];
      } else { ctx.fillStyle = "#9a958c"; ctx.font = "20px Arial"; ctx.fillText(`Photo ${i + 1}`, 300, y + boxH / 2); }
    }
    ctx.fillStyle = style === "black" ? "#fff" : "#687866"; ctx.font = "italic 36px Georgia"; ctx.fillText("Photo Booth", 300, 1665);
    if (style === "floral") { flower(115, 1715, .65); flower(485, 1715, .65); }
  }

  document.querySelector("#start").addEventListener("click", async () => {
    try { const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false }); video.srcObject = stream; cameraStarted = true; status.textContent = "Camera ready — choose a filter and take your first photo."; }
    catch (error) { status.textContent = "Camera unavailable. Allow camera access and try again."; }
  });

  document.querySelector("#capture").addEventListener("click", () => {
    if (!cameraStarted || !video.videoWidth) { status.textContent = "Start the camera before taking photos."; return; }
    if (photos.length >= 4) { status.textContent = "Your strip is complete."; return; }
    // FIX: Capture ab live canvas se hi lega - jo dikh raha hai wahi photo banegi
    // Isliye Noir B&W hi aayega, Vintage warm hi aayega, Retro me heavy VHS nahi aayega
    const shot = document.createElement("canvas"); shot.width = 640; shot.height = 480;
    const shotCtx = shot.getContext("2d");
    // Live canvas pe already filter laga hua hai, usko copy karo + halka grain
    shotCtx.drawImage(live, 0, 0, 640, 480);
    const f = looks[filterSelect.value];
    if (f.grain > 0) {
      const img = shotCtx.getImageData(0, 0, 640, 480); const d = img.data;
      for (let i = 0; i < d.length; i += 4) { const n = (Math.random() - 0.5) * f.grain; d[i] += n; d[i+1] += n; d[i+2] += n; }
      shotCtx.putImageData(img, 0, 0);
    }
    photos.push(shot.toDataURL("image/jpeg", .92)); drawStrip();
    status.textContent = photos.length < 4 ? `Photo ${photos.length} of 4 captured.` : "Your strip is ready — Please Scan QR & Pay ₹2, then Download!";
    document.querySelector("#capture").textContent = photos.length < 4 ? `Take photo ${photos.length + 1} of 4` : "Strip complete";
  });

  document.querySelector("#retake").addEventListener("click", () => {
    if (!photos.length) return;
    photos.pop(); drawStrip(); document.querySelector("#capture").textContent = `Take photo ${photos.length + 1} of 4`;
  });

  document.querySelector("#download").addEventListener("click", () => {
    if (photos.length !== 4) { status.textContent = "Take all four photos before downloading."; return; }
    drawStrip();
    setTimeout(() => { const link = document.createElement("a"); link.download = "midhat-photo-booth-strip.png"; link.href = canvas.toDataURL("image/png"); link.click(); status.textContent = "Downloaded! Thank you for paying ₹2 ❤️"; }, 350);
  });

  borderSelect.addEventListener("change", drawStrip);
  drawStrip();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE)

@app.route("/qr.png")
def qr_image():
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(UPI_LINK)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)