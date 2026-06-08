document.addEventListener('DOMContentLoaded', function() {
  const modal = document.getElementById('modal-confirmacao');
  const modalMensagem = document.getElementById('modal-mensagem');
  const btnSim = document.getElementById('btn-sim');
  const btnNao = document.getElementById('btn-nao');
  
  const linkSair = document.getElementById('link-sair');
  const linkDeletar = document.getElementById('link-deletar');

  function abrirModal(mensagem, acaoSim) {
    modalMensagem.innerHTML = mensagem;
    btnSim.onclick = acaoSim;
    modal.classList.add('active');
  }

  function fecharModal() {
    modal.classList.remove('active');
  }

  linkSair.addEventListener('click', function(e) {
    e.preventDefault();
    abrirModal(
      'Deseja sair da conta?',
      function() {
        window.location.href = "/logout";
      }
    );
  });

  linkDeletar.addEventListener('click', function(e) {
    e.preventDefault();
    abrirModal(
      'Tem certeza que deseja deletar sua conta?<br><small style="color:#dc2626;">Esta ação é irreversível.</small>',
      function() {
        window.location.href = "/deletar";
      }
    );
  });

  btnNao.addEventListener('click', fecharModal);

  modal.addEventListener('click', function(e) {
    if (e.target === modal) fecharModal();
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      fecharModal();
    }
  });
});