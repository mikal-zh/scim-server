function sumCategories(formData) {
    const categories = {
        'entrée': 0,
        'plat': 0,
        'desseert': 0
    };

    for (let [key, value] of formData.entries()) {
        const category = key.split(':')[0];
        const numericValue = parseFloat(value) || 0;

        if (categories.hasOwnProperty(category)) {
            categories[category] += numericValue;
        }
    }

    return categories;
}

function handleSubmit(event) {
    // Create FormData object
    const formData = new FormData(event.target);
    const results = sumCategories(formData);

    // POST data to server
    console.log(formData);
    console.log(results);

    // Recup id user

    // POST database

    // Reset the form
    event.target.reset();

    // prevent from submitting the form
    return false
}
