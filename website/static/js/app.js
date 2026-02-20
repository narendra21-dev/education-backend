// future animations & interactions
console.log("Landing page loaded");

// Navbar scroll effect
const navbar = document.querySelector(".glass-nav");
// ------------------------------
// Base API URL
// ------------------------------
// const API_BASE_URL = "https://education-backend-2-qmvp.onrender.com/api";
// const API_BASE_URL1 = "http://127.0.0.1:8000/api";
// const API_BASE_URL = "http://127.0.0.1:8000/api";

 const API_BASE_URL = "https://education-backend-2-qmvp.onrender.com/api";
// const API_BASE_URL1 = "http://127.0.0.1:8000/api";
// const API_BASE_URL = window.location.origin + "/api";

const PUBLIC_ROUTES = [
    "/",
    "/login/",
    "/register/",
    "/verify-otp/",
    "/forgot-password/"
];

const PROTECTED_ROUTES = [
    "/dashboard/",
    "/universities/",
    "/courses/",
    "/books/"
];

function isProtectedRoute(path) {
    return PROTECTED_ROUTES.some(route => path.startsWith(route));
}

function isPublicAuthRoute(path) {
    return ["/login/", "/register/", "/verify-otp/", "/forgot-password/"]
        .some(route => path.startsWith(route));
}


