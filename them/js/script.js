document.addEventListener("DOMContentLoaded", function () {
    const tagsInput = document.getElementById("tagsInput");
    const addTagBtn = document.getElementById("addTagBtn");
    const tagsContainer = document.getElementById("tagsContainer");
    const saveBtn = document.getElementById("saveBtn");
    const fileInput = document.getElementById("file");

    let formData = {};

    addTagBtn.addEventListener("click", function () {
        const tagText = tagsInput.value.trim();

        if (tagText !== "") {
            const tagSpan = document.createElement("span");
            tagSpan.textContent = tagText;
            tagsContainer.appendChild(tagSpan);

            // Add tag to formData
            if (!formData.tags) {
                formData.tags = [];
            }
            formData.tags.push(tagText);

            // Clear input
            tagsInput.value = "";
        }
    });

    fileInput.addEventListener("change", function () {
        const file = fileInput.files[0];

        const reader = new FileReader();
        reader.onload = function(event) {
            const imageData = event.target.result;
            const base64Image = imageData.split(",")[1]; // Remove data:image/jpeg;base64, part

            formData.image = base64Image;
        };
        reader.readAsDataURL(file);
    });

    saveBtn.addEventListener("click", function () {
        // Get all input values
        document.getElementById("info").innerHTML = editor.html.get()
        const inputs = document.querySelectorAll("input[type=text] , textarea, alireza, input[type=checkbox]:checked");
        inputs.forEach(input => {
            if (input.type === "checkbox") {
                if (!formData[input.name]) {
                    formData[input.name] = [];
                }
                formData[input.name].push(input.value);
            } else if(input.getAttribute("name") === "info") {
                formData[input.getAttribute("name")] = input.innerHTML
            } else {
                formData[input.name] = input.value;
            }
        });

        // Remove null or undefined values from formData
        formData = removeNullOrUndefinedValues(formData);

        // Convert formData.chart to a unique array
        if (formData.chart) {
            formData.chart = getUniqueArray(formData.chart);
        }

        // Check for empty fields and remove them
        formData = removeEmptyFields(formData);

        // Convert formData to JSON
        const jsonData = JSON.stringify(formData);

        // Save JSON to file
        const blob = new Blob([jsonData], {type: "application/json"});
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "form_data.json";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
});

function removeNullOrUndefinedValues(obj) {
    return Object.fromEntries(Object.entries(obj).filter(([_, v]) => v !== null && v !== undefined));
}

function getUniqueArray(arr) {
    return [...new Set(arr)];
}

function removeEmptyFields(obj) {
    Object.keys(obj).forEach(key => {
        if (obj[key] === "" || obj[key] === undefined) {
            delete obj[key];
        }
    });
    return obj;
}
