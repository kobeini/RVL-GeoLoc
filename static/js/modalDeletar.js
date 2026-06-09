document.addEventListener('DOMContentLoaded', function() {
  const modalDeletar = document.getElementById('modal-deletar');
  const linkDeletar = document.getElementById('link-deletar');
  const btnCancelar = document.getElementById('btn-cancelar-deletar');
  const formDeletar = document.getElementById('form-deletar');
  const erroSenha = document.getElementById('erro-deletar');

  linkDeletar.addEventListener('click', function(e) {
    e.preventDefault();
    modalDeletar.classList.add('active');
    erroSenha.style.display = 'none'; 
  });

  function fecharModal() {
    modalDeletar.classList.remove('active');
    formDeletar.reset();
  }

  btnCancelar.addEventListener('click', fecharModal);
  modalDeletar.addEventListener('click', function(e) {
    if (e.target === modalDeletar) fecharModal();
  });

  formDeletar.addEventListener('submit', function(e) {
    const senha = formDeletar.querySelector('[name="senha_atual"]').value.trim();
    if (!senha) {
      e.preventDefault();
      erroSenha.style.display = 'block';
    }
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modalDeletar.classList.contains('active')) {
      fecharModal();
    }
  });
});