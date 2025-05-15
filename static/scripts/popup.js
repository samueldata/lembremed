function abrir_popup(titulo, conteudo) {
	$("#myModalLabel").html(titulo);
	$("#getCode").html(conteudo);
	$("#getCodeModal").modal('show');
}

function carregar_pagina_popup(purl, pmethod, pdata, ptitulo) {
	$.ajax({
		type: pmethod,
		url: purl,
		data: pdata,
		success: function(msg) {
			abrir_popup(ptitulo.replace('/comprimido/','<br />'), msg);
		}
	});
}

function carregar_pagina_popuploading(purl, pmethod, pdata, ptitulo) {
	abrir_popup(ptitulo, '');
	$.ajax({
		type: pmethod,
		url: purl,
		data: pdata,
		success: function(msg) {
			location.reload();
		}
	});
}

function envia_para_popup(event) {
	// stop the page navigating away
	event.preventDefault();

	// Pega todos os elementos do formulário e serializá-los
	var formDataArray = $(this).serializeArray();

	// Transformar o array de elementos serializados em um objeto JSON
	var formDataObject = {};
	$.each(formDataArray, function(index, element) {
		formDataObject[element.name] = element.value;
	});

	// submit the form via AJAX
	carregar_pagina_popup(form.action, form.method, formDataObject);
}

function envia_e_recarregar(event) {
	// stop the page navigating away
	event.preventDefault();

	// Pega todos os elementos do formulário e serializá-los
	var formData = $(this).serialize();  // <- já lida com checkboxes múltiplos corretamente

	$.ajax({
		type: this.method,
		url: this.action,
		data: formData,  // <- isso envia como hora=7&hora=14&hora=21
		success: function(msg) {
			location.reload();
		}
	});
}

function submitar(url, metodo = 'POST') {
	// Divide a URL base dos parâmetros
	const [action, query] = url.split('?');
	

	// Cria o form
	const form = document.createElement('form');
	form.method = metodo;
	form.action = action;

	//Verifica se tem parametros
	if (query) {
		// Converte os parâmetros da query string em campos hidden
		const params = new URLSearchParams(query);
		for (const [key, value] of params.entries()) {
			const input = document.createElement('input');
			input.type = 'hidden';
			input.name = key;
			input.value = value;
			form.appendChild(input);
		}
	}

	// Adiciona o form ao DOM e envia
	document.body.appendChild(form);
	form.submit();
	}