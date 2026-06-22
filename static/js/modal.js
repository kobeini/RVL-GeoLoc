/**
 * Generic, reusable modal controller.
 *
 * The three previous files (modalEditar.js, modalDeletar.js, modalSair.js)
 * each reimplemented the same open/close/Escape-key/click-outside logic
 * around their own modal. That shared behaviour now lives in one place;
 * each page only wires up what's actually specific to it (see profile.js).
 */
class Modal {
  /**
   * @param {string} overlayId - id of the ".modal-overlay" element.
   * @param {{onOpen?: () => void, onClose?: () => void}} [hooks]
   */
  constructor(overlayId, { onOpen, onClose } = {}) {
    this.overlay = document.getElementById(overlayId);
    this.onOpen = onOpen;
    this.onClose = onClose;

    this.overlay.addEventListener("click", (event) => {
      if (event.target === this.overlay) this.close();
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && this.isOpen()) this.close();
    });
  }

  isOpen() {
    return this.overlay.classList.contains("active");
  }

  open() {
    this.overlay.classList.add("active");
    this.onOpen?.();
  }

  close() {
    this.overlay.classList.remove("active");
    this.onClose?.();
  }
}
