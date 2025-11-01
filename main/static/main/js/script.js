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

