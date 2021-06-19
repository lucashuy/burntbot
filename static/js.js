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

function get_human_time(timestamp_difference) {
	let string = ''

	let remaining_time = timestamp_difference;
	let amount;
	let minutes;

	// day+ ago
	minutes = 60 * 60 * 24
	amount = remaining_time / minutes
	if (amount > 1) {
		string += Math.floor(amount) + ' day '
	}
	remaining_time %= minutes

	// hour+ ago
	minutes = 60 * 60
	amount = remaining_time / minutes
	if (amount > 1) {
		string += Math.floor(amount) + ' hour '
	}
	remaining_time %= minutes

	// minute+ ago
	minutes = 60
	amount = remaining_time / minutes
	if (amount > 1) {
		string += Math.floor(amount) + ' minute'
	}

	return string;
}
