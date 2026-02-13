function scrollSlider(direction) {
    const track = document.getElementById('categoryTrack');
    if (track) {
        track.scrollBy({
            left: direction * 300,
            behavior: 'smooth'
        });
    }
}

document.addEventListener("DOMContentLoaded", function () {

    const cat = document.getElementById("category");
    const gen = document.getElementById("genre");

    // ======================
    // Custom category/genre
    // ======================

    if (cat) {
        cat.addEventListener("change", function () {
            const text = cat.options[cat.selectedIndex].text;
            document.getElementById("custom-category")
                ?.classList.toggle("d-none", text !== "Others");
        });
    }

    if (gen) {
        gen.addEventListener("change", function () {
            const text = gen.options[gen.selectedIndex].text;
            document.getElementById("custom-genre")
                ?.classList.toggle("d-none", text !== "Others");
        });
    }

    // ======================
    // Image preview
    // ======================

    const fileInput = document.querySelector('input[type=file]');
    if (fileInput) {
        fileInput.addEventListener("change", e => {
            const img = document.getElementById("preview");
            if (img) {
                img.src = URL.createObjectURL(e.target.files[0]);
                img.style.display = "block";
            }
        });
    }

    // ======================
    // Django toast auto-remove
    // ======================

    setTimeout(() => {
        document.querySelectorAll('.toast').forEach(t => t.remove());
    }, 3000);

    // ======================
    // Placeholder select color
    // ======================

    document.querySelectorAll(".placeholder-select").forEach(select => {

        select.style.color = select.value === "" ? "#6c757d" : "#000";

        select.addEventListener("change", function () {
            this.style.color = this.value === "" ? "#6c757d" : "#000";
        });
    });

    // ======================
    // Toggle requester books
    // ======================

    document.querySelectorAll(".toggle-books-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            setTimeout(() => {
                if (this.classList.contains("collapsed")) {
                    this.innerText = "View Requester Books";
                } else {
                    this.innerText = "Hide Requester Books";
                }
            }, 200);
        });
    });

});


// =========================
// 🔔 REAL TIME TOAST COUNTER
// =========================

let notified = false;

setInterval(() => {

    fetch("/books/check/")
    .then(res => res.json())
    .then(data => {

        if (data.count > 0 && !notified) {

            notified = true;

            const toast = document.createElement("div");
            toast.className = "toast show position-fixed bottom-0 end-0 m-4 bg-success text-white";
            toast.innerHTML = `
                <div class="toast-body">
                    You have ${data.count} new request(s)
                </div>
            `;

            document.body.appendChild(toast);

            setTimeout(() => toast.remove(), 4000);
        }
    });

}, 5000);


// =========================
// REAL-TIME EXCHANGE STATUS
// =========================

setInterval(() => {

    document.querySelectorAll(".exchange-badge").forEach(badge => {

        const exchangeId = badge.dataset.exchangeId;
        if (!exchangeId) return;

        fetch(`/exchange-status/${exchangeId}/`)
        .then(res => res.json())
        .then(data => {

            badge.innerText =
                data.status.charAt(0).toUpperCase() + data.status.slice(1);

            badge.className = "badge exchange-badge exchange-badge-sm";

            if (data.status === "completed") {
                badge.classList.add("bg-success");

                const btn = document.querySelector(
                    `.confirm-btn[data-exchange-id="${exchangeId}"]`
                );
                if (btn) btn.remove();
            }

            if (data.status === "approved") {
                badge.classList.add("bg-primary");
            }

            if (data.status === "pending") {
                badge.classList.add("bg-warning", "text-dark");
            }

            if (data.status === "rejected" || data.status === "cancelled") {
                badge.classList.add("bg-danger");
            }

        });

    });

}, 4000);


const footerForm = document.getElementById('footer-contact-form');
const footerResult = document.getElementById('footer-form-result');

footerForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(footerForm);
    const object = Object.fromEntries(formData);
    const json = JSON.stringify(object);
    footerResult.innerHTML = "Sending..."

    fetch('https://api.web3forms.com/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: json
        })
        .then(async (response) => {
            let json = await response.json();
            if (response.status == 200) {
                footerResult.className = "mt-2 small text-success";
                footerResult.innerHTML = "Thank you! We'll be in touch.";
            } else {
                footerResult.className = "mt-2 small text-danger";
                footerResult.innerHTML = json.message;
            }
        })
        .catch(error => {
            footerResult.innerHTML = "Something went wrong!";
        })
        .then(function() {
            footerForm.reset();
            setTimeout(() => {
                footerResult.innerHTML = "";
            }, 5000);
        });
});