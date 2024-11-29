function sumCategories(formData) {
    const categories = {
        'entree': 0,
        'plat': 0,
        'dessert': 0
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
    // console.log(formData);
    // console.log(results);

    // Recup id user

    // POST database    
    let i = fetch('https://securesnack.ariovis.fr/menu', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            nb_entree: results.entree,
            nb_plat: results.plat,
            nb_dessert: results.dessert,
        })
    }).then((response) => console.log("reponse", response))
    // Reset the form
    event.target.reset();

    // prevent from submitting the form
    return false
}
