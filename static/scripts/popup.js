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
			abrir_popup(ptitulo, msg);
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