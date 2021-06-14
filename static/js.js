function create_put_link(shaketag) {
	local_shaketag = append_shaketag(shaketag)

	element = document.createElement('span');
	element.textContent = local_shaketag;
	element.classList.add('add-link');

	element.addEventListener('click', () => {
		let tag = document.getElementById('swap-tag');
		tag.value = local_shaketag;
		tag.classList.remove('underline-red');
		tag.classList.add('underline-green');

		document.getElementById('swap-input-subtext').innerHTML = '&nbsp';

		toggle_form_buttons(true)
	})

	return element;
}

function append_shaketag(shaketag) {
	result = shaketag;
	if (shaketag[0] !== '@') result = '@' + shaketag;

	return result;
}

function get_human_time(timestamp) {
	let string = '';

	let remaining_time = timestamp;
	let counter = 0

	// determine days since
	let days_seconds = (24 * 60 * 60);
	counter = remaining_time / days_seconds;
	remaining_time = remaining_time % days_seconds;
	if (counter > 0) {
		string += `${counter} days${counter === 0 ? '' : 's'} `
	}

	// determine hours since
	let hours_seconds = (60 * 60);
	counter = remaining_time / hours_seconds;
	remaining_time = remaining_time % hours_seconds;
	if (counter > 0) {
		string += `${counter} hour${counter === 0 ? '' : 's'} `
	}

	// determine minutes since
	let minutes_seconds = 60;
	counter = remaining_time / minutes_seconds;
	remaining_time = remaining_time % minutes_seconds;
	if (counter > 0) {
		string += `${counter} min${counter === 0 ? '' : 's'} `
	}

	// determine seconds
	counter = remaining_time / minutes_seconds;
	if (remaining_time > 0) {
		string += `${counter} sec${counter === 0 ? '' : 's'} `
	}

	return string.trim();
}
