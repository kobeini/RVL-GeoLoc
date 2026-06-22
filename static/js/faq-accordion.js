// Accordion behaviour for the FAQ items on the homepage.
document.querySelectorAll(".items").forEach((question) => {
  question.addEventListener("click", () => {
    const answer = question.nextElementSibling;
    const isOpen = question.classList.contains("open");

    answer.style.maxHeight = isOpen ? 0 : `${answer.scrollHeight}px`;
    question.classList.toggle("open");
  });
});
