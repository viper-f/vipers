document.addEventListener('click', function (event) {
	if (!event.target.matches('#stop')) return;
	let session_id = document.getElementById('session_id').value
      fetch("/stop_session/"+session_id)
}, false);