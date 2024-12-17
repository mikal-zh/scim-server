function sumCategories(formData) {
    const categories = {
        'entree': 0,
        'plat': 0,
        'dessert': 0,
    };

    for (let [key, value] of formData.entries()) {
        const category = key.split(':')[0];
        const numericValue = parseFloat(value) || 0;

        if (categories.hasOwnProperty(category)) {
            categories[category] += numericValue;
        }
    }
    const total = categories.entree * 3 + categories.plat * 8 + categories.dessert * 3;
    categories.total = total;
    return categories;
}

function handleSubmit(event) {
    // Create FormData object
    const formData = new FormData(event.target);
    const results = sumCategories(formData);

    // POST data to server
    console.log(formData);
    console.log(results);

    if (results.total == 0)
        return false;

    // POST database    
    let i = fetch('https://securesnack.ariovis.fr/menu', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            Entree: results.entree,
            Plat: results.plat,
            Dessert: results.dessert,
            Total: results.total,
        })
    }).then((response) => 
        {
            if (response.ok) {
                Toastify({
                    text: "Votre commande a été validée",
                    duration: 3000,
                    destination: "commande",
                    gravity: "bottom", // `top` or `bottom`
                    position: "right", // `left`, `center` or `right`
                    stopOnFocus: true, // Prevents dismissing of toast on hover
                    backgroundColor: "green",
                }).showToast();
            } else {
                Toastify({
                    text: "Erreur lors de la validation de votre commande",
                    duration: 3000,
                    destination: "commande",
                    gravity: "bottom", // `top` or `bottom`
                    position: "right", // `left`, `center` or `right`
                    stopOnFocus: true, // Prevents dismissing of toast on hover
                    backgroundColor: "red",
                }).showToast();
            }
        }
    )
    // Reset the form
    event.target.reset();
    // prevent from submitting the form
    return false
}

function deleteDB(event) {
    const formData = new FormData(event.target);
}