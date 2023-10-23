let temp_area = document.getElementById('id_template')

document.addEventListener('click', function (event) {
	if (!event.target.matches('input.temp-radio')) return;
    temp_area.value = event.target.value
}, false);