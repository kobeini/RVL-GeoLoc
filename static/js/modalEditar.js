document.addEventListener('DOMContentLoaded', function() {
  const modalEditar = document.getElementById('modal-editar');
  const linkEditar = document.getElementById('link-editar');
  const btnCancelarEdicao = document.getElementById('btn-cancelar-edicao');
  const formEditar = document.getElementById('form-editar');
  const erroSenha = document.getElementById('erro-senha');

  formEditar.addEventListener('submit', function(e) {
    const senha = formEditar.querySelector('[name="senha"]').value;
    const confirmar = formEditar.querySelector('[name="confirmar_senha"]').value;
    if (senha || confirmar) {
      if (senha !== confirmar) {
        e.preventDefault();
        erroSenha.style.display = 'block';
      } else {
        erroSenha.style.display = 'none';
      }
    }
  });

  function abrirModalEditar() {
    modalEditar.classList.add('active');
    erroSenha.style.display = 'none';
  }

  function fecharModalEditar() {
    modalEditar.classList.remove('active');
  }

  linkEditar.addEventListener('click', function(e) {
    e.preventDefault();
    abrirModalEditar();
  });

  btnCancelarEdicao.addEventListener('click', fecharModalEditar);
  modalEditar.addEventListener('click', function(e) {
    if (e.target === modalEditar) fecharModalEditar();
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modalEditar.classList.contains('active')) {
      fecharModalEditar();
    }
  });
});