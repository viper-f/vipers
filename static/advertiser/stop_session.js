document.addEventListener('click', function (event) {
	if (!event.target.matches('#stop')) return;
	let session_id = document.getElementById('session_id').value
      fetch("/advertiser/stop_session/"+session_id)
}, false);