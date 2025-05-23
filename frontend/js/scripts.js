document.addEventListener('DOMContentLoaded', () => {
    const trainForm = document.getElementById('trainForm');
    if (!trainForm) {
        console.error('Error: Form with ID "trainForm" not found.');
        return;
    }

    trainForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const messageElement = document.getElementById('message');
        if (!messageElement) {
            console.error('Error: Element with ID "message" not found.');
            return;
        }
        messageElement.textContent = ''; // Clear previous messages

        // Get references to input elements
        const category1LabelElement = document.getElementById('category1Label');
        const category1ImagesElement = document.getElementById('category1Images');
        const category2LabelElement = document.getElementById('category2Label');
        const category2ImagesElement = document.getElementById('category2Images');

        // Validate elements exist
        if (!category1LabelElement) {
            console.error('Error: Input with ID "category1Label" not found.');
            messageElement.textContent = 'Error: Category 1 Label input not found.';
            return;
        }
        if (!category1ImagesElement) {
            console.error('Error: Input with ID "category1Images" not found.');
            messageElement.textContent = 'Error: Category 1 Images input not found.';
            return;
        }
        if (!category2LabelElement) {
            console.error('Error: Input with ID "category2Label" not found.');
            messageElement.textContent = 'Error: Category 2 Label input not found.';
            return;
        }
        if (!category2ImagesElement) {
            console.error('Error: Input with ID "category2Images" not found.');
            messageElement.textContent = 'Error: Category 2 Images input not found.';
            return;
        }

        const formData = new FormData();

        // Append label values
        formData.append('category1_label', category1LabelElement.value);
        formData.append('category2_label', category2LabelElement.value);

        // Append files for category 1
        if (category1ImagesElement.files) {
            for (const file of category1ImagesElement.files) {
                formData.append('category1_images', file);
            }
        } else {
            console.error('Error: category1ImagesElement.files is null');
            messageElement.textContent = 'Error: No files selected for Category 1.';
            return;
        }


        // Append files for category 2
        if (category2ImagesElement.files) {
            for (const file of category2ImagesElement.files) {
                formData.append('category2_images', file);
            }
        } else {
            console.error('Error: category2ImagesElement.files is null');
            messageElement.textContent = 'Error: No files selected for Category 2.';
            return;
        }

        try {
            const response = await fetch('/train_model', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                messageElement.textContent = result.message;
            } else {
                const errorText = await response.text();
                messageElement.textContent = `Error training model: ${response.status} ${response.statusText}. ${errorText}`;
                console.error('Error training model:', response.status, response.statusText, errorText);
            }
        } catch (error) {
            messageElement.textContent = `Error training model: ${error.message}`;
            console.error('Fetch error:', error);
        }
    });
});
