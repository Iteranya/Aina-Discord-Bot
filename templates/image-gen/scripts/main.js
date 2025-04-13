let currentTaskId = null;
        let statusCheckInterval = null;
        let consecutiveNetworkErrors = 0;
        const MAX_NETWORK_RETRIES = 5;

        // Initialize gallery from sessionStorage
        let gallery = JSON.parse(sessionStorage.getItem('comfyui_gallery')) || [];

        const statusElement = document.getElementById('status');
        const statusTextElement = statusElement.querySelector('span');
        const generateButton = document.getElementById('generateButton'); // Use specific ID
        const galleryGrid = document.getElementById('galleryGrid');
        const clearGalleryButton = document.getElementById('clearGalleryButton'); // Use specific ID

        // --- NEW: Modal Elements ---
        const imageModal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        const modalCloseBtn = document.getElementById('modalCloseBtn');

        // Initialize gallery display
        updateGalleryDisplay();

        // Helper function to update status with icon logic
        function updateStatus(message, type = 'info') {
            statusTextElement.textContent = message; // Update only the text part
            statusElement.className = type; // Set class for styling (info, success, error, loading)
        }

        async function generateImage() {
            currentTaskId = null;
            consecutiveNetworkErrors = 0; // Reset error counter for new task
            updateStatus('Starting image generation... Getting ready! (๑˃̵ᴗ˂̵)و', 'loading'); // Use loading style
            generateButton.disabled = true; // Disable button during processing
            clearInterval(statusCheckInterval); // Clear any existing interval
            statusCheckInterval = null; // Explicitly nullify

            // Gather form data
            const positive_prompt = document.getElementById('positive_prompt').value;
            const negative_prompt = document.getElementById('negative_prompt').value;
            const width = parseInt(document.getElementById('width').value, 10);
            const height = parseInt(document.getElementById('height').value, 10);
            let server_address = document.getElementById('server_address').value.trim();
            if (!server_address) {
                server_address = null; // Send null if empty, so backend uses default
            }

            const payload = {
                positive_prompt,
                negative_prompt,
                width,
                height,
                server_address
            };

            try {
                // Fetch paths should remain the same if your FastAPI routes are correct
                const response = await fetch('/comfyui/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                // Try to parse JSON regardless of response.ok to get potential error detail
                let data;
                try {
                    data = await response.json();
                    console.log("Generation Request Response:", data);
                } catch (jsonError) {
                    // If JSON parsing fails, create a generic error object
                    console.error("Failed to parse JSON response:", jsonError);
                    data = { detail: `Server returned status ${response.status} but response was not valid JSON.` };
                }


                if (!response.ok) {
                    // Display detail from HTTPException if available, or a fallback
                    updateStatus(`Error starting generation: ${data.detail || `Server error ${response.status}`}. Please try again! (｡•́︿•̀｡)`, 'error');
                    generateButton.disabled = false; // Re-enable button
                    return;
                }

                currentTaskId = data.task_id;
                if (!currentTaskId) {
                    updateStatus('Error: Server responded OK but did not provide a Task ID. Cannot track progress. (⊙_⊙)?', 'error');
                    generateButton.disabled = false;
                    return;
                }

                updateStatus(`Generation started (Task ID: ${currentTaskId}). Checking status... Let's see... (づ｡◕‿‿◕｡)づ`, 'loading');

                // Start checking status immediately and then interval
                // Use setTimeout for the first check to allow UI to update immediately
                setTimeout(async () => {
                   await checkStatus(); // Initial check

                   // Only set interval if the task didn't *already* complete or fail in the first check
                   // and the interval hasn't been cleared by checkStatus itself.
                   // Check if `currentTaskId` is still set (not cleared by failure/completion)
                   // and if the status is still 'loading'.
                   if (currentTaskId && statusElement.className.includes('loading')) {
                        // Clear any *previous* interval just in case (shouldn't be needed but safe)
                        if (statusCheckInterval) clearInterval(statusCheckInterval);
                        statusCheckInterval = setInterval(checkStatus, 3000); // Check every 3 seconds
                        console.log(`Interval set for Task ID: ${currentTaskId}`);
                   } else {
                        // If the task completed/failed on the first check or currentTaskId got unset
                        console.log(`Interval NOT set after first check. Task ID: ${currentTaskId}, Status Class: ${statusElement.className}`);
                        if (!generateButton.disabled && statusElement.className !== 'loading') {
                            // Ensure button is enabled if we're not loading anymore
                            generateButton.disabled = false;
                        }
                   }
                }, 100); // Short delay (100ms) before first check


            } catch (error) {
                console.error("Error during generateImage fetch:", error);
                updateStatus(`Network error during initial request: ${error.message}. Check connection? (＞﹏＜)`, 'error');
                generateButton.disabled = false; // Re-enable button
                 clearInterval(statusCheckInterval); // Ensure no interval runs
                 statusCheckInterval = null;
            }
        }

        function updateGalleryDisplay() {
            galleryGrid.innerHTML = ''; // Clear existing grid items
            gallery.forEach((item, index) => {
                const wrapper = document.createElement('div');
                wrapper.className = 'gallery-item';
                wrapper.dataset.index = index; // Store index for modal click

                wrapper.innerHTML = `
                    <img src="${item.url}" class="gallery-image" alt="Generated image preview">
                    <div class="gallery-meta">${item.timestamp}<br>Task: ${item.taskId}</div>
                    <button class="delete-btn" data-index="${index}">
                        <i class="fa-solid fa-times"></i>
                    </button>
                `;

                // Add click listener for modal *only* to the wrapper/image area
                wrapper.addEventListener('click', (event) => {
                    // Prevent modal opening if the delete button was clicked
                    if (event.target.closest('.delete-btn')) {
                        return;
                    }
                    openImageModal(index);
                });

                 // Add separate click listener for the delete button
                 const deleteButton = wrapper.querySelector('.delete-btn');
                 deleteButton.addEventListener('click', (event) => {
                     event.stopPropagation(); // Prevent gallery item click event
                     deleteGalleryItem(index);
                 });


                galleryGrid.appendChild(wrapper);
            });
        }

        function deleteGalleryItem(index) {
            gallery.splice(index, 1); // Remove item from array
            sessionStorage.setItem('comfyui_gallery', JSON.stringify(gallery)); // Update storage
            updateGalleryDisplay(); // Redraw the gallery
        }

        function clearGallery() {
            gallery = []; // Clear the array
            sessionStorage.removeItem('comfyui_gallery'); // Clear storage
            updateGalleryDisplay(); // Redraw empty gallery
        }

        // --- NEW: Modal Functions ---
        function openImageModal(index) {
            if (index >= 0 && index < gallery.length) {
                const item = gallery[index];
                modalImage.src = item.url; // Set the image source for the modal
                modalImage.alt = `Full size image from task ${item.taskId}`;
                imageModal.classList.add('visible'); // Show the modal
            }
        }

        function closeImageModal() {
            imageModal.classList.remove('visible'); // Hide the modal
            // Optional: Clear src to prevent showing old image briefly on next open
            setTimeout(() => { modalImage.src = ''; }, 300); // Delay matches transition
        }

        async function checkStatus() {
            if (!currentTaskId) {
                 console.warn("checkStatus called without currentTaskId.");
                 clearInterval(statusCheckInterval);
                 statusCheckInterval = null;
                 // Ensure button is enabled if we stop checking for this reason
                 if (statusElement.className !== 'loading') generateButton.disabled = false;
                return;
            }

            console.log(`Checking status for Task ID: ${currentTaskId}, Consecutive Errors: ${consecutiveNetworkErrors}`);

            try {
                const response = await fetch(`/comfyui/status/${currentTaskId}`);
                console.log(`AAAAAAAAAAAAAAAAAAAA ${response} AAAAAAAAAAAAAAAAAAAA`)
                consecutiveNetworkErrors = 0; // ** Reset network error counter on successful communication **

                if (!response.ok) {
                    let errorMsg = `Server returned ${response.status}`;
                    if (response.status === 404) {
                        errorMsg = `Task ID ${currentTaskId} not found. Maybe it finished super fast or there was an issue?`;
                    }
                    updateStatus(`Error checking status: ${errorMsg}. Stopping checks. (´･_･\`)`, 'error');
                    clearInterval(statusCheckInterval);
                    statusCheckInterval = null;
                    currentTaskId = null; // Task is gone or errored, stop associating with it
                    generateButton.disabled = false;
                    return;
                }

                let data;
                try {
                     data = await response.json();
                     console.log("Status Check Response:", data);
                } catch (jsonError) {
                     console.error("Failed to parse JSON response from status check:", jsonError);
                     updateStatus(`Error: Received OK status from server, but couldn't understand the response. Stopping checks. ( T ω T )`, 'error');
                     clearInterval(statusCheckInterval);
                     statusCheckInterval = null;
                     currentTaskId = null; // Unset task ID as we can't track it anymore
                     generateButton.disabled = false;
                     return;
                }


                // --- Process the valid JSON data ---
                 const statusTaskId = data.task_id || currentTaskId; // Use task_id from response if available

                if (data.status === 'completed') {
                    clearInterval(statusCheckInterval);
                    statusCheckInterval = null;
                    updateStatus(`Yay! Generated ${data.image_count} image(s)! Adding to gallery... (っ˘ω˘ς )`, 'success');
                    generateButton.disabled = false;

                     if (data.image_count > 0 && statusTaskId) {
                        const timestamp = new Date().toLocaleString();
                        const imagePromises = [];

                        for (let i = 0; i < data.image_count; i++) {
                            imagePromises.push(
                                new Promise((resolve) => {
                                    const imageUrl = `/comfyui/image/${statusTaskId}?index=${i}`; // Add timestamp to prevent caching issues maybe?
                                    const img = new Image();
                                    img.onload = () => resolve({
                                        url: imageUrl,
                                        timestamp: timestamp,
                                        taskId: statusTaskId
                                    });
                                    // If an image fails to load, resolve with null so Promise.all doesn't reject
                                    img.onerror = () => {
                                         console.error(`Failed to load image: ${imageUrl}`);
                                         resolve(null);
                                     };
                                    img.src = imageUrl;
                                })
                            );
                        }

                        Promise.all(imagePromises).then(images => {
                            const newImages = images.filter(img => img !== null); // Filter out failed loads

                             // Remove any previous images from the *same completed task ID* before adding new ones
                             // This prevents duplicates if checkStatus somehow runs again after completion
                             gallery = gallery.filter(existingImg => existingImg.taskId !== statusTaskId);

                            // Add the newly generated images to the front (most recent first!)
                            gallery.unshift(...newImages);

                            sessionStorage.setItem('comfyui_gallery', JSON.stringify(gallery));
                            updateGalleryDisplay();
                        }).catch(err => {
                            console.error("Error loading images into gallery:", err);
                            updateStatus(`Generated images, but couldn't load them all into the gallery. (｡•́︿•̀｡)`, 'warning');
                        });

                    } else if (data.image_count > 0 && !statusTaskId) {
                        updateStatus(`Yay! Generated ${data.image_count} image(s)! Adding to gallery... (っ˘ω˘ς )`, 'success');
                        //updateStatus('Generation complete, but failed to confirm Task ID for image retrieval. (｡•́︿•̀｡)', 'error');
                    } else {
                        updateStatus('Generation complete, but no images were returned. Hmm... (￣ω￣;)', 'warning');
                    }
                    currentTaskId = null; // Task is complete, clear the current ID

                } else if (data.status === 'failed') {
                    clearInterval(statusCheckInterval);
                    statusCheckInterval = null;
                    updateStatus(`Oh no! Generation failed for Task ${statusTaskId}: ${data.error || 'Unknown error'} (｡>_<｡)`, 'error');
                    generateButton.disabled = false;
                    currentTaskId = null; // Task failed, clear the ID

                } else if (data.status === 'processing') {
                    // Update status but keep polling
                    let progressMsg = `Processing... Hang tight, Senpai! (づ｡◕‿‿◕｡)づ (Task ID: ${statusTaskId})`;
                    if (data.progress && data.total_steps) {
                        progressMsg += ` [${data.progress}/${data.total_steps}]`;
                    }
                    updateStatus(progressMsg, 'loading');
                    // Button remains disabled, interval continues

                } else {
                    // Handle unexpected statuses
                    updateStatus(`Status: Unknown (${data.status}) for Task ${statusTaskId} - That's weird! Stopping checks. (o_O)`, 'error');
                    clearInterval(statusCheckInterval);
                    statusCheckInterval = null;
                    generateButton.disabled = false;
                    currentTaskId = null; // Unset task ID
                }
            } catch (error) {
                consecutiveNetworkErrors++;
                console.error(`Network error checking status (Attempt ${consecutiveNetworkErrors}/${MAX_NETWORK_RETRIES}):`, error);

                if (consecutiveNetworkErrors >= MAX_NETWORK_RETRIES) {
                    updateStatus(`Network error checking status for Task ${currentTaskId}: ${error.message}. Giving up after ${MAX_NETWORK_RETRIES} tries. (✖﹏✖)`, 'error');
                    clearInterval(statusCheckInterval);
                    statusCheckInterval = null;
                    generateButton.disabled = false; // Re-enable button as we stopped trying
                    currentTaskId = null; // Assume task state is unknown/lost
                } else {
                    updateStatus(`Network error checking status for Task ${currentTaskId}: ${error.message}. Trying again... (${consecutiveNetworkErrors}/${MAX_NETWORK_RETRIES}) (＞人＜;)`, 'error');
                     // Keep the 'error' class, but the message indicates a retry. Interval continues.
                }
            }
        }

        // Event listener for form submission
        document.getElementById('generateForm').addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission
            generateImage(); // Call our JS function instead
        });

        // Event listener for clearing the gallery
        clearGalleryButton.addEventListener('click', clearGallery);

        // --- NEW: Event listeners for Modal ---
        modalCloseBtn.addEventListener('click', closeImageModal);
        // Close modal if user clicks on the dark overlay background
        imageModal.addEventListener('click', (event) => {
            if (event.target === imageModal) { // Check if the click was directly on the overlay
                closeImageModal();
            }
        });
        // Close modal on Escape key press
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && imageModal.classList.contains('visible')) {
                closeImageModal();
            }
        });
        // Initial status message on page load
        updateStatus('Enter parameters and click Generate, Senpai! Let\'s make something amazing! ( ´ ▽ ` )ﾉ', 'info');