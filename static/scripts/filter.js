function filterMoradores() {
    var input = document.getElementById('searchInput');
    var filter = input.value.toUpperCase();
    var cardsContainer = document.querySelector('.moradores-cards');
    var cards = cardsContainer.getElementsByClassName('morador-card');

    for (var i = 0; i < cards.length; i++) {
        var card = cards[i];
        var name = card.querySelector('.morador-info p').textContent.toUpperCase(); // Aqui está assumindo que o nome é o primeiro <p> dentro de .morador-info
        var cpf = card.querySelectorAll('.morador-info p')[1].textContent.toUpperCase(); // Assumindo que o CPF é o segundo <p>

        // Verifica se o texto inserido no input está no nome ou no CPF
        if (name.indexOf(filter) > -1 || cpf.indexOf(filter) > -1) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    }
}

function filterMedicamentos() {
    var input = document.getElementById('searchInput');
    var filter = input.value.toUpperCase();
    var cardsContainer = document.querySelector('.medicamentos-cards');
    var cards = cardsContainer.getElementsByClassName('tbody-medicamento');

    for (var i = 0; i < cards.length; i++) {
        var card = cards[i];
        var name = card.querySelector('.details .span-medicamento').textContent.toUpperCase(); 
        var concentracao = card.querySelectorAll('.details td')[2].textContent.toUpperCase();  
        var horarios = card.querySelectorAll('.details td')[5].textContent.toUpperCase(); 
        var estoque = card.querySelectorAll('.details td')[7].textContent.toUpperCase(); 

        // Verifica se o texto inserido no input está no nome ou no CPF
        if (name.indexOf(filter) > -1 || 
            concentracao.indexOf(filter) > -1 || 
            horarios.indexOf(filter) > -1 || 
            estoque.indexOf(filter) > -1) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    }
}
