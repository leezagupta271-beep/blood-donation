document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            hamburger.classList.toggle('active');
            // Animate hamburger to X
            const spans = hamburger.querySelectorAll('span');
            if (navLinks.classList.contains('active')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });
    }

    // Modern Toast Notification UI
    window.showAlert = function(message, type = 'success') {
        let container = document.querySelector('.alert-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'alert-container';
            document.body.appendChild(container);
        }

        const icon = type === 'success' ? 'check-circle' : 'alert-circle';
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i data-feather="${icon}" class="toast-icon"></i>
            <p>${message}</p>
        `;
        
        container.appendChild(toast);
        if (typeof feather !== 'undefined') feather.replace();

        // Animate in
        requestAnimationFrame(() => {
            setTimeout(() => toast.classList.add('show'), 10);
        });

        // Animate out and remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }

    // Form Handling with Fetch API
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Contact form basic verification
            if (form.id === 'contactForm') {
                const submitBtn = form.querySelector('button[type="submit"]');
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<div class="spinner" style="width:20px;height:20px;margin:0;border-width:2px;display:inline-block;"></div> Sending...';
                submitBtn.classList.add('loading');
                
                setTimeout(() => {
                    showAlert('Your message has been received! Our support team will respond shortly.', 'success');
                    form.reset();
                    submitBtn.innerHTML = originalText;
                    submitBtn.classList.remove('loading');
                }, 1000);
                return;
            }

            // Register Form
            if (form.id === 'registerForm') {
                const name = document.getElementById('fullName').value;
                const email = document.getElementById('email').value;
                const phone = document.getElementById('phone').value;
                const blood_group = document.getElementById('bloodGroup').value;
                const location = document.getElementById('location').value;
                const password = document.getElementById('password').value;

                // Button loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<div class="spinner" style="width:20px;height:20px;margin:0;border-width:2px;display:inline-block;"></div> Registering...';
                submitBtn.classList.add('loading');

                try {
                    const response = await fetch('/api/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, email, phone, blood_group, location, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showAlert('Welcome to the lifesavers network! Redirecting...', 'success');
                        setTimeout(() => window.location.href = '/login', 1500);
                    } else {
                        showAlert(data.error || 'Registration failed', 'error');
                        submitBtn.innerHTML = originalText;
                        submitBtn.classList.remove('loading');
                    }
                } catch (err) {
                    showAlert('Network error occurred. Please try again.', 'error');
                    submitBtn.innerHTML = originalText;
                    submitBtn.classList.remove('loading');
                }
            }

            // Login Form
            if (form.id === 'loginForm') {
                const email = document.getElementById('loginEmail').value;
                const password = document.getElementById('loginPassword').value;

                const submitBtn = form.querySelector('button[type="submit"]');
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<div class="spinner" style="width:20px;height:20px;margin:0;border-width:2px;display:inline-block;"></div> Authenticating...';
                submitBtn.classList.add('loading');

                try {
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showAlert('Authentication successful!', 'success');
                        setTimeout(() => {
                            if (data.role === 'admin') window.location.href = '/admin';
                            else window.location.href = '/dashboard';
                        }, 1000);
                    } else {
                        showAlert(data.error || 'Invalid credentials', 'error');
                        submitBtn.innerHTML = originalText;
                        submitBtn.classList.remove('loading');
                    }
                } catch (err) {
                    showAlert('Network error occurred.', 'error');
                    submitBtn.innerHTML = originalText;
                    submitBtn.classList.remove('loading');
                }
            }
        });
    });

    // Logout Helper
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            await fetch('/api/logout', { method: 'POST' });
            window.location.href = '/login';
        });
    }

    // Initialize Pages dynamically
    const path = window.location.pathname;
    if (path === '/camps') fetchCamps();
    if (path === '/dashboard') fetchDashboardStats();
    if (path === '/availability') fetchAvailability('all');
    if (path === '/needs') fetchNeeds();

    // Donor search logic
    const searchDonorsBtn = document.getElementById('searchDonorsBtn');
    if (searchDonorsBtn) {
        searchDonorsBtn.addEventListener('click', async () => {
            const loc = document.getElementById('donorLocationSearch').value.trim();
            if (!loc) return showAlert('Please enter a location to search', 'warning');

            document.getElementById('loadingIndicator').style.display = 'block';
            document.getElementById('donorsGrid').innerHTML = '';
            document.getElementById('noDonorsMsg').style.display = 'none';

            try {
                const response = await fetch(`/api/donors/location/${encodeURIComponent(loc)}`);
                const donors = await response.json();
                
                document.getElementById('loadingIndicator').style.display = 'none';
                
                if (donors.length === 0) {
                    document.getElementById('noDonorsMsg').style.display = 'block';
                } else {
                    const grid = document.getElementById('donorsGrid');
                    donors.forEach(donor => {
                        grid.innerHTML += `
                            <div class="data-card">
                                <div class="card-header">
                                    <h3>${donor.name}</h3>
                                </div>
                                <div class="card-body">
                                    <p><i data-feather="map-pin"></i> ${donor.location}</p>
                                    <p><i data-feather="phone"></i> ${donor.phone}</p>
                                    <div class="blood-group-highlight">${donor.blood_group}</div>
                                </div>
                                <div class="card-footer">
                                    <button class="btn primary-btn btn-full">Request Blood</button>
                                </div>
                            </div>
                        `;
                    });
                    if (typeof feather !== 'undefined') feather.replace();
                }
            } catch (err) {
                document.getElementById('loadingIndicator').style.display = 'none';
                showAlert('Failed to connect to the donor network', 'error');
            }
        });
    }
    
    // Blood Group Filter on Availability
    const bgFilter = document.getElementById('bloodGroupStockFilter');
    if (bgFilter) bgFilter.addEventListener('change', (e) => fetchAvailability(e.target.value));

    // Modal behavior for Availability Contact
    window.openContactModal = function(name, contact, loc) {
        document.getElementById('modalHospitalName').textContent = name;
        document.getElementById('modalPhone').textContent = contact && contact !== 'undefined' ? contact : 'Not Provided';
        document.getElementById('modalLocation').textContent = loc || 'Location Not Provided';
        document.getElementById('modalEmail').textContent = `contact@${name.replace(/[^a-zA-Z]/g, '').toLowerCase()}.org`;
        
        const modal = document.getElementById('contactModal');
        modal.style.display = 'flex';
        // Small delay for fade in effect
        requestAnimationFrame(() => modal.classList.add('show'));
    };

    document.addEventListener('click', (e) => {
        if(e.target.classList.contains('close-modal') || e.target.id === 'contactModal') {
            const modal = document.getElementById('contactModal');
            if(modal) {
                modal.classList.remove('show');
                setTimeout(() => modal.style.display = 'none', 300);
            }
        }
    });
});

async function fetchCamps() {
    try {
        const response = await fetch('/api/camps');
        const camps = await response.json();
        const grid = document.querySelector('.camps-grid');
        
        if (grid) {
            grid.innerHTML = '';
            camps.forEach(camp => {
                grid.innerHTML += `
                    <div class="data-card">
                        <div class="card-header">
                            <h3>${camp.name}</h3>
                        </div>
                        <div class="card-body">
                            <p><i data-feather="map-pin"></i> ${camp.location}</p>
                            <p><i data-feather="calendar"></i> ${camp.date}</p>
                        </div>
                        <div class="card-footer">
                            <button class="btn secondary-btn btn-full register-camp-btn" data-id="${camp.id}">Register for Camp</button>
                        </div>
                    </div>
                `;
            });
            if (typeof feather !== 'undefined') feather.replace();

            document.querySelectorAll('.register-camp-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const campId = e.target.getAttribute('data-id');
                    try {
                        const res = await fetch('/api/register_camp', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ camp_id: campId })
                        });
                        const data = await res.json();
                        if (res.ok) showAlert(data.message, 'success');
                        else showAlert(data.error || 'Failed to register', 'error');
                    } catch (err) {
                        showAlert('Authentication required to register for camps.', 'error');
                    }
                });
            });
        }
    } catch (err) {
        console.error("Failed to load camps", err);
    }
}

async function fetchDashboardStats() {
    try {
        const response = await fetch('/api/dashboard_stats');
        if (response.ok) {
            const stats = await response.json();
            
            // Donor Dashboard
            if (stats.blood_group) {
                document.getElementById('donationsCount').textContent = stats.donations;
                document.getElementById('livesSavedCount').textContent = stats.lives_saved;
                document.getElementById('nextEligibleDate').textContent = stats.next_eligible;
                document.getElementById('userGroupSpan').textContent = `${stats.blood_group}`;
            }
            // Admin Dashboard
            else if (stats.total_donors !== undefined) {
                document.getElementById('totalDonorsCount').textContent = stats.total_donors;
                document.getElementById('activeCampsCount').textContent = stats.active_camps;
                document.getElementById('inventoryCount').textContent = `${stats.total_inventory}`;
                document.getElementById('urgentReqCount').textContent = stats.pending_requests;
                const md = document.getElementById('mostDemandedGroup');
                if (md) md.textContent = stats.most_demanded;
            }
        }
    } catch (err) {
        console.error("Failed to fetch dashboard stats", err);
    }
}

async function fetchAvailability(group = 'all') {
    const loading = document.getElementById('loadingIndicator');
    const noStock = document.getElementById('noStockMsg');
    const grid = document.getElementById('availabilityGrid');
    if (!grid) return;

    loading.style.display = 'block';
    noStock.style.display = 'none';
    grid.innerHTML = '';
    
    try {
        const res = await fetch(`/api/blood_availability?blood_group=${encodeURIComponent(group)}`);
        const data = await res.json();
        loading.style.display = 'none';
        
        if (data.length === 0) {
            noStock.style.display = 'block';
        } else {
            data.forEach(item => {
                let badgeClass = 'badge-success';
                let badgeText = 'Available';
                
                if (item.units_available === 0) {
                    badgeClass = 'badge-danger';
                    badgeText = 'Out of Stock';
                } else if (item.units_available < 15) {
                    badgeClass = 'badge-warning';
                    badgeText = 'Low Stock';
                }
                
                grid.innerHTML += `
                    <div class="data-card">
                        <div class="card-header">
                            <h3>${item.hospital}</h3>
                            <span class="badge ${badgeClass}"><i data-feather="activity"></i> ${badgeText}</span>
                        </div>
                        <div class="card-body">
                            <p><i data-feather="map-pin"></i> ${item.location}</p>
                            <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                                <div>
                                    <span style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Blood Group</span><br>
                                    <div class="blood-group-highlight">${item.blood_group}</div>
                                </div>
                                <div style="text-align: right;">
                                    <span style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Units</span><br>
                                    <span style="font-size: 1.5rem; font-weight: 700;">${item.units_available}</span>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <button class="btn secondary-btn btn-full" onclick="openContactModal('${item.hospital}', '${item.contact}', '${item.location}')">Contact Blood Bank</button>
                        </div>
                    </div>
                `;
            });
            if (typeof feather !== 'undefined') feather.replace();
        }
    } catch(e) {
        loading.style.display = 'none';
        showAlert('Error fetching stock availability from the server', 'error');
    }
}

async function fetchNeeds() {
    const loading = document.getElementById('loadingIndicatorReq');
    const noReq = document.getElementById('noReqMsg');
    const grid = document.getElementById('needsGrid');
    if (!grid) return;

    loading.style.display = 'block';
    noReq.style.display = 'none';
    grid.innerHTML = '';
    
    try {
        const res = await fetch('/api/blood_requests/pending');
        const reqs = await res.json();
        loading.style.display = 'none';
        
        if (reqs.length === 0) {
            noReq.style.display = 'block';
        } else {
            reqs.forEach(r => {
                let badgeClass = '';
                let badgeText = '';
                let borderStyle = '';
                
                if(r.urgency === 'high') {
                    badgeClass = 'badge-urgent';
                    badgeText = '<i data-feather="alert-triangle"></i> URGENT';
                    borderStyle = 'border-top: 4px solid var(--urgent);';
                } else if(r.urgency === 'medium') {
                    badgeClass = 'badge-warning';
                    badgeText = 'Needs Attention';
                    borderStyle = 'border-top: 4px solid var(--warning);';
                } else {
                    badgeClass = 'badge-success';
                    badgeText = 'Standard';
                    borderStyle = 'border-top: 4px solid var(--success);';
                }

                grid.innerHTML += `
                    <div class="data-card" style="${borderStyle}">
                        <div class="card-header">
                            <h3>${r.hospital}</h3>
                            <span class="badge ${badgeClass}">${badgeText}</span>
                        </div>
                        <div class="card-body">
                            <p><i data-feather="calendar"></i> Requested: ${r.date}</p>
                            <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                                <div>
                                    <span style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Required Group</span><br>
                                    <div class="blood-group-highlight">${r.blood_group}</div>
                                </div>
                                <div style="text-align: right;">
                                    <span style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Units Needed</span><br>
                                    <span style="font-size: 1.5rem; font-weight: 700;">${r.units}</span>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <a href="/availability" class="btn primary-btn btn-full"><i data-feather="heart"></i> Donate Now</a>
                        </div>
                    </div>
                `;
            });
            if (typeof feather !== 'undefined') feather.replace();
        }
    } catch(e) {
        loading.style.display = 'none';
        showAlert('Error fetching urgent requests', 'error');
    }
}
