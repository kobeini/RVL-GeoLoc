const questions = document.querySelectorAll(".items");
questions.forEach((question) => {
  question.addEventListener("click", () => {
    if (question.classList.contains("open")) {
      question.nextElementSibling.style.maxHeight = 0;
    } else {
      question.nextElementSibling.style.maxHeight =
        question.nextElementSibling.scrollHeight + "px";
    }
    question.classList.toggle("open");
  });
});
