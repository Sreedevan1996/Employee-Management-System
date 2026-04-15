(() => {
    "use strict";

    const EMS = {
        unsavedChanges: false,

        init() {
            this.initRevealAnimations();
            this.initFlashMessages();
            this.initMobileNav();
            this.initBackToTop();
            this.initSortableTables();
            this.initLiveTableFilters();
            this.initFormEnhancements();
            this.initPasswordEnhancements();
            this.initStatCounters();
            this.initDestructiveActionModal();
            this.initRowHighlightFromQuery();
            this.initKeyboardShortcuts();
        },

        // -----------------------------
        // Helpers
        // -----------------------------
        qs(selector, scope = document) {
            return scope.querySelector(selector);
        },

        qsa(selector, scope = document) {
            return Array.from(scope.querySelectorAll(selector));
        },

        createEl(tag, className = "", html = "") {
            const el = document.createElement(tag);
            if (className) el.className = className;
            if (html) el.innerHTML = html;
            return el;
        },

        debounce(fn, delay = 180) {
            let timeout;
            return (...args) => {
                window.clearTimeout(timeout);
                timeout = window.setTimeout(() => fn(...args), delay);
            };
        },

        formatNumber(num) {
            return new Intl.NumberFormat().format(num);
        },

        // -----------------------------
        // Reveal animations
        // -----------------------------
        initRevealAnimations() {
            const revealTargets = this.qsa(".card, .stats-grid > *, .page-header, .hero .card");
            revealTargets.forEach((el, index) => {
                el.classList.add("reveal");
                el.style.transitionDelay = `${Math.min(index * 40, 220)}ms`;
            });

            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("revealed");
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });

            revealTargets.forEach((el) => observer.observe(el));
        },

        // -----------------------------
        // Flash messages
        // -----------------------------
        initFlashMessages() {
            const alerts = this.qsa(".alert");
            alerts.forEach((alert) => {
                if (!alert.querySelector(".alert-close")) {
                    const btn = document.createElement("button");
                    btn.type = "button";
                    btn.className = "alert-close";
                    btn.setAttribute("aria-label", "Dismiss message");
                    btn.innerHTML = "&times;";
                    btn.addEventListener("click", () => this.dismissAlert(alert));
                    alert.appendChild(btn);
                }

                window.setTimeout(() => {
                    if (document.body.contains(alert)) {
                        this.dismissAlert(alert);
                    }
                }, 5500);
            });
        },

        dismissAlert(alert) {
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-6px)";
            alert.style.transition = "opacity 0.25s ease, transform 0.25s ease";
            window.setTimeout(() => alert.remove(), 250);
        },

        // -----------------------------
        // Mobile nav
        // -----------------------------
        initMobileNav() {
            const nav = this.qs(".main-nav");
            const navContainer = this.qs(".nav-container");
            if (!nav || !navContainer) return;

            if (this.qs(".mobile-nav-toggle", navContainer)) return;

            const toggle = document.createElement("button");
            toggle.type = "button";
            toggle.className = "mobile-nav-toggle";
            toggle.setAttribute("aria-label", "Toggle navigation");
            toggle.setAttribute("aria-expanded", "false");
            toggle.innerHTML = "<span></span>";

            const brand = this.qs(".brand", navContainer);
            if (brand && brand.nextSibling) {
                navContainer.insertBefore(toggle, brand.nextSibling);
            } else {
                navContainer.prepend(toggle);
            }

            toggle.addEventListener("click", () => {
                const isOpen = nav.classList.toggle("open");
                toggle.classList.toggle("active", isOpen);
                toggle.setAttribute("aria-expanded", String(isOpen));
                document.body.classList.toggle("nav-open", isOpen);
            });

            document.addEventListener("click", (event) => {
                if (!nav.classList.contains("open")) return;
                if (!nav.contains(event.target) && !toggle.contains(event.target)) {
                    nav.classList.remove("open");
                    toggle.classList.remove("active");
                    toggle.setAttribute("aria-expanded", "false");
                    document.body.classList.remove("nav-open");
                }
            });

            window.addEventListener("resize", () => {
                if (window.innerWidth > 980) {
                    nav.classList.remove("open");
                    toggle.classList.remove("active");
                    toggle.setAttribute("aria-expanded", "false");
                    document.body.classList.remove("nav-open");
                }
            });
        },

        // -----------------------------
        // Back to top
        // -----------------------------
        initBackToTop() {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "back-to-top";
            btn.setAttribute("aria-label", "Back to top");
            btn.innerHTML = "↑";
            document.body.appendChild(btn);

            const toggleVisibility = () => {
                btn.classList.toggle("visible", window.scrollY > 300);
            };

            window.addEventListener("scroll", toggleVisibility, { passive: true });
            toggleVisibility();

            btn.addEventListener("click", () => {
                window.scrollTo({ top: 0, behavior: "smooth" });
            });
        },

        // -----------------------------
        // Sortable tables
        // -----------------------------
        initSortableTables() {
            this.qsa(".table").forEach((table) => {
                const headerCells = this.qsa("thead th", table);
                const tbody = this.qs("tbody", table);
                if (!tbody || !headerCells.length) return;

                headerCells.forEach((th, index) => {
                    if (th.classList.contains("actions-col")) return;

                    th.classList.add("sortable");
                    th.dataset.sortDirection = "none";

                    th.addEventListener("click", () => {
                        const rows = this.qsa("tr", tbody);
                        const currentDirection = th.dataset.sortDirection;
                        const nextDirection = currentDirection === "asc" ? "desc" : "asc";

                        headerCells.forEach((cell) => {
                            cell.dataset.sortDirection = "none";
                            cell.classList.remove("sort-asc", "sort-desc");
                        });

                        th.dataset.sortDirection = nextDirection;
                        th.classList.add(nextDirection === "asc" ? "sort-asc" : "sort-desc");

                        const sortedRows = [...rows].sort((a, b) => {
                            const aText = (a.children[index]?.textContent || "").trim();
                            const bText = (b.children[index]?.textContent || "").trim();

                            const aNumber = Number(aText.replace(/[^0-9.-]/g, ""));
                            const bNumber = Number(bText.replace(/[^0-9.-]/g, ""));
                            const numeric = !Number.isNaN(aNumber) && !Number.isNaN(bNumber) && aText !== "" && bText !== "";

                            let result = 0;
                            if (numeric) {
                                result = aNumber - bNumber;
                            } else {
                                result = aText.localeCompare(bText, undefined, { numeric: true, sensitivity: "base" });
                            }

                            return nextDirection === "asc" ? result : -result;
                        });

                        sortedRows.forEach((row) => tbody.appendChild(row));
                    });
                });
            });
        },

        // -----------------------------
        // Live table filter UI
        // -----------------------------
        initLiveTableFilters() {
            this.qsa(".table-responsive").forEach((tableWrap) => {
                const table = this.qs(".table", tableWrap);
                const tbody = this.qs("tbody", table);
                const header = tableWrap.closest(".card")?.querySelector("h2");
                if (!table || !tbody) return;

                const rows = this.qsa("tr", tbody);
                if (!rows.length) return;

                const toolbar = this.createEl("div", "section-toolbar");
                const input = this.createEl("input", "form-control table-search");
                input.type = "search";
                input.placeholder = "Quick filter visible rows...";
                input.setAttribute("aria-label", "Quick filter table rows");

                const meta = this.createEl("div", "field-hint");
                meta.textContent = `${rows.length} record(s)`;

                toolbar.appendChild(input);
                toolbar.appendChild(meta);

                const host = header ? header.parentElement : tableWrap.parentElement;
                host.insertBefore(toolbar, tableWrap);

                const emptyState = this.createEl("div", "table-empty-state", "No matching records.");
                emptyState.style.display = "none";
                tableWrap.appendChild(emptyState);

                const runFilter = this.debounce(() => {
                    const term = input.value.trim().toLowerCase();
                    let visibleCount = 0;

                    rows.forEach((row) => {
                        const text = row.textContent.toLowerCase();
                        const show = text.includes(term);
                        row.style.display = show ? "" : "none";
                        if (show) visibleCount += 1;
                    });

                    meta.textContent = `${visibleCount} visible / ${rows.length} total`;
                    emptyState.style.display = visibleCount === 0 ? "block" : "none";
                }, 120);

                input.addEventListener("input", runFilter);
            });
        },

        // -----------------------------
        // Form enhancements
        // -----------------------------
        initFormEnhancements() {
            const forms = this.qsa("form");
            forms.forEach((form) => {
                const fields = this.qsa("input, select, textarea", form);

                fields.forEach((field) => {
                    const initialValue = this.getFieldValue(field);
                    field.dataset.initialValue = initialValue;

                    field.addEventListener("input", () => {
                        this.markChangedField(field);
                        this.applyLiveValidation(field);
                        this.unsavedChanges = true;
                    });

                    field.addEventListener("change", () => {
                        this.markChangedField(field);
                        this.applyLiveValidation(field);
                        this.unsavedChanges = true;
                    });

                    // Auto-format fields by common EMS patterns
                    if (field.name === "employee_code" || field.name === "code") {
                        field.addEventListener("input", () => {
                            field.value = field.value.toUpperCase().replace(/\s+/g, "");
                        });
                    }

                    if (field.name === "email") {
                        field.addEventListener("blur", () => {
                            field.value = field.value.trim().toLowerCase();
                        });
                    }

                    if (field.name === "salary") {
                        field.addEventListener("blur", () => {
                            const num = Number(field.value);
                            if (!Number.isNaN(num) && field.value.trim() !== "") {
                                field.value = num.toFixed(2);
                            }
                        });
                    }
                });

                form.addEventListener("submit", () => {
                    this.unsavedChanges = false;
                });
            });

            window.addEventListener("beforeunload", (event) => {
                if (!this.unsavedChanges) return;
                event.preventDefault();
                event.returnValue = "";
            });
        },

        getFieldValue(field) {
            if (field.type === "checkbox" || field.type === "radio") {
                return String(field.checked);
            }
            return field.value ?? "";
        },

        markChangedField(field) {
            const group = field.closest(".form-group");
            if (!group) return;

            const initial = field.dataset.initialValue;
            const current = this.getFieldValue(field);
            group.classList.toggle("has-changed", initial !== current);
        },

        applyLiveValidation(field) {
            if (!field.classList.contains("form-control")) return;

            const value = field.value.trim();
            const type = field.getAttribute("type");
            const required = field.required;

            let valid = true;

            if (required && !value) valid = false;

            if (valid && type === "email" && value) {
                valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            }

            if (valid && field.name === "employee_code" && value) {
                valid = /^[A-Z0-9_-]+$/.test(value);
            }

            if (valid && field.name === "phone" && value) {
                valid = /^[\d+\-\s()]+$/.test(value);
            }

            if (value === "" && !required) {
                field.classList.remove("is-valid", "is-invalid");
                return;
            }

            field.classList.toggle("is-valid", valid);
            field.classList.toggle("is-invalid", !valid);
        },

        // -----------------------------
        // Password enhancements
        // -----------------------------
        initPasswordEnhancements() {
            const passwordInputs = this.qsa('input[type="password"]');
            passwordInputs.forEach((input) => {
                if (input.dataset.passwordEnhanced === "true") return;
                input.dataset.passwordEnhanced = "true";

                const wrapper = document.createElement("div");
                wrapper.className = "password-wrapper";
                input.parentNode.insertBefore(wrapper, input);
                wrapper.appendChild(input);

                const toggle = document.createElement("button");
                toggle.type = "button";
                toggle.className = "password-toggle";
                toggle.textContent = "Show";
                toggle.setAttribute("aria-label", "Show password");
                wrapper.appendChild(toggle);

                toggle.addEventListener("click", () => {
                    const hidden = input.type === "password";
                    input.type = hidden ? "text" : "password";
                    toggle.textContent = hidden ? "Hide" : "Show";
                    toggle.setAttribute("aria-label", hidden ? "Hide password" : "Show password");
                });

                if (/new_password|password|confirm_password/i.test(input.name || "")) {
                    let strengthWrap = wrapper.parentElement.querySelector(".password-strength");
                    if (!strengthWrap && /password/i.test(input.name || "")) {
                        strengthWrap = this.createEl(
                            "div",
                            "password-strength",
                            `
                                <div class="password-strength-bar">
                                    <div class="password-strength-fill"></div>
                                </div>
                                <div class="password-strength-label">Strength: -</div>
                            `
                        );
                        wrapper.insertAdjacentElement("afterend", strengthWrap);

                        input.addEventListener("input", () => {
                            const score = this.getPasswordStrengthScore(input.value);
                            const fill = strengthWrap.querySelector(".password-strength-fill");
                            const label = strengthWrap.querySelector(".password-strength-label");

                            const map = [
                                { width: 10, label: "Very weak", color: "#dc2626" },
                                { width: 30, label: "Weak", color: "#ea580c" },
                                { width: 55, label: "Fair", color: "#d97706" },
                                { width: 78, label: "Good", color: "#2563eb" },
                                { width: 100, label: "Strong", color: "#16a34a" }
                            ];

                            const current = map[score];
                            fill.style.width = `${current.width}%`;
                            fill.style.background = current.color;
                            label.textContent = `Strength: ${current.label}`;
                        });
                    }
                }
            });
        },

        getPasswordStrengthScore(password) {
            let score = 0;
            if (password.length >= 8) score += 1;
            if (/[a-z]/.test(password)) score += 1;
            if (/[A-Z]/.test(password)) score += 1;
            if (/\d/.test(password)) score += 1;
            if (/[^A-Za-z0-9]/.test(password)) score += 1;
            return Math.min(score, 4);
        },

        // -----------------------------
        // Stat counters
        // -----------------------------
        initStatCounters() {
            this.qsa(".stat-number").forEach((el) => {
                const raw = (el.textContent || "").trim();
                const number = Number(raw.replace(/,/g, ""));
                if (Number.isNaN(number)) return;

                const duration = 900;
                const start = performance.now();

                const animate = (now) => {
                    const progress = Math.min((now - start) / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    const value = Math.round(number * eased);
                    el.textContent = this.formatNumber(value);

                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    } else {
                        el.textContent = this.formatNumber(number);
                    }
                };

                requestAnimationFrame(animate);
            });
        },

        // -----------------------------
        // Destructive action modal
        // -----------------------------
        initDestructiveActionModal() {
            const destructiveButtons = this.qsa(
                'form[action*="/delete"] button[type="submit"], button[data-confirm]'
            );

            destructiveButtons.forEach((button) => {
                button.addEventListener("click", (event) => {
                    const form = button.closest("form");
                    const customMessage = button.dataset.confirmMessage || "Are you sure you want to continue? This action may be irreversible.";
                    if (!form) return;

                    event.preventDefault();

                    this.openConfirmModal({
                        title: "Confirm Action",
                        message: customMessage,
                        confirmText: "Yes, continue",
                        cancelText: "Cancel",
                        danger: true,
                        onConfirm: () => form.submit()
                    });
                });
            });
        },

        openConfirmModal({ title, message, confirmText, cancelText, danger = false, onConfirm }) {
            const backdrop = this.createEl("div", "ems-modal-backdrop");
            const modal = this.createEl(
                "div",
                "ems-modal",
                `
                    <div class="ems-modal-header">
                        <h3>${title}</h3>
                        <button type="button" class="ems-modal-close" aria-label="Close">&times;</button>
                    </div>
                    <div class="ems-modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="ems-modal-footer">
                        <button type="button" class="btn btn-secondary modal-cancel">${cancelText}</button>
                        <button type="button" class="btn ${danger ? "btn-danger" : "btn-primary"} modal-confirm">${confirmText}</button>
                    </div>
                `
            );

            backdrop.appendChild(modal);
            document.body.appendChild(backdrop);
            document.body.style.overflow = "hidden";

            const close = () => {
                backdrop.remove();
                document.body.style.overflow = "";
            };

            backdrop.addEventListener("click", (e) => {
                if (e.target === backdrop) close();
            });

            modal.querySelector(".ems-modal-close").addEventListener("click", close);
            modal.querySelector(".modal-cancel").addEventListener("click", close);
            modal.querySelector(".modal-confirm").addEventListener("click", () => {
                close();
                if (typeof onConfirm === "function") onConfirm();
            });

            document.addEventListener("keydown", function escHandler(e) {
                if (e.key === "Escape") {
                    close();
                    document.removeEventListener("keydown", escHandler);
                }
            });
        },

        // -----------------------------
        // Row highlight from query param
        // -----------------------------
        initRowHighlightFromQuery() {
            const params = new URLSearchParams(window.location.search);
            const highlight = params.get("highlight");
            if (!highlight) return;

            const rows = this.qsa(".table tbody tr");
            const target = rows.find((row) => row.textContent.toLowerCase().includes(highlight.toLowerCase()));
            if (!target) return;

            target.classList.add("row-highlight");
            target.scrollIntoView({ behavior: "smooth", block: "center" });
        },

        // -----------------------------
        // Keyboard shortcuts
        // -----------------------------
        initKeyboardShortcuts() {
            document.addEventListener("keydown", (event) => {
                const activeTag = document.activeElement?.tagName?.toLowerCase();
                const typing = ["input", "textarea", "select"].includes(activeTag);

                // focus quick filter with "/"
                if (!typing && event.key === "/") {
                    const filter = this.qs(".table-search");
                    if (filter) {
                        event.preventDefault();
                        filter.focus();
                    }
                }

                // go to add employee with Alt+N
                if (event.altKey && event.key.toLowerCase() === "n") {
                    const addEmployeeLink = this.qs('a[href*="/employees/create"]');
                    if (addEmployeeLink) {
                        window.location.href = addEmployeeLink.href;
                    }
                }
            });
        }
    };

    document.addEventListener("DOMContentLoaded", () => EMS.init());
})();