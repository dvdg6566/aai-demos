const button = document.getElementById("changeColorButton");
const body = document.body;

let currentColor = "white";

button.addEventListener("click", () => {
  currentColor = currentColor === "white" ? "lightgreen" : "white";
  body.style.backgroundColor = currentColor;
});
