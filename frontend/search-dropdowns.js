// Search Date Dropdown Functions
function toggleSearchDateDropdown() {
    const dropdown = document.getElementById('search-date-dropdown');
    const display = document.getElementById('selected-search-date-display');
    
    if (dropdown.classList.contains('d-none')) {
        dropdown.classList.remove('d-none');
        display.classList.add('active');
        // Close other dropdowns
        closeSearchReminderDropdown();
    } else {
        dropdown.classList.add('d-none');
        display.classList.remove('active');
    }
}

function closeSearchDateDropdown() {
    const dropdown = document.getElementById('search-date-dropdown');
    const display = document.getElementById('selected-search-date-display');
    if (dropdown && display) {
        dropdown.classList.add('d-none');
        display.classList.remove('active');
    }
}

function selectSearchDatePreset(preset) {
    const display = document.getElementById('selected-search-date-display');
    const customDates = document.getElementById('search-custom-dates');
    
    // Update display
    const presetLabels = {
        '': 'Alle Zeiträume',
        'today': 'Heute',
        'yesterday': 'Gestern',
        'last_7_days': 'Letzte 7 Tage',
        'last_30_days': 'Letzte 30 Tage',
        'last_90_days': 'Letzte 90 Tage',
        'this_week': 'Diese Woche',
        'last_week': 'Letzte Woche',
        'this_month': 'Dieser Monat',
        'last_month': 'Letzter Monat',
        'this_quarter': 'Dieses Quartal',
        'last_quarter': 'Letztes Quartal',
        'this_year': 'Dieses Jahr',
        'last_year': 'Letztes Jahr',
        'custom': 'Benutzerdefiniert...'
    };
    
    display.innerHTML = `
        <span>${presetLabels[preset] || 'Alle Zeiträume'}</span>
        <i class="fas fa-chevron-down ms-auto"></i>
    `;
    
    // Handle custom date inputs
    if (preset === 'custom') {
        customDates.classList.remove('d-none');
    } else {
        customDates.classList.add('d-none');
        document.getElementById('search-date-from').value = '';
        document.getElementById('search-date-to').value = '';
    }
    
    // Update the hidden input value for backward compatibility
    const hiddenInput = document.getElementById('search-date-preset');
    if (hiddenInput) {
        hiddenInput.value = preset;
    }
    
    // Close dropdown
    closeSearchDateDropdown();
    
    // Perform search if there's a query
    if (preset !== 'custom') {
        const query = document.getElementById('search-query').value.trim();
        if (query) {
            performSearch();
        }
    }
}

// Search Reminder Dropdown Functions
function toggleSearchReminderDropdown() {
    const dropdown = document.getElementById('search-reminder-dropdown');
    const display = document.getElementById('selected-search-reminder-display');
    
    if (dropdown.classList.contains('d-none')) {
        dropdown.classList.remove('d-none');
        display.classList.add('active');
        // Close other dropdowns
        closeSearchDateDropdown();
    } else {
        dropdown.classList.add('d-none');
        display.classList.remove('active');
    }
}

function closeSearchReminderDropdown() {
    const dropdown = document.getElementById('search-reminder-dropdown');
    const display = document.getElementById('selected-search-reminder-display');
    if (dropdown && display) {
        dropdown.classList.add('d-none');
        display.classList.remove('active');
    }
}

function selectSearchReminderOption(option) {
    const display = document.getElementById('selected-search-reminder-display');
    
    const reminderOptions = {
        'all': 'Alle Dokumente',
        'has': 'Mit Erinnerung',
        'overdue': 'Überfällige Erinnerungen',
        'none': 'Ohne Erinnerung'
    };
    
    display.innerHTML = `
        <span>${reminderOptions[option] || 'Alle Dokumente'}</span>
        <i class="fas fa-chevron-down ms-auto"></i>
    `;
    
    // Update the hidden input value for backward compatibility
    const hiddenInput = document.getElementById('search-reminder-select');
    if (hiddenInput) {
        hiddenInput.value = option;
    }
    
    // Update the global selectedReminder variable
    if (typeof selectedReminder !== 'undefined') {
        selectedReminder = option;
    }
    
    // Close dropdown
    closeSearchReminderDropdown();
    
    // Perform search
    const query = document.getElementById('search-query').value.trim();
    if (query) {
        performSearch();
    }
}