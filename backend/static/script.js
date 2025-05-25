document.addEventListener('DOMContentLoaded', function () {
    const BASE_URL = window.location.hostname.includes("localhost") || window.location.hostname.includes("127.")
        ? "http://localhost:5000"
        : "https://los-colados.onrender.com";

    // Inicializar selects con Choices.js
    const allSelects = document.querySelectorAll('select');
    allSelects.forEach(select => {
        new Choices(select, {
            removeItemButton: select.multiple,
            placeholderValue: 'Selecciona una opción',
            searchEnabled: false
        });
    });

    // Evento envío de formulario
    document.getElementById("candidateForm").addEventListener("submit", async function (event) {
        event.preventDefault();

        const birthDateInput = document.querySelector("input[name='birthDate']");
        const birthDate = new Date(birthDateInput.value);
        const today = new Date();
        const age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        const dayDiff = today.getDate() - birthDate.getDate();

        const is18OrOlder =
            age > 18 ||
            (age === 18 && (monthDiff > 0 || (monthDiff === 0 && dayDiff >= 0)));

        if (!is18OrOlder) {
            showError("birthDate","⚠️ Debes tener al menos 18 años para enviar el formulario.");
            return;
        }

        const formData = new FormData(this);
        let isValid = true;

        const educationMap = {
            "secundaria": 1, "tecnico": 2, "tecnologo": 3,
            "universitario": 4, "postgrado": 5
        };
        if (formData.get("educationLevel")) {
            formData.set("educationLevel", educationMap[formData.get("educationLevel")] || 0);
        }

        document.querySelectorAll(".error-message").forEach(msg => msg.remove());
        document.querySelectorAll(".input-field").forEach(field => field.classList.remove("error"));

        function showError(inputName, message) {
            const inputElement = document.querySelector(`[name="${inputName}"]`);
            if (!inputElement) return;
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
            }
        }

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

        if (!formData.getAll("technicalSkills").length) {
            showError("technicalSkills", "Debe seleccionar al menos una habilidad técnica.");
            isValid = false;
        }

        if (isNaN(parseFloat(formData.get("interviewScore"))) ||
            parseFloat(formData.get("interviewScore")) < 0 || parseFloat(formData.get("interviewScore")) > 10) {
            showError("interviewScore", "Ingrese una puntuación válida para la entrevista (0-10).");
            isValid = false;
        }

        if (isNaN(parseInt(formData.get("technicalTestScore"))) ||
            parseInt(formData.get("technicalTestScore")) < 0 || parseInt(formData.get("technicalTestScore")) > 100) {
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

        if (!formData.get("location")) {
            showError("location", "Debe ingresar una ubicación.");
            isValid = false;
        }

        if (isNaN(parseInt(formData.get("experience"))) || parseInt(formData.get("experience")) < 0) {
            showError("experience", "Ingrese una experiencia válida en años.");
            isValid = false;
        }

        if (isNaN(parseInt(formData.get("icfes"))) || parseInt(formData.get("icfes")) < 0 || parseInt(formData.get("icfes")) > 500) {
            showError("icfes", "Ingrese un puntaje ICFES válido (0-500).");
            isValid = false;
        }

        if (!formData.getAll("softSkills").length) {
            showError("softSkills", "Debe seleccionar al menos una habilidad blanda.");
            isValid = false;
        }

        if (!formData.getAll("languages").length) {
            showError("languages", "Debe seleccionar al menos un idioma.");
            isValid = false;
        }

        if (!formData.get("workPreference")) {
            showError("workPreference", "Debe seleccionar una preferencia de trabajo.");
            isValid = false;
        }

        if (!formData.getAll("personalStrengths").length) {
            showError("personalStrengths", "Debe seleccionar al menos una fortaleza personal.");
            isValid = false;
        }

        // Verificar en el backend si ya existe el correo o teléfono
        try {
            const verificarResp = await fetch(`${BASE_URL}/verificar_existencia`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: formData.get("email"),
                    phoneNumber: formData.get("phoneNumber")
                })
            });

            const verificarData = await verificarResp.json();

            if (verificarData.emailExiste) {
                showError("email", "⚠️ Este correo electrónico ya está registrado.");
                isValid = false;
            }

            if (verificarData.telefonoExiste) {
                showError("phoneNumber", "⚠️ Este número de teléfono ya está registrado.");
                isValid = false;
            }

        } catch (error) {
            console.error("Error al verificar existencia en la base de datos:", error);
            showBackendErrors("⚠️ Error al verificar si el correo o teléfono ya están registrados.");
            return;
        }

        if (isValid) {
            const data = Object.fromEntries(formData.entries());
            data.interviewScore = parseFloat(data.interviewScore);
            data.technicalTestScore = parseInt(data.technicalTestScore);
            data.salaryExpectation = parseFloat(data.salaryExpectation);
            data.experience = parseInt(data.experience);
            data.technicalSkills = formData.getAll("technicalSkills");
            data.softSkills = formData.getAll("softSkills");
            data.personalStrengths = formData.getAll("personalStrengths");
            data.languages = formData.getAll("languages");
            data.careerInterest = formData.get("careerInterest");
            data.shortTermGoal = formData.get("shortTermGoal");
            data.icfes = parseInt(formData.get("icfes"));

            try {
                const response = await fetch(`${BASE_URL}/add_candidate`, {
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

    // Mostrar mejor candidato
    document.getElementById("showBestCandidate")?.addEventListener("click", async function () {
        const clave = prompt("🔐 Ingresa la clave de acceso:");
        if (clave !== "disruptive123") {
            alert("❌ Clave incorrecta");
            return;
        }

        try {
            const response = await fetch(`${BASE_URL}/mejor_candidato`);
            const result = await response.json();
            if (response.ok) {
                const mejor = result.mejor_candidato;
                const container = document.getElementById("bestCandidateResult");
                container.innerHTML = `
                    <h3>🏆 Mejor Candidato</h3>
                    <p><strong>Nombre:</strong> ${mejor.first_name} ${mejor.last_name}</p>
                    <p><strong>Correo:</strong> ${mejor.email}</p>
                    <p><strong>Puntaje total:</strong> ${mejor.total_score.toFixed(2)}</p>
                `;
            } else {
                alert("Error al obtener candidato: " + result.error);
            }
        } catch (err) {
            alert("⚠️ No se pudo conectar con el servidor.");
            console.error(err);
        }
    });

    // Acceso a página de administrador
    document.getElementById("adminAccessBtn")?.addEventListener("click", function () {
        const clave = prompt("🔐 Ingresa la clave de administrador:");
        if (clave === "disruptive123") {
            window.location.href = "/admin";
        } else {
            alert("❌ Clave incorrecta");
        }
    });

    // Generar datos con Faker
    document.getElementById("generateDataBtn")?.addEventListener("click", async function () {
        const confirmacion = confirm("¿Deseas generar 10 nuevos candidatos con Faker?");
        if (!confirmacion) return;

        try {
            const response = await fetch(`${BASE_URL}/generar_datos`, {
                method: "POST"
            });

            const result = await response.json();
            if (response.ok) {
                alert(result.message || "✅ Datos generados correctamente");
            } else {
                alert("⚠️ Error: " + result.error);
            }
        } catch (error) {
            console.error("❌ Error al generar datos:", error);
            alert("⚠️ No se pudo conectar con el servidor.");
        }
    });

    function showBackendErrors(errorMessage) {
        alert("⚠️ Error del servidor: " + errorMessage);
        console.error("Backend error:", errorMessage);
    }
});



