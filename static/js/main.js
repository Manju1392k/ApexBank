/**
 * ApexBank Client Side Helpers & Interactive UX
 */

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });

    // Format currency inputs with formatted visual preview if element exists
    const amountInputs = document.querySelectorAll('input[type="number"][name="amount"]');
    amountInputs.forEach(input => {
        const preview = document.createElement('div');
        preview.className = 'form-help';
        preview.style.color = '#c5a059';
        preview.style.fontWeight = '500';
        input.parentNode.appendChild(preview);

        input.addEventListener('input', () => {
            const val = parseFloat(input.value);
            if (!isNaN(val) && val > 0) {
                preview.textContent = `Amount: ₹ ${val.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            } else {
                preview.textContent = '';
            }
        });
    });

    // Recipient Account Live Verification in Transfer Form
    const recipientInput = document.getElementById('id_recipient');
    if (recipientInput) {
        const feedbackContainer = document.createElement('div');
        feedbackContainer.className = 'form-help';
        feedbackContainer.id = 'recipient-feedback';
        recipientInput.parentNode.appendChild(feedbackContainer);

        let debounceTimer;
        recipientInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            const accountNo = recipientInput.value.trim();

            if (accountNo.length >= 8) {
                feedbackContainer.innerHTML = '<span style="color:#94a3b8;">Verifying account...</span>';
                debounceTimer = setTimeout(() => {
                    fetch(`/transactions/api/verify-account/?account_number=${encodeURIComponent(accountNo)}`)
                        .then(res => res.json())
                        .then(data => {
                            if (data.valid) {
                                if (data.is_self) {
                                    feedbackContainer.innerHTML = '<span style="color:#f87171;">⚠️ Cannot transfer to your own account.</span>';
                                } else {
                                    feedbackContainer.innerHTML = `<span style="color:#34d399;">✓ Verified Holder: <strong>${data.holder_name}</strong></span>`;
                                }
                            } else {
                                feedbackContainer.innerHTML = `<span style="color:#f87171;">✗ ${data.message}</span>`;
                            }
                        })
                        .catch(() => {
                            feedbackContainer.textContent = '';
                        });
                }, 400);
            } else {
                feedbackContainer.textContent = '';
            }
        });
    }
});
