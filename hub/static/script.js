document.addEventListener("DOMContentLoaded", () => {
    // Current Active Charts (to allow destroying before recreation)
    let categoryChart = null;
    let patientChart = null;
    let trendChart = null;
    let doctorChart = null;

    // Database state
    let receiptsHistory = [];

    // Force clear browser autofill on page load and during events
    const chatInput = document.getElementById("chat-user-textbox");
    if (chatInput) {
        const preventAutofill = () => {
            if (chatInput.value.toLowerCase().trim() === "gemini api key") {
                chatInput.value = "";
            }
        };
        chatInput.addEventListener("input", preventAutofill);
        chatInput.addEventListener("change", preventAutofill);
        chatInput.addEventListener("focus", preventAutofill);
        
        chatInput.value = "";
        setTimeout(() => { chatInput.value = ""; }, 100);
        setTimeout(() => { chatInput.value = ""; }, 500);
    }

    // --- Tab Switching Logic ---
    const navItems = document.querySelectorAll(".nav-item");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const subtext = document.getElementById("workspace-subtext");

    const tabSubtexts = {
        dashboard: "Comprehensive medical spending analytics and AI diagnostics hub.",
        receipts: "OpenCV-optimized computer vision scanner and clinical OCR parser.",
        symptoms: "Deep learning PyTorch Transformer disease classifier and severity regressor.",
        assistant: "Local RAG assistant for Indian medicines and Jaipur pharmacy locator."
    };

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const tabId = item.getAttribute("data-tab");
            
            navItems.forEach(i => i.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));
            
            item.classList.add("active");
            document.getElementById(`${tabId}-pane`).classList.add("active");
            subtext.innerText = tabSubtexts[tabId] || "";

            // Special trigger when entering dashboard
            if (tabId === "dashboard") {
                loadDashboardAnalytics();
            }
        });
    });

    // --- Global Sync / Refresh Action ---
    const globalRefreshBtn = document.getElementById("global-refresh-btn");
    globalRefreshBtn.addEventListener("click", () => {
        globalRefreshBtn.classList.add("fa-spin");
        loadDashboardAnalytics().finally(() => {
            setTimeout(() => {
                globalRefreshBtn.classList.remove("fa-spin");
            }, 600);
        });
    });

    // --- Format currency utility ---
    function formatINR(value) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 2
        }).format(value);
    }

    // --- Chart.js Palette configurations ---
    const chartColors = [
        '#0d9488', // Teal
        '#4f46e5', // Indigo
        '#8b5cf6', // Accent Purple
        '#ec4899', // Pink
        '#f59e0b', // Amber
        '#10b981', // Emerald
        '#ef4444'  // Red
    ];

    // --- TAB 1: Load Dashboard Analytics & SQL History ---
    async function loadDashboardAnalytics() {
        try {
            const res = await fetch("/api/analytics");
            const data = await res.json();

            // Populate metrics
            document.getElementById("stat-total-spent").innerText = formatINR(data.metrics.total_spent || 0);
            document.getElementById("stat-total-visits").innerText = data.metrics.total_visits || 0;
            document.getElementById("stat-patients-count").innerText = data.metrics.patients_count || 0;

            // Render category chart
            renderCategorySpend(data.category_data);
            
            // Render patient spend
            renderPatientSpend(data.patient_data);

            // Render monthly trends
            renderMonthlyTrend(data.monthly_data);

            // Render doctor costs
            renderDoctorSpend(data.doctor_data);

            // Load logs table
            await loadLogsTable();

        } catch (err) {
            console.error("Dashboard load failed: ", err);
        }
    }

    function renderCategorySpend(catData) {
        const ctx = document.getElementById("chart-category").getContext("2d");
        if (categoryChart) categoryChart.destroy();

        if (!catData || catData.length === 0) {
            catData = [{category: "No Data", total_amount: 0}];
        }

        categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: catData.map(c => c.category),
                datasets: [{
                    data: catData.map(c => c.total_amount),
                    backgroundColor: chartColors,
                    borderWidth: 1,
                    borderColor: 'rgba(255, 255, 255, 0.05)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#9ca3af', font: { family: 'Inter' } }
                    }
                }
            }
        });
    }

    function renderPatientSpend(patData) {
        const ctx = document.getElementById("chart-patients").getContext("2d");
        if (patientChart) patientChart.destroy();

        patientChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: patData.map(p => p.patient_name),
                datasets: [{
                    label: 'Spent Share (₹)',
                    data: patData.map(p => p.total_amount),
                    backgroundColor: 'rgba(79, 70, 229, 0.75)',
                    borderColor: '#6366f1',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#9ca3af' }, grid: { display: false } },
                    y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255, 255, 255, 0.04)' } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    function renderMonthlyTrend(monthlyData) {
        const ctx = document.getElementById("chart-trend").getContext("2d");
        if (trendChart) trendChart.destroy();

        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: monthlyData.map(m => m.YearMonth),
                datasets: [{
                    label: 'Spent by Month (₹)',
                    data: monthlyData.map(m => m.total_amount),
                    borderColor: '#ec4899',
                    backgroundColor: 'rgba(236, 72, 153, 0.1)',
                    borderWidth: 2.5,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#ec4899'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#9ca3af' }, grid: { display: false } },
                    y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255, 255, 255, 0.04)' } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    function renderDoctorSpend(docData) {
        const ctx = document.getElementById("chart-doctors").getContext("2d");
        if (doctorChart) doctorChart.destroy();

        doctorChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: docData.map(d => d.doctor_or_hospital),
                datasets: [{
                    label: 'Consultation Spend (₹)',
                    data: docData.map(d => d.total_amount),
                    backgroundColor: 'rgba(13, 148, 136, 0.75)',
                    borderColor: '#2dd4bf',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y', // Makes it horizontal
                scales: {
                    x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255, 255, 255, 0.04)' } },
                    y: { ticks: { color: '#9ca3af' }, grid: { display: false } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    async function loadLogsTable() {
        try {
            const res = await fetch("/api/receipts");
            receiptsHistory = await res.json();

            const tbody = document.getElementById("history-table-body");
            tbody.innerHTML = "";

            if (receiptsHistory.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center">No receipt entries stored. Parse an image in MedReceipt OCR to commit records.</td></tr>`;
                return;
            }

            receiptsHistory.forEach(row => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${row.id}</td>
                    <td><strong>${row.patient_name}</strong></td>
                    <td>${row.doctor_or_hospital}</td>
                    <td>${row.date || "N/A"}</td>
                    <td><span class="category-badge category-${(row.category || "Other").replace(" ", "_")}">${row.category}</span></td>
                    <td>₹${(row.total_amount || 0).toFixed(2)}</td>
                    <td>
                        <div style="display: flex; gap: 0.35rem; justify-content: center; align-items: center;">
                            <button class="btn btn-sm btn-secondary inspect-btn" data-id="${row.id}" title="Inspect Record"><i class="fa-solid fa-eye"></i></button>
                            <button class="btn btn-sm btn-secondary delete-btn" data-id="${row.id}" title="Delete Record" style="background-color: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #ef4444;"><i class="fa-solid fa-trash-can"></i></button>
                        </div>
                    </td>
                `;
                
                // Clicking inspect button
                tr.querySelector(".inspect-btn").addEventListener("click", (e) => {
                    e.stopPropagation();
                    inspectRecord(row.id);
                });

                // Clicking delete button
                tr.querySelector(".delete-btn").addEventListener("click", (e) => {
                    e.stopPropagation();
                    if (confirm(`Are you sure you want to delete receipt #${row.id} for ${row.patient_name}?`)) {
                        deleteRecord(row.id);
                    }
                });

                // Clicking row inspects it too
                tr.addEventListener("click", () => inspectRecord(row.id));
                tbody.appendChild(tr);
            });

        } catch (err) {
            console.error("Failed to load sqlite logs: ", err);
        }
    }

    async function deleteRecord(recordId) {
        try {
            const res = await fetch(`/api/receipts/${recordId}`, {
                method: "DELETE"
            });
            if (res.ok) {
                // If the currently inspected record was deleted, hide inspector content
                const currentInspected = receiptsHistory.find(r => r.id === parseInt(recordId));
                const inspectPlaceholder = document.getElementById("inspector-placeholder");
                const inspectContent = document.getElementById("inspector-content");
                if (inspectContent && !inspectContent.classList.contains("hidden")) {
                    const inspectedPatient = document.getElementById("inspect-patient").innerText;
                    if (currentInspected && currentInspected.patient_name === inspectedPatient) {
                        inspectPlaceholder.classList.remove("hidden");
                        inspectContent.classList.add("hidden");
                    }
                }
                
                await loadDashboardAnalytics();
            } else {
                alert("Failed to delete record.");
            }
        } catch (err) {
            console.error("Delete record failed: ", err);
        }
    }

    function inspectRecord(recordId) {
        const record = receiptsHistory.find(r => r.id === parseInt(recordId));
        if (!record) return;

        document.getElementById("inspector-placeholder").classList.add("hidden");
        const inspectContent = document.getElementById("inspector-content");
        inspectContent.classList.remove("hidden");

        // Fill metadata
        document.getElementById("inspect-patient").innerText = record.patient_name;
        document.getElementById("inspect-doctor").innerText = record.doctor_or_hospital;
        document.getElementById("inspect-date").innerText = record.date || "N/A";
        document.getElementById("inspect-diagnosis").innerText = record.diagnosis_or_symptoms || "N/A";
        document.getElementById("inspect-cost").innerText = formatINR(record.total_amount || 0);

        // Fill badge classes
        const catBadge = document.getElementById("inspect-category");
        catBadge.innerText = record.category;
        catBadge.className = `category-badge category-${(record.category || "Other").replace(" ", "_")}`;

        // Populate medicines table
        const medsBody = document.getElementById("inspect-meds-body");
        medsBody.innerHTML = "";
        
        try {
            const meds = JSON.parse(record.medicines_json || "[]");
            if (meds.length === 0) {
                medsBody.innerHTML = `<tr><td colspan="3" class="text-muted text-center">No medicines attached to this receipt.</td></tr>`;
            } else {
                meds.forEach(m => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>${m.name || "N/A"}</strong></td>
                        <td>${m.dosage || "N/A"}</td>
                        <td>₹${parseFloat(m.price || 0).toFixed(2)}</td>
                    `;
                    medsBody.appendChild(tr);
                });
            }
        } catch (err) {
            medsBody.innerHTML = `<tr><td colspan="3" class="text-center text-danger">Error parsing medicines structure.</td></tr>`;
        }
    }

    // --- TAB 2: MEDRECEIPT OCR ---
    const ocrProvider = document.getElementById("ocr-provider");
    const geminiKeyWrapper = document.getElementById("gemini-key-wrapper");
    const ollamaUrlWrapper = document.getElementById("ollama-url-wrapper");
    const ollamaModelWrapper = document.getElementById("ollama-model-wrapper");

    // Toggle credentials options depending on provider
    ocrProvider.addEventListener("change", () => {
        if (ocrProvider.value === "ollama") {
            geminiKeyWrapper.classList.add("hidden");
            ollamaUrlWrapper.classList.remove("hidden");
            ollamaModelWrapper.classList.remove("hidden");
        } else {
            geminiKeyWrapper.classList.remove("hidden");
            ollamaUrlWrapper.classList.add("hidden");
            ollamaModelWrapper.classList.add("hidden");
        }
    });

    const dropzone = document.getElementById("upload-dropzone");
    const fileInput = document.getElementById("file-input");
    const selectFileBtn = document.getElementById("select-file-btn");

    selectFileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    dropzone.addEventListener("click", () => fileInput.click());

    // Drag-over hover indicators
    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.style.borderColor = "var(--color-accent)";
        dropzone.style.background = "rgba(139, 92, 246, 0.04)";
    });

    ["dragleave", "drop"].forEach(event => {
        dropzone.addEventListener(event, () => {
            dropzone.style.borderColor = "rgba(13, 148, 136, 0.3)";
            dropzone.style.background = "rgba(13, 148, 136, 0.02)";
        });
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    // Save state of raw json
    let currentRawJson = {};

    async function handleFileUpload(file) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("provider", ocrProvider.value);
        formData.append("gemini_key", document.getElementById("ocr-gemini-key").value);
        formData.append("ollama_url", document.getElementById("ocr-ollama-url").value);
        formData.append("ollama_model", document.getElementById("ocr-ollama-model").value);

        // Show status card loader
        const statusCard = document.getElementById("upload-status-card");
        const statusTitle = document.getElementById("ocr-status-title");
        const statusDesc = document.getElementById("ocr-status-desc");
        const ocrLoader = document.getElementById("ocr-loader");
        const previewWrapper = document.getElementById("image-preview-wrapper");
        const saveBtn = document.getElementById("save-receipt-btn");

        statusCard.classList.remove("hidden");
        ocrLoader.classList.remove("hidden");
        statusTitle.innerText = "Extracting receipt data...";
        statusDesc.innerText = "Running OpenCV pre-processing & AI parsing pipelines...";
        previewWrapper.classList.add("hidden");
        saveBtn.disabled = true;

        try {
            const res = await fetch("/api/scan", {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Server failed to scan image.");
            }

            const data = await res.json();

            // Success loading preview & parsed forms
            statusTitle.innerText = "Extraction Complete!";
            statusDesc.innerText = "Check parsed details in the workspace card.";
            ocrLoader.classList.add("hidden");

            // Preview base64 optimized image
            if (data.processed_image_b64) {
                document.getElementById("processed-img-preview").src = data.processed_image_b64;
                previewWrapper.classList.remove("hidden");
            }

            // Fill text fields
            document.getElementById("edit-patient").value = data.patient_name || "Unknown";
            document.getElementById("edit-doctor").value = data.doctor_or_hospital || "Unknown";
            document.getElementById("edit-date").value = data.date || "";
            document.getElementById("edit-amount").value = parseFloat(data.total_amount || 0);
            document.getElementById("edit-category").value = data.category || "Other";
            document.getElementById("edit-diagnosis").value = data.diagnosis_or_symptoms || "";

            // Populate interactive medicines table
            populateEditableMedsTable(data.medicines);

            currentRawJson = data;
            saveBtn.disabled = false;

        } catch (err) {
            statusTitle.innerText = "Scan failed";
            statusDesc.innerText = err.message;
            ocrLoader.classList.add("hidden");
            console.error("Scan failed: ", err);
        }
    }

    function populateEditableMedsTable(meds) {
        const medsBody = document.getElementById("editable-meds-body");
        medsBody.innerHTML = "";

        if (!meds || meds.length === 0) {
            medsBody.innerHTML = `<tr class="empty-row-msg"><td colspan="4" class="text-center">No medicines parsed. Click Add Row to add details.</td></tr>`;
            return;
        }

        meds.forEach(m => addEditableRow(m.name, m.dosage, m.price));
    }

    function addEditableRow(name = "", dosage = "", price = "") {
        const medsBody = document.getElementById("editable-meds-body");
        const emptyMsg = medsBody.querySelector(".empty-row-msg");
        if (emptyMsg) emptyMsg.remove();

        const tr = document.createElement("tr");
        tr.className = "medicine-row";
        tr.innerHTML = `
            <td><input type="text" class="med-name" value="${name || ""}" placeholder="Medicine Name"></td>
            <td><input type="text" class="med-dosage" value="${dosage || ""}" placeholder="Dosage/Frequency"></td>
            <td><input type="number" class="med-price" value="${price || ""}" step="0.01" placeholder="0.00"></td>
            <td class="text-center"><button type="button" class="btn-remove-row"><i class="fa-solid fa-trash-can"></i></button></td>
        `;

        // Trash action listener
        tr.querySelector(".btn-remove-row").addEventListener("click", () => {
            tr.remove();
            if (medsBody.querySelectorAll(".medicine-row").length === 0) {
                medsBody.innerHTML = `<tr class="empty-row-msg"><td colspan="4" class="text-center">No medicines parsed. Click Add Row to add details.</td></tr>`;
            }
        });

        medsBody.appendChild(tr);
    }

    document.getElementById("add-table-row-btn").addEventListener("click", () => addEditableRow());

    // COMMIT RECORD TO SQLITE
    const saveReceiptBtn = document.getElementById("save-receipt-btn");
    saveReceiptBtn.addEventListener("click", async () => {
        // Collect medicines list
        const medRows = document.querySelectorAll(".medicine-row");
        const medsList = [];
        medRows.forEach(row => {
            const name = row.querySelector(".med-name").value.trim();
            const dosage = row.querySelector(".med-dosage").value.trim();
            const price = row.querySelector(".med-price").value;

            if (name) {
                medsList.push({
                    name: name,
                    dosage: dosage || null,
                    price: price ? parseFloat(price) : null
                });
            }
        });

        const payload = {
            patient_name: document.getElementById("edit-patient").value.trim(),
            doctor_or_hospital: document.getElementById("edit-doctor").value.trim(),
            date: document.getElementById("edit-date").value.trim(),
            total_amount: parseFloat(document.getElementById("edit-amount").value || 0),
            category: document.getElementById("edit-category").value,
            diagnosis_or_symptoms: document.getElementById("edit-diagnosis").value.trim(),
            medicines_json: JSON.stringify(medsList),
            raw_text: JSON.stringify(currentRawJson)
        };

        const statusMsg = document.getElementById("save-status-msg");
        statusMsg.innerText = "Saving record...";
        statusMsg.className = "save-status-message mt-2 text-center text-muted";

        try {
            const res = await fetch("/api/receipts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("Could not commit record to database.");

            statusMsg.innerText = "✅ Record saved successfully! Check Dashboard.";
            statusMsg.className = "save-status-message mt-2 text-center text-success";
            
            // Sync analytics
            loadDashboardAnalytics();
            saveReceiptBtn.disabled = true;

        } catch (err) {
            statusMsg.innerText = `❌ Error: ${err.message}`;
            statusMsg.className = "save-status-message mt-2 text-center text-danger";
        }
    });

    // --- TAB 3: SYMBOT CHECKER ---
    const diagnoseBtn = document.getElementById("diagnose-btn");
    const clearSymptomsBtn = document.getElementById("clear-symptoms-btn");
    const symptomInputText = document.getElementById("symptom-input-text");

    clearSymptomsBtn.addEventListener("click", () => {
        symptomInputText.value = "";
        document.getElementById("sym-placeholder").classList.remove("hidden");
        document.getElementById("sym-results-content").classList.add("hidden");
    });

    diagnoseBtn.addEventListener("click", async () => {
        const text = symptomInputText.value.trim();
        if (!text) return;

        diagnoseBtn.disabled = true;
        diagnoseBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...`;
        
        const payload = {
            text: text,
            ollama_url: document.getElementById("sym-ollama-url").value,
            ollama_model: document.getElementById("sym-ollama-model").value
        };

        try {
            const res = await fetch("/api/symptoms", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            document.getElementById("sym-placeholder").classList.add("hidden");
            document.getElementById("sym-results-content").classList.remove("hidden");

            // Detected Symptoms
            const tagsCloud = document.getElementById("detected-symptoms-cloud");
            tagsCloud.innerHTML = "";
            data.symptoms.forEach(s => {
                const span = document.createElement("span");
                span.className = "detected-tag";
                span.innerText = s;
                tagsCloud.appendChild(span);
            });

            // Severity Meter
            document.getElementById("severity-score-val").innerText = data.severity.toFixed(2);
            const meterFill = document.getElementById("severity-meter-fill");
            const pct = Math.min((data.severity / 7) * 100, 100);
            meterFill.style.width = `${pct}%`;

            // Severity alert details
            const alertBanner = document.getElementById("severity-alert-banner");
            if (data.severity > 4.5) {
                alertBanner.className = "alert alert-red mt-2";
                alertBanner.innerHTML = `⚠️ <strong>High Severity!</strong> Custom regressor score indicates potential high clinical risk. Consult a physician immediately.`;
            } else if (data.severity >= 2.5) {
                alertBanner.className = "alert alert-yellow mt-2";
                alertBanner.innerHTML = `🩺 <strong>Moderate Severity:</strong> Keep watch on condition logs. Consult a physician if symptoms do not improve.`;
            } else {
                alertBanner.className = "alert alert-green mt-2";
                alertBanner.innerHTML = `✅ <strong>Mild Severity:</strong> Symptoms do not show high clinical indicators. Standard home care is recommended.`;
            }

            // Top predictions list
            const predList = document.getElementById("pytorch-predictions-list");
            predList.innerHTML = "";
            data.predictions.forEach(p => {
                const row = document.createElement("div");
                row.className = "pred-row";
                row.innerHTML = `
                    <span class="disease-name">${p.disease}</span>
                    <div class="prob-indicator">
                        <span class="prob-pct">${(p.probability * 100).toFixed(1)}%</span>
                    </div>
                `;
                predList.appendChild(row);
            });

            // Validator log
            document.getElementById("validator-explanation-log").innerText = data.explanation;

        } catch (err) {
            console.error("Diagnostic failure: ", err);
            alert("Symptoms diagnostics failed. Please make sure Ollama server is accessible.");
        } finally {
            diagnoseBtn.disabled = false;
            diagnoseBtn.innerHTML = `<i class="fa-solid fa-brain"></i> Analyze Symptoms`;
        }
    });

    // Populate tags examples clicks
    const exampleTags = document.querySelectorAll(".example-tag");
    exampleTags.forEach(tag => {
        tag.addEventListener("click", () => {
            symptomInputText.value = tag.innerText;
            diagnoseBtn.click();
        });
    });

    // --- TAB 4: MEDIBOT ASSISTANT ---
    const chatSendBtn = document.getElementById("chat-send-btn");
    const chatUserTextbox = document.getElementById("chat-user-textbox");
    const chatMessagesBody = document.getElementById("chat-messages-body");
    const chatAreaInput = document.getElementById("chat-area-input");
    const pharmacyResultsList = document.getElementById("pharmacy-results-list");

    // Locality area changes triggers stores lookup
    chatAreaInput.addEventListener("change", () => {
        const area = chatAreaInput.value;
        if (area) {
            updateNearestStores(area);
        } else {
            pharmacyResultsList.innerHTML = `<div class="placeholder-state-mini"><p>Select a Jaipur area above to look up closest medical shops.</p></div>`;
        }
    });

    async function updateNearestStores(area) {
        pharmacyResultsList.innerHTML = `<div class="text-center py-3"><i class="fa-solid fa-spinner fa-spin"></i> Locating shops...</div>`;
        try {
            // Run a dummy medicine lookup to trigger nearest stores
            const res = await fetch("/api/medicine", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: "Get nearby pharmacy stores",
                    area: area,
                    ollama_url: document.getElementById("chat-ollama-url").value,
                    ollama_model: document.getElementById("chat-ollama-model").value
                })
            });

            const data = await res.json();
            pharmacyResultsList.innerHTML = "";

            if (!data.stores || data.stores.length === 0) {
                pharmacyResultsList.innerHTML = `<div class="placeholder-state-mini"><p>No stores found in "${area}". Try Mansarovar, Malviya Nagar or Vaishali Nagar.</p></div>`;
                return;
            }

            data.stores.forEach(s => {
                const card = document.createElement("div");
                card.className = "store-result-card";
                card.innerHTML = `
                    <h5>${s.name}</h5>
                    <div class="store-meta">
                        <span><i class="fa-solid fa-location-dot"></i> ${s.locality}</span>
                        <span><i class="fa-solid fa-star"></i> ${s.rating}</span>
                        <span><i class="fa-solid fa-clock"></i> ${s.hours}</span>
                    </div>
                    <p class="store-address">${s.address}</p>
                    <div class="store-actions">
                        <span><i class="fa-solid fa-truck"></i> ${s.delivery}</span>
                        <a href="${s.map_link}" target="_blank"><i class="fa-solid fa-arrow-up-right-from-square"></i> Open Maps</a>
                    </div>
                `;
                pharmacyResultsList.appendChild(card);
            });

        } catch (err) {
            console.error("Nearest stores fetch failed: ", err);
            pharmacyResultsList.innerHTML = `<div class="placeholder-state-mini"><p class="text-danger">Failed to match pharmacies.</p></div>`;
        }
    }

    async function submitChatMessage(msgText) {
        if (!msgText.trim()) return;

        // User message bubble
        appendChatBubble(msgText, "user");
        chatUserTextbox.value = "";
        setTimeout(() => { chatUserTextbox.value = ""; }, 50);
        setTimeout(() => { chatUserTextbox.value = ""; }, 150);

        // Loader bubble
        const loadBubble = appendChatBubble(`<i class="fa-solid fa-ellipsis fa-bounce"></i> Parsing RAG context...`, "bot");

        const payload = {
            question: msgText,
            area: chatAreaInput.value || null,
            ollama_url: document.getElementById("chat-ollama-url").value,
            ollama_model: document.getElementById("chat-ollama-model").value
        };

        try {
            const res = await fetch("/api/medicine", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            // Replace loading bubble text
            loadBubble.innerText = data.answer || "No response received.";

            // If stores matches are returned and an area was selected, refresh stores list
            if (data.stores && data.stores.length > 0 && chatAreaInput.value) {
                updateNearestStores(chatAreaInput.value);
            }

        } catch (err) {
            loadBubble.innerText = `Error contacting local LLM. Verify Ollama is serving on the backend.`;
            console.error("Chat message send failed: ", err);
        }
    }

    function appendChatBubble(text, sender) {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble chat-bubble-${sender}`;
        
        if (sender === "bot" && text.includes("<i")) {
            bubble.innerHTML = text; // allow loading icons HTML
        } else {
            bubble.innerText = text;
        }

        chatMessagesBody.appendChild(bubble);
        chatMessagesBody.scrollTop = chatMessagesBody.scrollHeight;
        return bubble;
    }

    chatSendBtn.addEventListener("click", () => submitChatMessage(chatUserTextbox.value));
    chatUserTextbox.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            submitChatMessage(chatUserTextbox.value);
        }
    });

    // Chat Suggestion Chips clicks
    const suggestionBtns = document.querySelectorAll(".suggestion-btn");
    suggestionBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            submitChatMessage(btn.innerText);
        });
    });

    // Clear all records click event listener
    const clearAllDbBtn = document.getElementById("clear-all-db-btn");
    if (clearAllDbBtn) {
        clearAllDbBtn.addEventListener("click", async () => {
            if (confirm("Are you sure you want to delete ALL receipt logs? This action cannot be undone.")) {
                try {
                    const res = await fetch("/api/receipts", {
                        method: "DELETE"
                    });
                    if (res.ok) {
                        // Reset inspector view
                        const inspectPlaceholder = document.getElementById("inspector-placeholder");
                        const inspectContent = document.getElementById("inspector-content");
                        if (inspectPlaceholder && inspectContent) {
                            inspectPlaceholder.classList.remove("hidden");
                            inspectContent.classList.add("hidden");
                        }
                        await loadDashboardAnalytics();
                    } else {
                        alert("Failed to clear database records.");
                    }
                } catch (err) {
                    console.error("Clear database failed: ", err);
                }
            }
        });
    }

    // --- On Initial Load ---
    loadDashboardAnalytics();
});
