/**
 * Client-side real-time validation for PAN, Aadhar, and phone numbers.
 */

document.addEventListener('DOMContentLoaded', () => {
    const panInput = document.getElementById('id_pan');
    const aadharInput = document.getElementById('id_aadhar');
    const phoneInput = document.getElementById('id_phone');

    if (panInput) {
        panInput.addEventListener('input', (e) => {
            // Force uppercase
            panInput.value = panInput.value.toUpperCase();
            const val = panInput.value;
            const panPattern = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
            
            let helper = document.getElementById('pan-helper');
            if (!helper) {
                helper = document.createElement('div');
                helper.id = 'pan-helper';
                helper.className = 'form-help';
                panInput.parentNode.appendChild(helper);
            }

            if (val.length === 10) {
                if (panPattern.test(val)) {
                    helper.style.color = '#34d399';
                    helper.textContent = '✓ Valid PAN format';
                } else {
                    helper.style.color = '#f87171';
                    helper.textContent = '✗ Invalid PAN structure (e.g. ABCDE1234F)';
                }
            } else if (val.length > 0) {
                helper.style.color = '#94a3b8';
                helper.textContent = `${10 - val.length} characters remaining`;
            } else {
                helper.textContent = '';
            }
        });
    }

    if (aadharInput) {
        aadharInput.addEventListener('input', (e) => {
            // Allow only digits
            aadharInput.value = aadharInput.value.replace(/[^0-9]/g, '');
            const val = aadharInput.value;

            let helper = document.getElementById('aadhar-helper');
            if (!helper) {
                helper = document.createElement('div');
                helper.id = 'aadhar-helper';
                helper.className = 'form-help';
                aadharInput.parentNode.appendChild(helper);
            }

            if (val.length === 12) {
                helper.style.color = '#34d399';
                helper.textContent = '✓ 12-digit Aadhar entered';
            } else if (val.length > 0) {
                helper.style.color = '#94a3b8';
                helper.textContent = `${12 - val.length} digits remaining`;
            } else {
                helper.textContent = '';
            }
        });
    }

    if (phoneInput) {
        phoneInput.addEventListener('input', () => {
            phoneInput.value = phoneInput.value.replace(/[^0-9+]/g, '');
        });
    }
});
