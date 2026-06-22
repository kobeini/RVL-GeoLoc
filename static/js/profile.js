document.addEventListener("DOMContentLoaded", () => {
  const showFieldError = (id, show) => {
    const el = document.getElementById(id);
    if (el) el.style.display = show ? "block" : "none";
  };

  //Editar Conta
  const editModal = new Modal("modal-editar", {
    onOpen: () => showFieldError("erro-senha", false),
  });
  document.getElementById("link-editar").addEventListener("click", (event) => {
    event.preventDefault();
    editModal.open();
  });
  document.getElementById("btn-cancelar-edicao").addEventListener("click", () => editModal.close());

  const editForm = document.getElementById("form-editar");
  editForm.addEventListener("submit", (event) => {
    const senha = editForm.querySelector('[name="senha"]').value;
    const confirmar = editForm.querySelector('[name="confirmar_senha"]').value;
    const passwordsDiffer = (senha || confirmar) && senha !== confirmar;

    showFieldError("erro-senha", passwordsDiffer);
    if (passwordsDiffer) event.preventDefault();
  });

  //Deletar Conta
  const deleteForm = document.getElementById("form-deletar");
  const deleteModal = new Modal("modal-deletar", {
    onOpen: () => showFieldError("erro-deletar", false),
    onClose: () => deleteForm.reset(),
  });
  document.getElementById("link-deletar").addEventListener("click", (event) => {
    event.preventDefault();
    deleteModal.open();
  });
  document.getElementById("btn-cancelar-deletar").addEventListener("click", () => deleteModal.close());

  deleteForm.addEventListener("submit", (event) => {
    const senha = deleteForm.querySelector('[name="senha_atual"]').value.trim();
    showFieldError("erro-deletar", !senha);
    if (!senha) event.preventDefault();
  });

  //Logout
  const confirmModal = new Modal("modal-confirmacao");
  const confirmMessage = document.getElementById("modal-mensagem");
  const confirmYesBtn = document.getElementById("btn-sim");
  const logoutLink = document.getElementById("link-sair");

  logoutLink.addEventListener("click", (event) => {
    event.preventDefault();
    confirmMessage.textContent = "Deseja sair da conta?";
    confirmYesBtn.onclick = () => {
      window.location.href = logoutLink.dataset.logoutUrl;
    };
    confirmModal.open();
  });
  document.getElementById("btn-nao").addEventListener("click", () => confirmModal.close());
});
