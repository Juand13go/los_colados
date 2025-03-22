document.getElementById("candidateForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    let isValid = true;

    // Mapeo de nivel educativo
    const educationMap = {"secundaria": 1, "tecnico": 2, "tecnologo": 3, "universitario": 4, "postgrado": 5};
    if (formData.get("educationLevel")) {
        formData.set("educationLevel", educationMap[formData.get("educationLevel")] || 0);
    }
    
    // Limpia mensajes de error previos
    document.querySelectorAll(".error-message").forEach(msg => msg.remove());
    document.querySelectorAll(".input-field").forEach(field => field.classList.remove("error"));

    function showError(inputName, message) {
        const inputElement = document.querySelector(`[name="${inputName}"]`);
        
        if (!inputElement) {
            console.error(`No se encontró el campo: ${inputName}`);
            return;
        }
    
        const errorText = document.createElement("p");
        errorText.classList.add("error-message");
        errorText.style.color = "red";
        errorText.style.fontSize = "12px";
        errorText.style.marginTop = "5px";
        errorText.textContent = message;
    
        const inputContainer = inputElement.closest(".input-field") || inputElement.parentElement;
        if (inputContainer) {
            inputContainer.appendChild(errorText);
            inputContainer.classList.add("error");
        } else {
            console.error(`No se encontró el contenedor del campo: ${inputName}`);
        }
    }

    // Validaciones del formulario
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.get("email"))) {
        showError("email", "Ingrese un correo electrónico válido.");
        isValid = false;
    }

    if (!/^\+57[0-9]{10}$/.test(formData.get("phoneNumber"))) {
        showError("phoneNumber", "Ingrese un número de teléfono válido con el formato +57 seguido de 10 dígitos.");
        isValid = false;
    }

    if (formData.get("firstName").trim().length < 3) {
        showError("firstName", "El nombre debe tener al menos 3 caracteres.");
        isValid = false;
    }

    if (formData.get("lastName").trim().length < 3) {
        showError("lastName", "El apellido debe tener al menos 3 caracteres.");
        isValid = false;
    }

    if (!formData.get("gender")) {
        showError("gender", "Debe seleccionar un género.");
        isValid = false;
    }

    if (!formData.get("birthDate")) {
        showError("birthDate", "Debe ingresar una fecha de nacimiento.");
        isValid = false;
    }

    if (!formData.get("educationLevel")) {
        showError("educationLevel", "Debe seleccionar un nivel educativo.");
        isValid = false;
    }

    if (!formData.get("technicalSkills")) {
        showError("technicalSkills", "Debe ingresar al menos una habilidad técnica.");
        isValid = false;
    } else {
        let skills = formData.get("technicalSkills").split(",").map(skill => skill.trim());
        if (skills.some(skill => skill.length > 20)) {
            showError("technicalSkills", "Cada habilidad técnica debe tener menos de 20 caracteres.");
            isValid = false;
        }
    }

    if (isNaN(parseFloat(formData.get("interviewScore"))) || parseFloat(formData.get("interviewScore")) < 0 || parseFloat(formData.get("interviewScore")) > 10) {
        showError("interviewScore", "Ingrese una puntuación válida para la entrevista (0-10).");
        isValid = false;
    }

    if (isNaN(parseInt(formData.get("technicalTestScore"))) || parseInt(formData.get("technicalTestScore")) < 0 || parseInt(formData.get("technicalTestScore")) > 100) {
        showError("technicalTestScore", "Ingrese una puntuación válida para el test técnico (0-100).");
        isValid = false;
    }

    if (!formData.get("availability")) {
        showError("availability", "Debe seleccionar disponibilidad.");
        isValid = false;
    }

    if (isNaN(parseFloat(formData.get("salaryExpectation")))) {
        showError("salaryExpectation", "Ingrese una expectativa salarial válida.");
        isValid = false;
    }

    if (!formData.get("companyInterest")) {
        showError("companyInterest", "Debe seleccionar un nivel de interés en la empresa.");
        isValid = false;
    }
    
    if (!formData.get("location")) {
        showError("location", "Debe ingresar una ubicación.");
        isValid = false;
    }

    if (isNaN(parseInt(formData.get("experience"))) || parseInt(formData.get("experience")) < 0) {
        showError("experience", "Ingrese una experiencia válida en años.");
        isValid = false;
    }

    if (!formData.get("softSkills")) {
        showError("softSkills", "Debe ingresar al menos una habilidad blanda.");
        isValid = false;
    }

    if (!formData.get("workPreference")) {
        showError("workPreference", "Debe seleccionar una preferencia de trabajo.");
        isValid = false;
    }

    // Si no hay errores, envía la solicitud al servidor
    if (isValid) {
        const data = Object.fromEntries(formData.entries());
        data.technicalSkills = data.technicalSkills.split(",").map(skill => skill.trim());
        data.softSkills = data.softSkills.split(",").map(skill => skill.trim());
        data.interviewScore = parseFloat(data.interviewScore);
        data.technicalTestScore = parseInt(data.technicalTestScore);
        data.salaryExpectation = parseFloat(data.salaryExpectation);
        data.experience = parseInt(data.experience);

        try {
            const response = await fetch("http://localhost:5000/add_candidate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                alert("✅ Candidato registrado con éxito!");
                this.reset();
            } else {
                showBackendErrors(result.error);
            }
        } catch (error) {
            console.error("Error en la solicitud:", error);
            showBackendErrors("⚠️ Error al conectar con el servidor");
        }
    }
});

const formData = new FormData(document.querySelector("form"));
console.log("Valor educationLevel antes de enviar:", formData.get("educationLevel"));



