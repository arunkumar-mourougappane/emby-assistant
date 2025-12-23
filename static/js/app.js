// Theme Management
const ThemeManager = {
    init() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        $('#themeToggle').on('click', () => {
            const currentTheme = $('html').attr('data-bs-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            this.setTheme(newTheme);
        });
    },

    setTheme(theme) {
        $('html').attr('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        const icon = theme === 'light' ? '🌙' : '☀️';
        $('#themeToggle').text(icon);
    }
};

// Data Loading Functions
const App = {
    currentTab: 'recent',
    
    init() {
        ThemeManager.init();
        
        // Common elements
        this.loadServerStatus();
        this.loadNowPlaying();
        this.setupRefreshIntervals();
        
        // Page specific
        if($('#currentProcessing').length) this.loadCurrentProcessing();
        if($('#completedTasks').length) this.loadCompletedTasks();
        if($('#indexedMediaList').length) this.loadIndexedMedia();
        if($('#serverDetailsSection').length) this.loadServerDetails();
        if($('#librariesContainer').length) {
            this.loadLibrarySections();
            this.setupSearch();
        }
        if($('#castContainer').length) {
            this.loadCast();
            this.setupCastSearch();
        }
        
        // Update active nav link
        const currentPath = window.location.pathname;
        $('.navbar-nav .nav-link').each(function() {
            if($(this).attr('href') === currentPath) {
                $(this).addClass('active');
            }
        });
    },

    setupRefreshIntervals() {
        setInterval(() => this.loadServerStatus(), 30000);
        setInterval(() => this.loadNowPlaying(), 5000);
        
        if($('#currentProcessing').length) {
            setInterval(() => this.loadCurrentProcessing(), 5000);
        }
        
        if($('#serverDetailsSection').length) {
             setInterval(() => this.updateServerTime(), 4000);
        }
    },



    async loadServerStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (data.error) {
                this.showToast(data.error, 'danger');
                $('#statusIndicator').removeClass('status-online').addClass('status-offline');
                return;
            }

            $('#statusIndicator').removeClass('status-offline').addClass('status-online');
            $('#serverInfo').html(`
                <span class="navbar-text text-white me-3">
                    <span class="status-indicator status-online"></span>
                    ${data.server_name} (v${data.version})
                </span>
            `);
            $('#serverDetailsTrigger').show();
            // Store data for detail modal
            window.serverData = data; 
        } catch (error) {
            console.error('Status Error:', error);
            $('#statusIndicator').removeClass('status-online').addClass('status-offline');
        }
    },

    async updateServerTime() {
        if (!$('#serverTimeDisplay').length) return;
        try {
            const response = await fetch('/api/server-time');
            const data = await response.json();
            $('#serverTimeDisplay').text(data.server_time);
        } catch (error) {
             console.error('Time Update Error:', error);
        }
    },

    async loadNowPlaying() {
        try {
            const response = await fetch('/api/now-playing');
            const sessions = await response.json();
            const container = $('#nowPlayingSection');

            if (sessions.length === 0) {
                container.slideUp();
                return;
            }

            container.html(sessions.map(session => {
                const item = session.item;
                const progressPercent = (session.play_state.position_ticks / item.runtime_ticks) * 100;
                
                return `
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">▶ Now Playing</h5>
                        <span class="badge bg-light text-dark">${session.user} on ${session.device}</span>
                    </div>
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-2 text-center">
                                <img src="/api/image/${item.id}" class="img-fluid rounded shadow" style="max-height: 150px;" alt="${item.name}">
                            </div>
                            <div class="col-md-10">
                                <h4>${item.series_name ? `${item.series_name} - ` : ''}${item.name}</h4>
                                <div class="mb-2">
                                    ${item.season ? `<span class="badge bg-secondary">S${item.season}:E${item.episode}</span>` : ''}
                                    <span class="badge bg-info">${item.year}</span>
                                    <span class="badge bg-dark">${session.play_state.is_paused ? '⏸ Paused' : '▶ Playing'}</span>
                                    ${session.transcoding.is_transcoding ? 
                                        `<span class="badge bg-warning text-dark">⚙️ Transcoding (${session.transcoding.video_codec})</span>` : 
                                        '<span class="badge bg-success">Direct Play</span>'}
                                </div>
                                <div class="progress mb-2" style="height: 20px;">
                                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                         role="progressbar" 
                                         style="width: ${progressPercent}%">
                                    </div>
                                </div>
                                <div class="d-flex justify-content-between small text-muted">
                                    <span>${session.client} (${session.remote_endpoint})</span>
                                    <span>${session.transcoding.container ? `Container: ${session.transcoding.container}` : ''}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                `;
            }).join(''));

            container.slideDown();

        } catch (error) {
            console.error('Now Playing Error:', error);
        }
    },

    async loadCurrentProcessing() {
        try {
            const response = await fetch('/api/current-processing');
            const data = await response.json();
            const container = $('#currentProcessing');

            if (data.length === 0) {
                container.html(`
                    <div class="text-center text-muted py-4">
                        <div style="font-size: 2rem;">✨</div>
                        <div>No active processing tasks</div>
                    </div>
                `);
                return;
            }

            container.html(data.map(item => `
                <div class="task-item">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="badge badge-custom badge-running">${item.state}</span>
                        <small class="text-muted">${item.started_at}</small>
                    </div>
                    <h6 class="mb-1">${item.task_name}</h6>
                    <small class="text-muted d-block mb-2">${item.category}</small>
                    <div class="progress" style="height: 10px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated bg-success" 
                             role="progressbar" 
                             style="width: ${item.progress}%">
                        </div>
                    </div>
                    <small class="text-end d-block mt-1">${item.progress.toFixed(1)}%</small>
                </div>
            `).join(''));
        } catch (error) {
            console.error('Processing Error:', error);
        }
    },

    async loadCompletedTasks() {
        try {
            const response = await fetch('/api/completed-tasks');
            const data = await response.json();
            const container = $('#completedTasks');

            if (data.length === 0) {
                container.html(`
                    <div class="text-center text-muted py-4">
                        <div style="font-size: 2rem;">📋</div>
                        <div>No completed tasks yet</div>
                    </div>
                `);
                return;
            }

            container.html(data.map(task => `
                <div class="task-item" style="border-left-color: #3b82f6;">
                    <div class="d-flex justify-content-between">
                        <span class="badge badge-custom badge-completed">${task.status}</span>
                        <small class="text-muted">${task.completed_at}</small>
                    </div>
                    <h6 class="mt-2 mb-1">${task.name}</h6>
                    <div class="d-flex justify-content-between text-muted small">
                        <span>${task.category}</span>
                        <span>⏱️ ${task.duration}</span>
                    </div>
                </div>
            `).join(''));
        } catch (error) {
            console.error('Completed Tasks Error:', error);
        }
    },

    setupSearch: function() {
        const searchInput = $('#mediaSearch');
        if (!searchInput.length) return;

        searchInput.on('input', function() {
            const searchTerm = $(this).val().toLowerCase();
            $('.media-card-item').each(function() {
                const title = $(this).data('title');
                const titleStr = String(title || ""); 
                $(this).toggle(titleStr.includes(searchTerm));
            });
        });
    },

    loadLibrarySections: async function() {
        const container = $('#librariesContainer');
        if (!container.length) return;

        try {
            const response = await fetch('/api/libraries');
            const libraries = await response.json();

            container.empty();

            if (libraries.length === 0) {
                container.html(`
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>No media libraries found
                    </div>
                `);
                return;
            }

            // Create a section for each library
            for (const lib of libraries) {
                const sectionId = `lib-${lib.id}`;
                // Different icons based on collection type
                let iconClass = 'bi-collection';
                if (lib.collection_type === 'movies') iconClass = 'bi-film';
                else if (lib.collection_type === 'music') iconClass = 'bi-music-note-beamed';
                else if (lib.collection_type === 'tvshows') iconClass = 'bi-tv';
                else if (lib.collection_type === 'boxsets') iconClass = 'bi-box';

                const sectionHtml = `
                    <div class="card mb-4 border-0 shadow-sm theme-card">
                        <div class="card-header bg-transparent border-bottom-0 py-3">
                            <h3 class="h5 mb-0"><i class="bi ${iconClass} me-2 text-primary"></i>${lib.name}</h3>
                        </div>
                        <div class="card-body">
                            <div id="${sectionId}" class="row g-4 justify-content-center">
                                <div class="col-12 text-center">
                                    <div class="spinner-border spinner-border-sm text-secondary" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                container.append(sectionHtml);

                // Load media for this library
                this.loadMediaForLibrary(lib.id, sectionId, lib.collection_type);
            }

        } catch (error) {
            console.error('Error loading libraries:', error);
            container.html(`
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>Failed to load libraries
                </div>
            `);
        }
    },

    loadMediaForLibrary: async function(libraryId, containerId, collectionType) {
        const container = $(`#${containerId}`);
        // Initialize state if not present
        if (!container.data('state')) {
            container.data('state', {
                startIndex: 0,
                limit: 24,
                isLoading: false,
                hasMore: true,
                collectionType: collectionType,
                libraryId: libraryId
            });

            // Attach scroll listener once
            container.addClass('horizontal-scroll-container');
            container.removeClass('row justify-content-center');

            container.on('scroll', () => {
                const state = container.data('state');
                if (state.isLoading || !state.hasMore) return;

                // Check if nearing the end (within 300px)
                if (container.scrollLeft() + container.innerWidth() >= container[0].scrollWidth - 300) {
                    this.loadMediaForLibrary(libraryId, containerId, collectionType);
                }
            });
        }

        const state = container.data('state');
        if (state.isLoading || !state.hasMore) return;

        state.isLoading = true;

        try {
            const response = await fetch(`/api/media?libraryId=${libraryId}&collectionType=${collectionType}&limit=${state.limit}&startIndex=${state.startIndex}&sortBy=DateCreated&sortOrder=Descending`);
            const items = await response.json();

            state.isLoading = false;

            if (items.length === 0) {
                state.hasMore = false;
                if (state.startIndex === 0) {
                    container.html(`
                        <div class="col-12 text-center text-muted py-3">
                            No items found in this library
                        </div>
                    `);
                }
                return;
            }

            if (items.length < state.limit) {
                state.hasMore = false;
            }

            // Clean up initial spinner if first load
            if (state.startIndex === 0) {
                container.empty();
            }

            items.forEach(item => {
                // Correct image path logic using primary_image_tag
                const imagePath = item.primary_image_tag 
                    ? `/api/image/${item.id}?tag=${item.primary_image_tag}` 
                    : null;
                
                // Fallback icon based on type
                let fallbackIcon = 'bi-file-earmark-play';
                if (item.type === 'Audio' || item.type === 'MusicAlbum') fallbackIcon = 'bi-music-note';
                else if (item.type === 'BoxSet') fallbackIcon = 'bi-collection';

                const imageHtml = imagePath 
                    ? `<img src="${imagePath}" class="card-img-top" alt="${item.name}" loading="lazy" style="height: 300px; object-fit: cover;">`
                    : `<div class="card-img-top d-flex align-items-center justify-content-center bg-secondary text-white" style="height: 300px;">
                           <i class="bi ${fallbackIcon} display-1"></i>
                       </div>`;

                const cardHtml = `
                    <div class="media-card-item" data-title="${item.name.toLowerCase()}">
                        <div class="card h-100 border-0 shadow-sm item-card theme-card hvr-float">
                            <div class="position-relative">
                                ${imageHtml}
                                <div class="position-absolute top-0 end-0 p-2">
                                    <span class="badge bg-primary bg-opacity-75">${item.year || 'N/A'}</span>
                                </div>
                            </div>
                            <div class="card-body p-3">
                                <h5 class="card-title h6 text-truncate mb-1" title="${item.name}">${item.name}</h5>
                                <div class="d-flex justify-content-between align-items-center small text-muted">
                                    <span>${item.official_rating || ''}</span>
                                    <span>${item.runtime_minutes ? item.runtime_minutes + 'm' : ''}</span>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent border-top-0 p-3 pt-0">
                                <button class="btn btn-sm btn-outline-primary w-100" 
                                        onclick="App.showMovie(this)" 
                                        data-movie-id="${item.id}">
                                    Details
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                container.append(cardHtml);
            });

            // Update Start Index for next batch
            state.startIndex += items.length;

        } catch (error) {
            state.isLoading = false;
            console.error(`Error loading media for library ${libraryId}:`, error);
            if (state.startIndex === 0) {
                container.html(`
                    <div class="col-12 text-center text-danger">
                        Failed to load content
                    </div>
                `);
            }
        }
    },
    
    // Indexed Media Tab Switcher
    switchTab(tab, element) {
        this.currentTab = tab;
        $('#mediaTabs .nav-link').removeClass('active');
        $(element).addClass('active');
        this.loadIndexedMedia();
    },

    async loadIndexedMedia() {
        try {
            const limit = this.currentTab === 'recent' ? 50 : 100;
            const response = await fetch(`/api/indexed-media?limit=${limit}`);
            const data = await response.json();
            const container = $('#indexedMediaList');

            if (data.length === 0) {
                 container.html('<div class="text-center p-3">No indexed media</div>');
                 return;
            }

            container.html(data.map(item => {
                let badgeClass = 'badge-movie';
                if (item.type === 'Episode') badgeClass = 'badge-episode';
                else if (item.type === 'Series') badgeClass = 'badge-series';
                else if (item.type === 'Person') badgeClass = 'badge-person';
                
                return `
                <div class="media-item d-flex align-items-center mb-2 p-2 list-item-bg rounded">
                    <span class="badge ${badgeClass} me-2" style="min-width: 60px;">${item.type}</span>
                    <div class="flex-grow-1 text-truncate">
                        <strong>${item.series_name ? item.series_name + ' - ' : ''}${item.name}</strong>
                    </div>
                    <small class="text-muted ms-2">${item.added_at}</small>
                </div>
                `;
            }).join(''));
        } catch (error) {
            console.error('Indexed Media Error', error);
        }
    },

    showToast(message, type = 'info') {
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        $('#toastContainer').append(toastHtml);
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Remove from DOM after hide
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    },

    showMovie(element) {
        const movieId = $(element).data('movie-id');
        showMovieDetails(movieId);
    }
};

// Global Exposure for OnClick handlers
window.App = App;
window.switchTab = (t, e) => App.switchTab(t, e);
// Re-expose legacy functions if needed or update HTML to use App.x
window.loadCurrentProcessing = () => App.loadCurrentProcessing();
window.loadCompletedTasks = () => App.loadCompletedTasks();
window.loadMoviesWithLibraries = () => App.loadMoviesWithLibraries();
window.loadIndexedMedia = () => App.loadIndexedMedia();

// Initialize on Ready
$(document).ready(() => {
    App.init();
});

// Helper for Server Details (moved from HTML)
async function loadServerDetails() {
        // Load server details
        try {
            const response = await fetch('/api/server-details');
            const data = await response.json();

            if (data.error) {
                $('#serverDetailsSection').html(`
                    <div class="alert alert-danger">${data.error}</div>
                `);
                return;
            }

            // Format server details
            $('#serverDetailsSection').html(`
                <div class="row g-3">
                    <div class="col-lg-3 col-md-6">
                        <div class="card h-100 border-0 shadow-sm">
                            <div class="card-body">
                                <h6 class="card-title text-primary mb-3">🖥️ System</h6>
                                <div class="small">
                                    <div class="d-flex justify-content-between mb-1"><span>OS:</span> <strong>${data.operating_system}</strong></div>
                                    <div class="d-flex justify-content-between mb-1"><span>Version:</span> <strong>${data.version}</strong></div>
                                    <div class="d-flex justify-content-between mb-1"><span>Arch:</span> <strong>${data.system_architecture}</strong></div>
                                    <div class="d-flex justify-content-between"><span>Time:</span> <strong id="serverTimeDisplay">${data.server_time}</strong></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6">
                        <div class="card h-100 border-0 shadow-sm">
                            <div class="card-body">
                                <h6 class="card-title text-success mb-3">🌐 Network</h6>
                                <div class="small">
                                    <div class="truncate mb-1" title="${data.local_address}">Local: <strong>${data.local_address}</strong></div>
                                    <div class="truncate mb-1" title="${data.wan_address}">WAN: <strong>${data.wan_address}</strong></div>
                                    <div class="d-flex justify-content-between mb-1"><span>HTTP Port:</span> <strong>${data.http_server_port_number}</strong></div>
                                    <div class="d-flex justify-content-between"><span>HTTPS Port:</span> <strong>${data.https_port_number}</strong></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6">
                        <div class="card h-100 border-0 shadow-sm">
                            <div class="card-body">
                                <h6 class="card-title text-warning mb-3">💾 Storage & Logs</h6>
                                <div class="small">
                                    <div class="mb-1">
                                        <span class="d-block text-muted" style="font-size: 0.75rem;">Transcoding Path:</span>
                                        <div class="text-truncate" title="${data.transcoding_temp_path}">${data.transcoding_temp_path}</div>
                                    </div>
                                    <div>
                                        <span class="d-block text-muted" style="font-size: 0.75rem;">Log Path:</span>
                                        <div class="text-truncate" title="${data.log_path}">${data.log_path}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6">
                        <div class="card h-100 border-0 shadow-sm">
                            <div class="card-body d-flex flex-column justify-content-center align-items-center">
                                 <div class="d-flex flex-wrap gap-2 justify-content-center">
                                     <div class="badge bg-secondary p-2">Auto-Update: ${data.can_self_update ? 'Yes' : 'No'}</div>
                                     <div class="badge bg-secondary p-2">Auto-Restart: ${data.can_self_restart ? 'Yes' : 'No'}</div>
                                     ${data.has_pending_restart ? '<div class="badge bg-warning text-dark p-2">Restart Pending</div>' : '<div class="badge bg-success p-2">Status: OK</div>'}
                                 </div>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        } catch (error) {
            $('#serverDetailsSection').html(`
                <div class="alert alert-danger">Failed to load server details</div>
            `);
        }
    }
    // Attach to App object
    App.loadServerDetails = loadServerDetails;

    // Cast Page Functions
    App.loadCast = async function(startIndex = 0, append = false) {
        const container = $('#castContainer');
        const limit = 50;
        
        if (!append) {
             container.data('startIndex', 0);
             container.data('hasMore', true);
             container.empty();
        }
        
        startIndex = container.data('startIndex') || 0;
        const searchTerm = $('#castSearch').val();
        
        try {
            let url = `/api/cast?limit=${limit}&startIndex=${startIndex}`;
            if (searchTerm) url += `&searchTerm=${encodeURIComponent(searchTerm)}`;
            
            const response = await fetch(url);
            const people = await response.json();
            
            if (people.length < limit) container.data('hasMore', false);
            
            if (people.length === 0 && !append) {
                container.html('<div class="col-12 text-center text-muted">No people found</div>');
                return;
            }
            
            people.forEach(person => {
                 const imagePath = person.primary_image_tag 
                    ? `/api/image/${person.id}?tag=${person.primary_image_tag}` 
                    : null;
                 
                 const imageHtml = imagePath 
                    ? `<img src="${imagePath}" class="card-img-top" alt="${person.name}" loading="lazy" style="height: 250px; object-fit: cover;">`
                    : `<div class="card-img-top d-flex align-items-center justify-content-center bg-secondary text-white" style="height: 250px;"><span class="display-4">👤</span></div>`;

                 const card = `
                    <div class="col-6 col-md-4 col-lg-3 col-xl-2">
                        <div class="card h-100 border-0 shadow-sm theme-card hvr-float person-card" onclick="App.showPersonDetails('${person.id}', '${person.name}')" style="cursor: pointer;">
                            ${imageHtml}
                            <div class="card-body p-2 text-center">
                                <h6 class="card-title mb-0 text-truncate">${person.name}</h6>
                            </div>
                        </div>
                    </div>
                 `;
                 container.append(card);
            });
            
            container.data('startIndex', startIndex + people.length);
            
        } catch (e) {
            console.error(e);
        }
    };
    
    App.setupCastSearch = function() {
        let timeout;
        $('#castSearch').on('input', () => {
             clearTimeout(timeout);
             timeout = setTimeout(() => App.loadCast(), 500);
        });
        
        // Infinite scroll for cast
        $(window).on('scroll', () => {
             if ($(window).scrollTop() + $(window).height() > $(document).height() - 200) {
                 if ($('#castContainer').length && $('#castContainer').data('hasMore')) {
                     App.loadCast(null, true); 
                 }
             }
        });
    };

    App.showPersonDetails = async function(personId, personName) {
        const modal = new bootstrap.Modal(document.getElementById('personDetailsModal'));
        modal.show();
        $('#personDetailsModalLabel').text(personName);
        $('#personDetailsContent').html('<div class="text-center py-5"><div class="spinner-border text-primary"></div></div>');
        
        try {
            // Fetch details and credits in parallel
            const [detailsResponse, creditsResponse] = await Promise.all([
                fetch(`/api/person/${personId}`),
                fetch(`/api/person/${personId}/credits`)
            ]);

            const person = await detailsResponse.json();
            const credits = await creditsResponse.json();
            
            // Build Credits HTML
            let creditsHtml = '';
            if (credits.length === 0) {
                creditsHtml = '<p class="text-muted">No credits found.</p>';
            } else {
                 creditsHtml = `
                    <h5 class="mb-3 mt-4">Appears In (${credits.length})</h5>
                    <div class="horizontal-scroll-container">
                         ${credits.map(item => {
                             const img = item.primary_image_tag 
                                ? `/api/image/${item.id}?tag=${item.primary_image_tag}` 
                                : null;
                             const imgHtml = img 
                                ? `<img src="${img}" class="rounded mb-2" style="width: 100%; height: 200px; object-fit: cover;">`
                                : `<div class="bg-secondary rounded mb-2 d-flex align-items-center justify-content-center text-white" style="width:100%; height:200px;">🎬</div>`;
                             
                             return `
                                <div class="media-card-item" onclick="showMovieDetails('${item.id}')" style="cursor: pointer; width: 140px;">
                                    ${imgHtml}
                                    <div class="small text-truncate fw-bold">${item.name}</div>
                                    <div class="small text-muted">${item.year || ''}</div>
                                </div>
                             `;
                         }).join('')}
                    </div>
                 `;
            }
            
            // Build Info HTML
            let infoHtml = '';
            if (person.birth_date && person.birth_date !== 'N/A') {
                infoHtml += `<div class="mb-2"><strong>Born:</strong> ${person.birth_date.split(' ')[0]}</div>`;
            }
            if (person.birth_place && person.birth_place !== 'Unknown') {
                infoHtml += `<div class="mb-2"><strong>Place of Birth:</strong> ${person.birth_place}</div>`;
            }
            
            const bioHtml = person.overview 
                ? `<div class="mt-3"><h6 class="fw-bold">Biography</h6><p class="text-muted small">${person.overview}</p></div>` 
                : '';

            $('#personDetailsContent').html(`
                 <div class="row">
                    <div class="col-md-3 text-center mb-3">
                        <img src="/api/image/${personId}" class="img-fluid rounded shadow" onerror="this.style.display='none'">
                    </div>
                    <div class="col-md-9">
                        <h4 class="mb-3">${person.name}</h4>
                        ${infoHtml}
                        ${bioHtml}
                        ${creditsHtml}
                    </div>
                 </div>
            `);
            
        } catch (e) {
            console.error(e);
            $('#personDetailsContent').html('<div class="alert alert-danger">Failed to load details</div>');
        }
    };

// Helper for Movie Details
async function showMovieDetails(itemId) {
    const modal = new bootstrap.Modal(document.getElementById('movieDetailsModal'));
    modal.show();
    $('#movieDetailsContent').html('<div class="text-center py-5"><div class="spinner-border text-primary"></div></div>');
    
    try {
        const response = await fetch(`/api/item/${itemId}`);
        const movie = await response.json();
        
        if (movie.error) {
            $('#movieDetailsContent').html(`<div class="alert alert-danger">${movie.error}</div>`);
            return;
        }
        
        $('#movieDetailsModalLabel').text(movie.name);
        
        // Simple Cast HTML builder
        let castHtml = '';
        if (movie.people && movie.people.length > 0) {
             const actors = movie.people.filter(p => p.Type === 'Actor').slice(0, 10);
             if (actors.length) {
                 castHtml = `<h6 class="mt-4 mb-3">Cast</h6>
                             <div class="cast-carousel">
                                ${actors.map(actor => `
                                    <div class="cast-member">
                                        <img src="/api/person-image/${actor.Id}" 
                                             onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22><text y=%2250%%22 x=%2250%%22 text-anchor=%22middle%22 dy=%22.3em%22 font-size=%2240%22>👤</text></svg>'">
                                        <div class="cast-name">${actor.Name}</div>
                                        <div class="cast-role text-truncate" style="max-width: 100px;">${actor.Role || 'Actor'}</div>
                                    </div>
                                `).join('')}
                             </div>`;
             }
        }
        
        $('#movieDetailsContent').html(`
            <div class="row">
                <div class="col-md-4 mb-3">
                    <img src="/api/image/${movie.id}" class="img-fluid rounded shadow" alt="${movie.name}">
                </div>
                <div class="col-md-8">
                    <h4>${movie.name} <small class="text-muted">(${movie.year})</small></h4>
                    <div class="mb-3">
                        ${movie.genres.map(g => `<span class="badge bg-secondary me-1">${g}</span>`).join('')}
                        ${movie.official_rating ? `<span class="badge bg-info">${movie.official_rating}</span>` : ''}
                    </div>
                    <p><strong>Length:</strong> ${movie.runtime_minutes} mins</p>
                    <p>${movie.overview || 'No overview available.'}</p>
                    ${castHtml}
                </div>
            </div>
        `);
        
        // Connect Emby Link
        const embyUrl = window.EMBY_SERVER_URL || (window.location.protocol + '//' + window.location.hostname + ':8096');
        const serverId = window.EMBY_SERVER_ID || movie.id; // Fallback only if cache failed, but movie.id is technially wrong
        $('#embyLinkBtn').show().off('click').on('click', () => {
             window.open(`${embyUrl}/web/index.html#!/item?id=${movie.id}&serverId=${serverId}`, '_blank');
        });
        
    } catch (e) {
        $('#movieDetailsContent').html('<div class="alert alert-danger">Error details</div>');
    }
}
window.showMovieDetails = showMovieDetails;
