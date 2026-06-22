
document.addEventListener('DOMContentLoaded', function() {
    const paymentForm = document.querySelector('.payment-form');
    const paymentOptions = document.querySelectorAll('.payment-option');
    const methodForms = document.querySelectorAll('.payment-method-form');
    const successOverlay = document.querySelector('.payment-success-overlay');

    // Handle payment option selection
    paymentOptions.forEach(option => {
        option.addEventListener('click', function() {
            const method = this.dataset.method;
            const radio = this.querySelector('input[type="radio"]');

            // Update radio button
            radio.checked = true;

            // Update active states
            paymentOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');

            // Show corresponding form
            methodForms.forEach(form => {
                if (form.id === `${method}-form`) {
                    form.classList.add('active');
                    form.style.display = 'block';
                } else {
                    form.classList.remove('active');
                    form.style.display = 'none';
                }
            });
        });
    });

    // Handle form submission
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Show success animation
            successOverlay.style.display = 'flex';
            successOverlay.style.opacity = '1';

            // Submit form after animation
            setTimeout(() => {
                paymentForm.submit();
            }, 2000);
        });
    }

    // Format card number input
    const cardNumberInput = document.querySelector('input[name="card_number"]');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 16) value = value.slice(0, 16);
            const chunks = value.match(/.{1,4}/g) || [];
            e.target.value = chunks.join(' ');
        });
    }

    // Initialize first payment option
    const firstOption = paymentOptions[0];
    if (firstOption) {
        firstOption.click();
    }
});