// ------------------------------
// DOMContentLoaded wrapper
// ------------------------------
document.addEventListener("DOMContentLoaded", () => {

    // ------------------------------
    // AUTH GUARD: Redirect logged-in users away from login/register pages
    // ------------------------------
    // const token = localStorage.getItem("access_token");

    const path = window.location.pathname;
    const token = localStorage.getItem("access_token");

    // 🔒 Block protected pages if NOT logged in
    if (isProtectedRoute(path) && !token) {
        window.location.replace("/login/");
        return;
    }

    // 🔁 Redirect logged-in users away from auth pages
    if (isPublicAuthRoute(path) && token) {
        window.location.replace("/dashboard/");
        return;
    }

    // if (window.location.pathname.includes("login") || window.location.pathname.includes("register") || window.location.pathname.includes("verify_otp")) {
    //     if (token) {
    //         window.location.href = "/dashboard/";
    //         return;
    //     }
    // }

    // document.addEventListener("DOMContentLoaded", () => {
    //     const path = window.location.pathname;
    //     const token = localStorage.getItem("access_token");

    //     // 🔒 Block protected pages if NOT logged in
    //     if (isProtectedRoute(path) && !token) {
    //         window.location.replace("/login/");
    //         return;
    //     }

    //     // 🔁 Redirect logged-in users away from auth pages
    //     if (isPublicAuthRoute(path) && token) {
    //         window.location.replace("/dashboard/");
    //         return;
    //     }
    // });

    window.UI = {

        setLoading(button, text = "Processing...") {
            if (!button) return;

            button.dataset.originalText = button.innerHTML;
            button.disabled = true;

            button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2"></span>
            ${text}
          `;
        },

        clearLoading(button) {
            if (!button) return;

            button.disabled = false;
            button.innerHTML = button.dataset.originalText;
        },

        showToast(message, type = "success") {

            const toast = document.createElement("div");
            toast.className = `toast align-items-center text-bg-${type} border-0 show position-fixed bottom-0 end-0 m-4`;
            toast.style.zIndex = 9999;

            toast.innerHTML = `
            <div class="d-flex">
              <div class="toast-body">
                ${message}
              </div>
              <button type="button" class="btn-close btn-close-white me-2 m-auto"></button>
            </div>
          `;

            document.body.appendChild(toast);

            setTimeout(() => {
                toast.remove();
            }, 3000);
        },

        showPageLoader() {
            const loader = document.createElement("div");
            loader.id = "pageLoader";
            loader.innerHTML = `
            <div style="
              position:fixed;
              inset:0;
              background:rgba(255,255,255,0.6);
              display:flex;
              align-items:center;
              justify-content:center;
              z-index:9998;">
              <div class="spinner-border text-primary"></div>
            </div>
          `;
            document.body.appendChild(loader);
        },

        hidePageLoader() {
            const loader = document.getElementById("pageLoader");
            if (loader) loader.remove();
        }

    };


    // ------------------------------
    // REGISTER FORM
    // ------------------------------
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const registerBtn = document.getElementById("registerBtn");
            const btnText = document.getElementById("btnText");
            const btnLoader = document.getElementById("btnLoader");

            // Show loader
            if (btnText && btnLoader && registerBtn) {
                btnText.classList.add("d-none");
                btnLoader.classList.remove("d-none");
                registerBtn.disabled = true;
            }

            const formData = new FormData(registerForm);
            const payload = {
                username: formData.get("username"),
                email: formData.get("email"),
                password: formData.get("password"),
            };

            try {
                const res = await fetch(`${API_BASE_URL}/accounts/register/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });

                const data = await res.json();
                // console.log("data :" + data.email)user with this email already exists.


                if (!res.ok) {
                    if (data.email === "user with this email already exists.") {
                        console.log("data enater :" + data.email)
                        window.location.href = "/verify-otp/";
                    }
                    // alert(data.detail || "Registration failed");
                    showFormMessage("danger", data.detail || "Invalid email or password");
                    // return;
                }

                // Save email for OTP step
                localStorage.setItem("pending_email", payload.email);
                window.location.href = "/verify-otp/";

            } catch (err) {
                console.error(err);
                alert("Network error, try again.");
            } finally {
                if (btnText && btnLoader && registerBtn) {
                    btnText.classList.remove("d-none");
                    btnLoader.classList.add("d-none");
                    registerBtn.disabled = false;
                }
            }
        });
    }

    // ------------------------------
    // VERIFY OTP FORM (with spinner)
    // ------------------------------
    // const otpForm = document.getElementById("otpForm");
    // if (otpForm) {
    //     otpForm.addEventListener("submit", async (e) => {
    //         e.preventDefault();

    //         const otpBtn = document.getElementById("otpBtn");
    //         const btnText = document.getElementById("btnText");
    //         const btnLoader = document.getElementById("btnLoader");

    //         // show loader
    //         if (btnText && btnLoader && otpBtn) {
    //             btnText.classList.add("d-none");
    //             btnLoader.classList.remove("d-none");
    //             otpBtn.disabled = true;
    //         }

    //         const email = localStorage.getItem("pending_email");
    //         const otp = document.getElementById("otp").value.trim();

    //         try {
    //             const res = await fetch(`${API_BASE_URL}/accounts/verify-otp/`, {
    //                 method: "POST",
    //                 headers: { "Content-Type": "application/json" },
    //                 body: JSON.stringify({ email, otp }),
    //             });

    //             const data = await res.json();

    //             if (!res.ok) {
    //                 alert(data.detail || "Invalid OTP");
    //                 return;
    //             }

    //             // success → redirect to login
    //             localStorage.removeItem("pending_email");
    //             window.location.href = "/login/";

    //         } catch (err) {
    //             console.error(err);
    //             alert("Network error. Try again.");
    //         } finally {
    //             // hide loader
    //             if (btnText && btnLoader && otpBtn) {
    //                 btnText.classList.remove("d-none");
    //                 btnLoader.classList.add("d-none");
    //                 otpBtn.disabled = false;
    //             }
    //         }
    //     });
    // }

    // ------------------------------
    // VERIFY OTP + RESEND OTP
    // ------------------------------
    const otpForm = document.getElementById("otpForm");
    const resendOtpBtn = document.getElementById("resendOtpBtn");
    const timerEl = document.getElementById("timer");
    const messageBox = document.getElementById("messageBox");

    function showMessage(type, text) {
        messageBox.className = `alert alert-${type}`;
        messageBox.textContent = text;
        messageBox.classList.remove("d-none");
    }

    function startResendTimer() {
        let timeLeft = 60;
        resendOtpBtn.disabled = true;
        timerEl.textContent = timeLeft;

        const interval = setInterval(() => {
            timeLeft--;
            timerEl.textContent = timeLeft;

            if (timeLeft <= 0) {
                clearInterval(interval);
                resendOtpBtn.disabled = false;
                resendOtpBtn.textContent = "Resend OTP";
            }
        }, 1000);
    }

    if (otpForm) {
        startResendTimer(); // start on page load

        otpForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const otpBtn = document.getElementById("otpBtn");
            const btnText = document.getElementById("btnText");
            const btnLoader = document.getElementById("btnLoader");

            btnText.classList.add("d-none");
            btnLoader.classList.remove("d-none");
            otpBtn.disabled = true;

            const email = localStorage.getItem("pending_email");
            const otp = document.getElementById("otp").value.trim();

            try {
                const res = await fetch(`${API_BASE_URL}/accounts/verify-otp/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, otp }),
                });

                const data = await res.json();

                if (!res.ok) {
                    showMessage("danger", data.detail || "Invalid OTP");
                    return;
                }
                window.location.href = "/dashboard/";
                showMessage("success", "OTP verified successfully 🎉 Redirecting...");

                localStorage.removeItem("pending_email");

                setTimeout(() => {
                    // window.location.href = "/login/";
                }, 1200);

            } catch (err) {
                showMessage("danger", "Network error. Please try again.");
            } finally {
                btnText.classList.remove("d-none");
                btnLoader.classList.add("d-none");
                otpBtn.disabled = false;
            }
        });
    }

    // ------------------------------
    // RESEND OTP
    // ------------------------------
    if (resendOtpBtn) {
        resendOtpBtn.addEventListener("click", async () => {
            const email = localStorage.getItem("pending_email");

            try {
                const res = await fetch(`${API_BASE_URL}/accounts/resend-register-otp/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email }),
                });

                const data = await res.json();

                if (!res.ok) {
                    showMessage("danger", data.detail || "Failed to resend OTP");
                    return;
                }

                showMessage("success", "OTP resent successfully 📩");
                resendOtpBtn.textContent = "Resend OTP (60s)";
                startResendTimer();

            } catch (err) {
                showMessage("danger", "Network error. Try again.");
            }
        });
    }


    // ------------------------------
    // LOGIN FORM
    // ------------------------------
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const loginBtn = document.getElementById("loginBtn");
            const btnText = document.getElementById("btnText");
            const btnLoader = document.getElementById("btnLoader");

            // Show loader
            if (btnText && btnLoader && loginBtn) {
                btnText.classList.add("d-none");
                btnLoader.classList.remove("d-none");
                loginBtn.disabled = true;
            }

            const formData = new FormData(loginForm);
            const payload = {
                email: formData.get("email"),
                password: formData.get("password"),
            };

            try {
                const res = await fetch(`${API_BASE_URL}/accounts/login/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });

                const data = await res.json();
                console.log("data at login :___" + JSON.stringify(data))

                if (!res.ok) {
                    // alert(data.detail || "Login failed");
                    showFormMessage("danger", data.detail || "Invalid email or password");
                    return;
                }

                // Save JWT tokens
                localStorage.setItem("access_token", data.access);
                localStorage.setItem("refresh_token", data.refresh);
                // localStorage.setItem("access_token", data.access);
                // localStorage.setItem("refresh_token", data.refresh);
                console.log("access_token :____", data.access)

                // fetch user role
                fetch(`${API_BASE_URL}/accounts/me/`, {

                    headers: {
                        Authorization: `Bearer ${data.access}`,
                    },
                })
                    .then(res => res.json())
                    .then(user => {
                        localStorage.setItem("is_admin", user.is_staff);
                        console.log("is_admin", user.is_staff)
                        window.location.href = "/dashboard/";
                    });



                // window.location.href = "/dashboard/";

            } catch (err) {
                console.error(err);
                alert("Network error, try again." + JSON.stringify(err));
            } finally {
                if (btnText && btnLoader && loginBtn) {
                    btnText.classList.remove("d-none");
                    btnLoader.classList.add("d-none");
                    loginBtn.disabled = false;
                }
            }
        });
    }


    // ------------------------------
    // FORGOT FORM
    // ------------------------------


    const forgotForm = document.getElementById("forgotForm");
    if (forgotForm) {
        forgotForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const forgotBtn = document.getElementById("forgotBtn");
            const btnText = document.getElementById("btnText");
            const btnLoader = document.getElementById("btnLoader");



            // Show loader
            if (btnText && btnLoader && forgotBtn) {
                btnText.classList.add("d-none");
                btnLoader.classList.remove("d-none");
                forgotBtn.disabled = true;

            }
        });
    }


    // ------------------------------
    // DASHBOARD / UNIVERSITIES / PROTECTED PAGES
    // ------------------------------

    // ------------------------------
    // DASHBOARD API
    // ------------------------------
    if (window.location.pathname.includes("dashboard")) {

        const token = localStorage.getItem("access_token");
        if (!token) {
            window.location.href = "/login/";
            return;
        }

        const loader = document.getElementById("dashboardLoader");
        const content = document.getElementById("dashboardContent");
        const errorBox = document.getElementById("dashboardError");

        Promise.all([
            fetch(`${API_BASE_URL}/universities/`, {
                headers: { Authorization: `Bearer ${token}` }
            }).then(r => r.json()),

            fetch(`${API_BASE_URL}/courses/`, {
                headers: { Authorization: `Bearer ${token}` }
            }).then(r => r.json()),

            // fetch(`${API_BASE_URL}/accounts/users/`, {
            //     headers: { Authorization: `Bearer ${token}` }
            // }).then(r => r.json()),
        ])
            .then(([universities, courses]) => {

                loader.classList.add("d-none");
                content.classList.remove("d-none");
                console.log("universities ::__" + JSON.stringify(universities))

                /* ---------- Universities ---------- */
                document.getElementById("totalUniversities").textContent = universities.count;
                const uniList = document.getElementById("universitiesList");
                uniList.innerHTML = "";
                const allNames = universities.results.map(university => university.name);
                console.log(allNames); //
                universities.results.slice(0, 5).forEach(u => {
                    uniList.innerHTML += `<li>• ${u.name}</li>`;
                });

                /* ---------- Courses ---------- */
                document.getElementById("totalCourses").textContent = courses.count;
                const courseList = document.getElementById("coursesList");
                courseList.innerHTML = "";

                courses.results.slice(0, 5).forEach(c => {
                    courseList.innerHTML += `<li>• ${c.name}</li>`;
                });

                /* ---------- Users ---------- */
                // document.getElementById("totalUsers").textContent = users.count;
                // const userList = document.getElementById("usersList");
                // userList.innerHTML = "";

                // users.results.slice(0, 5).forEach(u => {
                //     userList.innerHTML += `<li>• ${u.email}</li>`;
                // });

            })
            .catch(() => {
                loader.classList.add("d-none");
                errorBox.classList.remove("d-none");
                errorBox.textContent = "Failed to load dashboard data";
            });
    }


    // if (window.location.pathname.includes("dashboard") || window.location.pathname.includes("universities")) {
    //     const token = localStorage.getItem("access_token");
    //     if (!token) {
    //         window.location.href = "/login/";
    //         return;
    //     }

    // Example: Load Universities
    // const universitiesGrid = document.getElementById("universitiesGrid");
    //     const universitiesGrid = document.getElementById("dashboardContent");
    //     // const loader = document.getElementById("loader");
    //     const errorBox = document.getElementById("errorBox");
    //     console.log("universitiesGrid ,:___" + JSON.stringify(universitiesGrid))

    //     if (universitiesGrid) {
    //         fetch(`${API_BASE_URL}/universities/`, {
    //             headers: {
    //                 Authorization: `Bearer ${token}`,
    //             },
    //         })
    //             .then(res => {
    //                 console.log("res ,:___" + res)
    //                 if (res.status === 401) {
    //                     // Token expired or invalid
    //                     localStorage.removeItem("access_token");
    //                     localStorage.removeItem("refresh_token");
    //                     window.location.href = "/login/";
    //                     return;
    //                 }
    //                 return res.json();
    //             })
    //             .then(data => {
    //                 console.log("data ,:___" + JSON.stringify(data))
    //                 if (!data) return;

    //                 // loader.classList.add("d-none");
    //                 universitiesGrid.classList.remove("d-none");

    //                 if (data.length === 0) {
    //                     universitiesGrid.innerHTML = "<p>No universities found.</p>";
    //                     return;
    //                 }

    //                 data.forEach(university => {
    //                     const col = document.createElement("div");
    //                     col.className = "col-md-4";
    //                     col.innerHTML = `
    //                   <a href="/courses/?university=${university.id}" class="browse-card">
    //                     <h5>${university.name}</h5>
    //                     <p>${university.code || ""}</p>
    //                   </a>
    //                 `;
    //                     universitiesGrid.appendChild(col);
    //                 });
    //             })
    //             .catch(err => {
    //                 console.log("err ,:___" + JSON.stringify(err))
    //                 loader.classList.add("d-none");
    //                 if (errorBox) errorBox.classList.remove("d-none");
    //                 console.error("Universities API error:", err);
    //             });
    //     }
    // }

    // ------------------------------
    // LOGOUT BUTTON (Optional)
    // ------------------------------
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.location.href = "/login/";
        });
    }


    function renderNavbarAuth() {
        const navArea = document.getElementById("nav-auth-area");
        const navActions = document.getElementById("navActions");
        const token = localStorage.getItem("access_token");
        const isAdmin = localStorage.getItem("is_admin") === "true";

        //     if (navActions) {
        //         if (!token) {
        //             navActions.innerHTML = `
        //   <a href="/login/" class="btn btn-outline-light btn-sm me-2">Login</a>
        //   <a href="/register/" class="btn btn-primary btn-sm">Get Started</a>
        // `;
        //         } else {
        //             navActions.innerHTML = `
        //   ${isAdmin ? `<a href="/admin/" class="btn btn-warning btn-sm me-2">Admin</a>` : ""}
        //   <button id="logoutBtn" class="btn btn-danger btn-sm">Logout</button>
        // `;
        //         }
        //     }

        if (!navArea) return;

        // const token = localStorage.getItem("access_token");

        if (token) {
            //     navArea.innerHTML = `
            //     <a href="/dashboard/" class="btn btn-outline-light btn-sm me-2">
            //       Dashboard
            //     </a>
            //     <button id="logoutBtn" class="btn btn-danger btn-sm">
            //       Logout
            //     </button>
            //   `;

            navArea.innerHTML = `
        ${isAdmin ? `<a href="/admin/" class="btn btn-warning btn-sm me-2">Admin</a>` : ""}
        <button id="logoutBtn" class="btn btn-danger btn-sm">Logout</button>
        <a href="/dashboard/" class="btn btn-outline-light btn-sm me-2">Dashboard</a>
        `;
        } else {
            navArea.innerHTML = `
            <a href="/login/" class="btn btn-outline-light btn-sm me-2">
              Login
            </a>
            <a href="/register/" class="btn btn-primary btn-sm">
              Get Started
            </a>
          `;
        }
    }

    renderNavbarAuth();

    document.addEventListener("click", (e) => {
        if (e.target.id === "logoutBtn") {
            localStorage.clear();
            window.location.replace("/login/");
        }
    });

    // fetch(API_BASE_URL, {
    //     headers: {
    //         Authorization: `Bearer ${localStorage.getItem("access_token")}`
    //     }
    // })
    //     .then(res => {
    //         if (res.status === 401) {
    //             localStorage.clear();
    //             window.location.replace("/login/");
    //             return;
    //         }
    //         return res.json();
    //     });
    function showFormMessage(type, text) {
        const box = document.getElementById("formMessage");
        if (!box) return;

        box.className = `alert alert-${type} fade-in`;
        box.textContent = text;
        box.classList.remove("d-none");

        if (type === "danger") {
            box.classList.add("shake");
        }
    }



});
