function create_put_link(shaketag) {
	local_shaketag = append_shaketag(shaketag)

	element = document.createElement('span');
	element.textContent = local_shaketag;
	element.classList.add('add-link');

	element.addEventListener('click', () => {
		let tag = document.getElementById('swap-tag');
		tag.value = local_shaketag;
		tag.classList.remove('border-red');
		tag.dispatchEvent(new Event('input'));

		document.getElementById('swap-input-subtext').innerHTML = '&nbsp';
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
		amount = Math.floor(amount);
		string += amount + ' day' + (amount >= 1 ? 's' : '') + ' '
	}
	remaining_time %= minutes

	// hour+ ago
	minutes = 60 * 60
	amount = remaining_time / minutes
	if (amount > 1) {
		amount = Math.floor(amount);
		string += amount + ' hour' + (amount >= 1 ? 's' : '') + ' '
	}
	remaining_time %= minutes

	// minute+ ago
	minutes = 60
	amount = remaining_time / minutes
	if (amount > 1) {
		amount = Math.floor(amount);
		string += amount + ' minute' + (amount >= 1 ? 's' : '') + ' '
	}

	string = string.trim() + ' ago';

	return string;
}

function set_checkmark(container) {
	let check = document.createElement('i');
	check.classList.add('fas');
	check.classList.add('fa-check');

	container.innerHTML = '';
	container.appendChild(check);
}

function set_loading(container) {
	let loading = document.createElement('div');
	loading.classList.add('loading');
	loading.innerHTML = '<div></div><div></div>';

	container.innerHTML = '';
	container.appendChild(loading);
}

function unset_loading(container) {
	container.classList.remove('loading');
	container.innerHTML = '';
}

function set_x(container) {
	let check = document.createElement('i');
	check.classList.add('fas');
	check.classList.add('fa-times');

	container.innerHTML = '';
	container.appendChild(check);
}