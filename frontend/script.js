let mediaRecorder = null;
let audioChunks = [];
const micBtn = document.getElementById("micBtn");
const statusDiv = document.getElementById("status");
const transcriptDiv = document.getElementById("transcript");

micBtn.disabled = false;

micBtn.addEventListener("click", async () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    micBtn.classList.remove("recording");
    micBtn.disabled = true; 
    statusDiv.textContent = "Thinking...";
    statusDiv.style.opacity = "0.9";
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
  
      stream.getTracks().forEach((track) => track.stop());

      if (audioChunks.length === 0) {
        updateStatus("No audio detected. Try again.", false);
        enableMic();
        return;
      }

      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", audioBlob, "recorded.webm");

      try {
        updateStatus("Processing...", false);
        transcriptDiv.textContent = "";

        const res = await fetch("/process", {
          method: "POST",
          body: formData,
        });

        if (res.ok) {
          const userTranscript = res.headers.get("X-Transcript");
          if (userTranscript) {
            transcriptDiv.textContent = `"${userTranscript}"`;
          }

          const audioUrl = URL.createObjectURL(await res.blob());
          const audio = new Audio(audioUrl);
          audio.play();

          updateStatus("Speaking...", false);

          audio.onended = () => {
            updateStatus("Ready for your next command", true);
            setTimeout(() => {
              if (!transcriptDiv.textContent.includes("Error")) {
                transcriptDiv.textContent = "";
              }
            }, 3000);
          };
        } else {
          const errText = await res.text();
          updateStatus(`Error: ${errText || "Processing failed"}`, true, true);
        }
      } catch (e) {
        console.error("Network error:", e);
        updateStatus(`Network error: ${e.message}`, true, true);
      } finally {
        enableMic();
      }
    };

    mediaRecorder.start();
    micBtn.classList.add("recording");
    updateStatus("Listening...", false);
    transcriptDiv.textContent = "";
  } catch (err) {
    console.error("Mic access error:", err);
    updateStatus(
      `Mic error: ${err.message || "Permission denied"}`,
      true,
      true,
    );
    enableMic();
  }
});

document.addEventListener("keydown", (e) => {
  if (e.key === " " && micBtn.disabled === false) {
    e.preventDefault();
    if (!mediaRecorder || mediaRecorder.state !== "recording") {
      micBtn.click();
    }
  }
});

function updateStatus(message, isError = false, isCritical = false) {
  statusDiv.textContent = message;
  statusDiv.style.color = isError ? "#ffcccc" : "white";
  statusDiv.style.opacity = isCritical ? "1" : "0.9";

  if (isError && isCritical) {
    transcriptDiv.textContent = `️ ${message}`;
    transcriptDiv.style.color = "#ff9999";
  }
}

function enableMic() {
  micBtn.disabled = false;
  if (mediaRecorder?.state === "recording") {
    micBtn.classList.add("recording");
  } else {
    micBtn.classList.remove("recording");
  }
}

setTimeout(() => {
  statusDiv.style.opacity = "0.7";
}, 2000);
