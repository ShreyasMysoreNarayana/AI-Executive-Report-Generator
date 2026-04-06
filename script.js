const form = document.getElementById("reportForm");
const submitBtn = document.getElementById("submitBtn");
const statusBox = document.getElementById("statusBox");
const downloadBox = document.getElementById("downloadBox");
const downloadLink = document.getElementById("downloadLink");
const loadingOverlay = document.getElementById("loadingOverlay");

function showStatus(message, type = "success") {
    statusBox.classList.remove("hidden", "success", "error");
    statusBox.classList.add(type);
    statusBox.textContent = message;
}

function hideStatus() {
    statusBox.classList.add("hidden");
    statusBox.classList.remove("success", "error");
    statusBox.textContent = "";
}

function showDownload(url) {
    if (!url) {
        downloadBox.classList.add("hidden");
        return;
    }
    downloadLink.href = url;
    downloadBox.classList.remove("hidden");
}

function hideDownload() {
    downloadBox.classList.add("hidden");
    downloadLink.href = "#";
}

function setLoading(isLoading) {
    if (isLoading) {
        loadingOverlay.classList.remove("hidden");
        submitBtn.disabled = true;
        submitBtn.textContent = "Generating...";
    } else {
        loadingOverlay.classList.add("hidden");
        submitBtn.disabled = false;
        submitBtn.textContent = "Generate Report";
    }
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    hideStatus();
    hideDownload();
    setLoading(true);

    try {
        const formData = new FormData(form);

        const response = await fetch("/api/generate-report", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Failed to generate report.");
        }

        showStatus(data.message || "Report generated successfully.", "success");

        if (data.download_url) {
            showDownload(data.download_url);
        }
    } catch (error) {
        showStatus(error.message || "Something went wrong.", "error");
    } finally {
        setLoading(false);
    }
});