document.addEventListener('DOMContentLoaded', () => {
    const caseSearchForm = document.getElementById('caseSearchForm');
    const messageDiv = document.getElementById('message');
    const resultsSection = document.getElementById('results-section');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const partiesNameSpan = document.getElementById('partiesName');
    const filingDateSpan = document.getElementById('filingDate');
    const nextHearingDateSpan = document.getElementById('nextHearingDate');
    const ordersListDiv = document.getElementById('ordersList');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');

    caseSearchForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        // Clear previous messages and results
        messageDiv.classList.add('hidden');
        messageDiv.textContent = '';
        resultsSection.classList.add('hidden');
        ordersListDiv.innerHTML = '<p>No orders found yet.</p>'; // Reset orders list
        partiesNameSpan.textContent = 'N/A';
        filingDateSpan.textContent = 'N/A';
        nextHearingDateSpan.textContent = 'N/A';


        // Show loading indicator
        loadingIndicator.classList.remove('hidden');

        const formData = new FormData(caseSearchForm);
        const caseType = formData.get('caseType');
        const caseNumber = formData.get('caseNumber');
        const filingYear = formData.get('filingYear');

        submitBtn.classList.add('loading');
        btnLoader.classList.remove('hidden');
        btnText.textContent = "Fetching Case Details...";
        submitBtn.disabled = true;
        // fetch('http://127.0.0.1:5000/search_case') for local testing
        try {
            const response = await fetch('https://court-data-fetcher-mini-dashboard-3ym9.onrender.com/search_case', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ caseType, caseNumber, filingYear })
            });

            // Hide loading indicator regardless of success or failure
            loadingIndicator.classList.add('hidden');

            const data = await response.json();

            submitBtn.classList.remove('loading');
            btnLoader.classList.add('hidden');
            btnText.textContent = "Fetch Case Details";
            submitBtn.disabled = false;

            if (response.ok) {
                if (data.success) {
                    resultsSection.classList.remove('hidden');
                    partiesNameSpan.textContent = data.parties || 'N/A';
                    filingDateSpan.textContent = data.filingDate || 'N/A';
                    nextHearingDateSpan.textContent = data.nextHearingDate || 'N/A';

                    if (data.orders && data.orders.length > 0) {
                        ordersListDiv.innerHTML = ''; // Clear "No orders" message
                        data.orders.forEach(order => {
                            const orderItem = document.createElement('div');
                            orderItem.classList.add('order-item');
                            orderItem.innerHTML = `
                                <p>${order.date}: <a href="${order.link}" target="_blank" download="${order.filename}">${order.description || 'Download Order'}</a></p>
                            `;
                            ordersListDiv.appendChild(orderItem);
                        });
                    } else {
                        ordersListDiv.innerHTML = '<p>No orders found for this case.</p>';
                    }

                    showMessage('Case details fetched successfully!', 'success');
                } else {
                    showMessage(data.message || 'Error fetching case details.', 'error');
                }
            } else {
                showMessage(data.message || `Server error: ${response.status}`, 'error');
            }

        } catch (error) {
            console.error('Fetch error:', error);
            submitBtn.classList.remove('loading');
            btnLoader.classList.add('hidden');
            btnText.textContent = "Fetch Case Details";
            submitBtn.disabled = false;
            loadingIndicator.classList.add('hidden'); // Hide loading on network error
            showMessage('Network error or server unreachable. Please try again later.', 'error');
        }
    });

    function showMessage(msg, type) {
        messageDiv.textContent = msg;
        messageDiv.classList.remove('hidden', 'success', 'error');
        messageDiv.classList.add(type);
        messageDiv.style.display = 'block'; // Ensure it's displayed
    }
});