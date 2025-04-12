// previewManager.js - Preview pane & editor logic

/**
 * Initialize the preview functionality
 * @param {HTMLTextAreaElement} htmlCode - The HTML editor element
 * @param {HTMLIFrameElement} preview - The preview iframe element
 */
function initPreview(htmlCode, preview) {
    // Set up event listener for editor changes
    htmlCode.addEventListener('input', () => updatePreview(htmlCode, preview));
    
    // Initial update
    updatePreview(htmlCode, preview);
}

/**
 * Update the preview iframe with the current HTML code
 * @param {HTMLTextAreaElement} htmlCode - The HTML editor element
 * @param {HTMLIFrameElement} preview - The preview iframe element
 */
function updatePreview(htmlCode, preview) {
    const previewDoc = preview.contentDocument || preview.contentWindow.document;
    previewDoc.open();
    previewDoc.write(htmlCode.value);
    previewDoc.close();
}