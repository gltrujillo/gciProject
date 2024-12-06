// Initialize Socket.IO connection
const socket = io("http://127.0.0.1:5000"); // Adjust URL for your Flask app

// WebSocket connection events
socket.on("connect", () => {
    console.log("WebSocket connection established");
    socket.emit("message", "Hello from the client!");
});

socket.on("message", (data) => {
    console.log("Message from server:", data);
});

socket.on("disconnect", () => {
    console.warn("WebSocket connection closed");
});

socket.on("error", (error) => {
    console.error("WebSocket error:", error);
});

// File Input Handling
const triggerFileInput = document.getElementById("triggerFileInput");
const audioInput = document.getElementById("audioInput");
const resultDiv = document.getElementById("result");
const promptTextarea = document.getElementById("prompt-textarea");

// Debugging button and input availability
console.log("Trigger button:", triggerFileInput);
console.log("Audio input:", audioInput);

if (triggerFileInput && audioInput) {
    console.log("Audio input and trigger button found!");

    // Add click listener to trigger the file input
    triggerFileInput.addEventListener("click", () => {
        console.log("Trigger button clicked");
        try {
            audioInput.click();
            console.log("File input click triggered");
        } catch (error) {
            console.error("Error triggering file input:", error);
        }
    });

    // Handle file selection
    audioInput.addEventListener("change", async (event) => {
        console.log("File input change event triggered");

        const file = event.target.files[0];
        console.log("Selected file:", file);

        if (file) {
            promptTextarea.innerHTML = "<p>Uploading and processing your audio...</p>";
            await handleFileUpload(file);
        } else {
            promptTextarea.innerHTML = "<p>No file selected. Please try again.</p>";
        }
    });
} else {
    console.error("Audio input or trigger button not found!");
}

// Handle Audio File Upload
async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${window.location.origin}/upload`, {
            method: "POST",
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            console.log("File uploaded successfully:", result.message);
            promptTextarea.innerHTML = `<p>${result.message}</p>`;

            // Fetch and display the notes in the textarea
            await fetchAndDisplayNotes();
        } else {
            console.error("File upload error:", result.error);
            promptTextarea.innerHTML = `<p>Error: ${result.error}</p>`;
        }
    } catch (error) {
        console.error("Error during file upload:", error);
        promptTextarea.innerHTML = "<p>An error occurred while processing the file. Please try again.</p>";
    }
}

// Fetch and Display Notes
async function fetchAndDisplayNotes() {
    try {
        const response = await fetch(`${window.location.origin}/get_notes`);

        if (response.ok) {
            const data = await response.json();
            console.log("Notes fetched successfully:", data.notes);

            // Display the notes in the prompt-textarea div
            if (promptTextarea) {
                promptTextarea.innerText = data.notes;
                promptTextarea.style.color = "white"; // Adjust text color for display
            }
        } else {
            console.error("Error fetching notes:", response.statusText);
        }
    } catch (error) {
        console.error("Error while fetching notes:", error);
    }
}

// Placeholder Management for #prompt-textarea
if (promptTextarea) {
    promptTextarea.style.color = "gray"; // Set initial placeholder text color
    promptTextarea.addEventListener("focus", () => handlePlaceholderFocus(promptTextarea));
    promptTextarea.addEventListener("blur", () => handlePlaceholderBlur(promptTextarea));
}

function handlePlaceholderFocus(element) {
    if (element.innerText.trim() === element.getAttribute("data-placeholder")) {
        element.innerText = ""; // Clear placeholder text
        element.style.color = "black"; // Adjust text color for user input
    }
}

function handlePlaceholderBlur(element) {
    if (element.innerText.trim() === "") {
        element.innerText = element.getAttribute("data-placeholder"); // Reset placeholder text
        element.style.color = "gray"; // Placeholder text color
    }
}
