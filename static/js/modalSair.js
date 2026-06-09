document.addEventListener('DOMContentLoaded', function() {
  const modalSair = document.getElementById('modal-confirmacao');
  const modalMensagem = document.getElementById('modal-mensagem');
  const btnSim = document.getElementById('btn-sim');
  const btnNao = document.getElementById('btn-nao');
  const linkSair = document.getElementById('link-sair');

  function abrirModal(mensagem, acaoSim) {
    modalMensagem.innerHTML = mensagem;
    btnSim.onclick = acaoSim;
    modalSair.classList.add('active');
  }

  function fecharModal() {
    modalSair.classList.remove('active');
  }

  linkSair.addEventListener('click', function(e) {
    e.preventDefault();
    abrirModal(
      'Deseja sair da conta?',
      function() { window.location.href = "/logout"; }
    );
  });

  btnNao.addEventListener('click', fecharModal);
  modalSair.addEventListener('click', function(e) {
    if (e.target === modalSair) fecharModal();
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modalSair.classList.contains('active')) fecharModal();
  });
});