function showJob(jobId) {
  // remove active class from all cards
  document.querySelectorAll('.job-card').forEach(c => c.classList.remove('active'));

  // add active to clicked card
  event.currentTarget.classList.add('active');

  // fetch job details 
  fetch(`/jobs/partial/${jobId}`)
    .then(response => response.text())
    .then(html => {
      document.getElementById('job-details').innerHTML = html;
    });
}

function toggleSave(jobId, btn) {
  // send request to save/unsave job
  fetch(`/saved/${jobId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'), // required for django post request
    },
  })
    .then(response => response.json()) // turn response into json
    .then(data => {
      const icon = btn.querySelector('i'); // get icon element 
      if (data.is_saved) {
        // if saved fill bookmark
        icon.classList.remove('bi-bookmark');
        icon.classList.add('bi-bookmark-fill', 'text-primary');
      } else {
        icon.classList.remove('bi-bookmark-fill', 'text-primary');
        icon.classList.add('bi-bookmark');
      }
    });
}

// get csrf token
function getCookie(name) {
  let cookieValue = null;
  // check if cookie exist in document
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // if cookie name match, get the value
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// creaet job script
document.addEventListener('DOMContentLoaded', function () {
  const progressBar = document.querySelector('.progress-bar');
  const stepIndicators = document.querySelectorAll('.rounded-circle');
  const stepLabels = document.querySelectorAll('.text-center .small');
  const formSteps = document.querySelectorAll('.form-step');
  const nextButtons = document.querySelectorAll('.next-step');
  const prevButtons = document.querySelectorAll('.prev-step');

  let currentStep = 1;
  const totalSteps = 3;

  // update progress bar and step indicators
  function updateProgress(step) {
    const progressPercentage = (step / totalSteps) * 100;
    progressBar.style.width = `${progressPercentage}%`;

    // update step indicators
    stepIndicators.forEach((indicator, index) => {
      if (index < step) {
        indicator.classList.remove('bg-secondary');
        indicator.classList.add('bg-primary');
      } else {
        indicator.classList.remove('bg-primary');
        indicator.classList.add('bg-secondary');
      }
    });

    // update step labels
    stepLabels.forEach((label, index) => {
      if (index < step) {
        label.classList.add('fw-bold');
      } else {
        label.classList.remove('fw-bold');
      }
    });
  }

  // show current step and hide others
  function showStep(stepNumber) {
    formSteps.forEach((step, index) => {
      if (index === stepNumber - 1) {
        step.classList.remove('d-none');
      } else {
        step.classList.add('d-none');
      }
    });

    currentStep = stepNumber;
    updateProgress(stepNumber);
  }

  // validate current step before proceeding
  function validateStep(stepNumber) {
    const currentStepElement = document.getElementById(`step${stepNumber}`);
    const inputs = currentStepElement.querySelectorAll('input, select, textarea');
    let isValid = true;

    // clear previous error messages
    currentStepElement.querySelectorAll('.text-danger').forEach(error => {
      error.remove();
    });

    // check each input
    inputs.forEach(input => {
      if (input.hasAttribute('required') && !input.value.trim()) {
        isValid = false;
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-danger small mt-1';
        errorDiv.textContent = 'This field is required.';
        input.parentNode.appendChild(errorDiv);
      }

      // custom validation for pay fields
      if (input.name === 'pay_min' || input.name === 'pay_max') {
        const value = parseFloat(input.value);
        if (isNaN(value) || value < 1 || value > 1000000) {
          isValid = false;
          const errorDiv = document.createElement('div');
          errorDiv.className = 'text-danger small mt-1';
          errorDiv.textContent = 'Pay must be between 1 and 1,000,000.';
          input.parentNode.appendChild(errorDiv);
        }
      }
    });

    // validate pay range if both fields are filled
    const payMin = document.querySelector('input[name="pay_min"]');
    const payMax = document.querySelector('input[name="pay_max"]');

    if (payMin && payMax && payMin.value && payMax.value) {
      const minValue = parseFloat(payMin.value);
      const maxValue = parseFloat(payMax.value);

      if (minValue > maxValue) {
        isValid = false;
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-danger small mt-1';
        errorDiv.textContent = 'Maximum pay must be greater than or equal to minimum pay.';
        payMax.parentNode.appendChild(errorDiv);
      }
    }

    return isValid;
  }

  // next button event listeners
  nextButtons.forEach(button => {
    button.addEventListener('click', function () {
      const nextStep = parseInt(this.getAttribute('data-next').replace('step', ''));

      if (validateStep(currentStep)) {
        showStep(nextStep);
      }
    });
  });

  // previous button event listeners
  prevButtons.forEach(button => {
    button.addEventListener('click', function () {
      const prevStep = parseInt(this.getAttribute('data-prev').replace('step', ''));
      showStep(prevStep);
    });
  });

  // initialize form
  showStep(1);
});

// profile
document.addEventListener("DOMContentLoaded", function () {
  const logoInput = document.getElementById("logoInput");
  const logoPreview = document.getElementById("logoPreview");
  const removeLogoBtn = document.getElementById("removeLogo");

  if (logoInput) {
    logoInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          logoPreview.innerHTML = `<img src="${e.target.result}" class="image-thumbnail" width="100" height="100">`;
        };
        reader.readAsDataURL(file);
      }
    });
  }

  if (removeLogoBtn) {
    removeLogoBtn.addEventListener("click", function () {
      logoInput.value = "";
      logoPreview.innerHTML = `
        <div class="logo-placeholder bg-light d-flex align-items-center justify-content-center">
          <i class="fas fa-building fa-3x text-muted"></i>
        </div>`;
    });
  }
});