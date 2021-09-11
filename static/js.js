function create_put_link(shaketag) {
	local_shaketag = append_shaketag(shaketag)

	element = document.createElement('span');
	element.textContent = local_shaketag;
	element.classList.add('add-link');

	element.addEventListener('click', () => {
		let tag = document.getElementById('check-tag');
		tag.value = local_shaketag;
		tag.classList.remove('border-red');
		tag.dispatchEvent(new Event('input'));

		document.getElementById('check-input-subtext').innerHTML = '&nbsp';
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

function remove_list_user(event) {
	let shaketag = event.value;
	
	set_loading(event);
	event.disabled = true;

	fetch('/list/' + shaketag, {
		method: 'DELETE'
	})
	.then(async (data) => {
		if (await data.ok) {
			event.parentElement.parentElement.parentElement.remove();
		} else {
			console.log('list', `not deleted ${shaketag}`);
		}
	})
}

function remove_blacklist_user(event) {
	let shaketag = event.value;
	
	set_loading(event);

	fetch('/blacklist/' + shaketag, {
		method: 'DELETE'
	})
	.then(async (data) => {
		if (await data.ok) {
			window.location.reload();
		} else {
			console.log('blacklist', `not deleted ${shaketag}`);
		}
	})
}

function list_ignore_warning(button) {
	let shaketag = button.value;
	let parent = button.parentNode.parentNode.parentNode;

	set_loading(button);
	button.disabled = true;

	fetch('/list/warning/' + shaketag, {method: 'PATCH'})
	.then(async (data) => {
		if (await data.ok) {
			parent.classList.toggle('border-red');
			parent.classList.toggle('border-yellow');

			button.classList.toggle('emphasis');
			button.classList.toggle('contained');

			unset_loading(button);
			button.textContent = 'IGNORE WARNING';
			button.disabled = false;
		}
	});
}